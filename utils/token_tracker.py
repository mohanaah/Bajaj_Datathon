"""
Token usage tracking utility for LLM API calls
"""
from typing import Dict
import tiktoken

class TokenTracker:
    """Track token usage across all LLM calls"""
    
    def __init__(self):
        self.total_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
        
    def add_usage(self, input_tokens: int, output_tokens: int):
        """Add token usage from an API call"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens = self.input_tokens + self.output_tokens
    
    def get_usage(self) -> Dict[str, int]:
        """Get current token usage statistics"""
        return {
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens
        }
    
    def reset(self):
        """Reset token counters"""
        self.total_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
    
    @staticmethod
    def count_tokens_openai(text: str, model: str = "gpt-4") -> int:
        """Count tokens for OpenAI models"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except:
            # Fallback: approximate token count (1 token ≈ 4 characters)
            return len(text) // 4
    
    @staticmethod
    def count_tokens_anthropic(text: str) -> int:
        """Count tokens for Anthropic models (approximate)"""
        # Anthropic uses a different tokenizer, approximate with tiktoken
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            return len(text) // 4


