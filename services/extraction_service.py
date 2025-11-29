"""
LLM-based extraction service for bill data
"""
import json
import re
from typing import List, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from groq import Groq
from utils.logger import logger
from utils.token_tracker import TokenTracker
import config

class ExtractionService:
    """Service for extracting structured data from bill text using LLM"""
    
    def __init__(self, token_tracker: TokenTracker):
        self.token_tracker = token_tracker
        self.openai_client = None
        self.anthropic_client = None
        self.groq_client = None
        
        if config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        if config.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        if config.GROQ_API_KEY:
            self.groq_client = Groq(api_key=config.GROQ_API_KEY)
    
    def _call_openai(self, prompt: str, system_prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Track tokens
            input_tokens = self.token_tracker.count_tokens_openai(
                system_prompt + prompt, config.OPENAI_MODEL
            )
            output_tokens = self.token_tracker.count_tokens_openai(
                response.choices[0].message.content, config.OPENAI_MODEL
            )
            self.token_tracker.add_usage(input_tokens, output_tokens)
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        """Call Anthropic API"""
        try:
            message = f"{system_prompt}\n\n{prompt}"
            response = self.anthropic_client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=4096,
                temperature=0.1,
                messages=[{"role": "user", "content": message}]
            )
            
            content = response.content[0].text
            
            # Track tokens (approximate)
            input_tokens = self.token_tracker.count_tokens_anthropic(message)
            output_tokens = self.token_tracker.count_tokens_anthropic(content)
            self.token_tracker.add_usage(input_tokens, output_tokens)
            
            return content
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def _call_groq(self, prompt: str, system_prompt: str) -> str:
        """Call Groq API"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            completion = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=messages,
                temperature=0.1,
                max_completion_tokens=4096,
                top_p=1,
                stream=False,
                stop=None
            )
            
            content = completion.choices[0].message.content
            
            # Track tokens (approximate using tiktoken)
            input_tokens = self.token_tracker.count_tokens_openai(
                system_prompt + prompt, "gpt-4"
            )
            output_tokens = self.token_tracker.count_tokens_openai(
                content, "gpt-4"
            )
            self.token_tracker.add_usage(input_tokens, output_tokens)
            
            return content
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def _call_llm(self, prompt: str, system_prompt: str) -> str:
        """Call LLM based on configured provider"""
        if config.DEFAULT_LLM_PROVIDER == "groq" and self.groq_client:
            return self._call_groq(prompt, system_prompt)
        elif config.DEFAULT_LLM_PROVIDER == "openai" and self.openai_client:
            return self._call_openai(prompt, system_prompt)
        elif config.DEFAULT_LLM_PROVIDER == "anthropic" and self.anthropic_client:
            return self._call_anthropic(prompt, system_prompt)
        else:
            raise ValueError("No valid LLM provider configured")
    
    def detect_page_type(self, text: str) -> str:
        """Detect page type: Bill Detail, Final Bill, or Pharmacy"""
        system_prompt = """You are a document classification expert. Classify the document type based on the content.
Return ONLY one of these three options: "Bill Detail", "Final Bill", or "Pharmacy".
- "Bill Detail": Detailed itemized bills with line items
- "Final Bill": Summary bills with totals
- "Pharmacy": Pharmacy bills with medication items"""
        
        prompt = f"""Classify this document:\n\n{text[:2000]}"""
        
        try:
            response = self._call_llm(prompt, system_prompt)
            # Extract classification from response
            if "Bill Detail" in response:
                return "Bill Detail"
            elif "Final Bill" in response:
                return "Final Bill"
            elif "Pharmacy" in response:
                return "Pharmacy"
            else:
                return "Bill Detail"  # Default
        except Exception as e:
            logger.error(f"Error detecting page type: {str(e)}")
            return "Bill Detail"  # Default fallback
    
    def extract_line_items(self, text: str, page_no: int) -> List[Dict[str, Any]]:
        """Extract line items from bill text using LLM"""
        system_prompt = """You are an expert at extracting structured data from medical bills and invoices.
Extract ALL line items from the bill text. For each line item, extract:
- item_name: The exact name/description as shown in the bill
- item_amount: The net amount (after discounts) for this line item (float)
- item_rate: The unit rate/price for this item (float)
- item_quantity: The quantity of this item (float)

IMPORTANT RULES:
1. Extract EVERY line item - do not miss any
2. Do NOT include subtotals or totals as line items
3. item_amount should be the total for that line (quantity × rate, after discounts)
4. If quantity is not explicitly mentioned, use 1.0
5. If rate is not explicitly mentioned but amount and quantity are, calculate rate = amount / quantity
6. Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{
  "bill_items": [
    {
      "item_name": "string",
      "item_amount": 0.0,
      "item_rate": 0.0,
      "item_quantity": 1.0
    }
  ]
}"""
        
        prompt = f"""Extract all line items from this bill page. Return ONLY valid JSON in the exact format specified above, no additional text or markdown:\n\n{text}\n\nJSON:"""
        
        try:
            response = self._call_llm(prompt, system_prompt)
            
            # Parse JSON response
            # Handle cases where response might have markdown code blocks
            response = response.strip()
            if response.startswith("```"):
                # Remove markdown code blocks
                response = re.sub(r'^```json\s*', '', response)
                response = re.sub(r'^```\s*', '', response)
                response = re.sub(r'```\s*$', '', response)
            
            data = json.loads(response)
            
            # Validate and clean extracted items
            bill_items = []
            for item in data.get("bill_items", []):
                # Ensure all required fields exist
                if "item_name" in item and item["item_name"].strip():
                    bill_items.append({
                        "item_name": str(item["item_name"]).strip(),
                        "item_amount": float(item.get("item_amount", 0.0)),
                        "item_rate": float(item.get("item_rate", 0.0)),
                        "item_quantity": float(item.get("item_quantity", 1.0))
                    })
            
            logger.info(f"Extracted {len(bill_items)} line items from page {page_no}")
            return bill_items
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}, Response: {response[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error extracting line items: {str(e)}")
            return []
    
    def process_page(self, page_no: int, text: str) -> Dict[str, Any]:
        """Process a single page and extract line items"""
        logger.info(f"Processing page {page_no}")
        
        # Detect page type
        page_type = self.detect_page_type(text)
        logger.info(f"Page {page_no} detected as: {page_type}")
        
        # Extract line items
        bill_items = self.extract_line_items(text, page_no)
        
        return {
            "page_no": str(page_no),
            "page_type": page_type,
            "bill_items": bill_items
        }


