"""
FastAPI application for bill extraction
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn

from utils.document_processor import DocumentProcessor
from services.extraction_service import ExtractionService
from utils.token_tracker import TokenTracker
from utils.logger import logger
import config

app = FastAPI(title="Bill Extraction API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ExtractBillRequest(BaseModel):
    document: str = Field(..., description="URL of the document to process")

class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float

class PageLineItems(BaseModel):
    page_no: str
    page_type: str
    bill_items: List[BillItem]

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int

class ExtractBillData(BaseModel):
    pagewise_line_items: List[PageLineItems]
    total_item_count: int

class ExtractBillResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: ExtractBillData

@app.get("/")
async def root():
    return {"message": "Bill Extraction API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/extract-bill-data", response_model=ExtractBillResponse)
async def extract_bill_data(request: ExtractBillRequest):
    """
    Extract line items from bill documents
    """
    token_tracker = TokenTracker()
    
    try:
        logger.info(f"Received request to process document: {request.document}")
        
        # Initialize processors
        doc_processor = DocumentProcessor()
        extraction_service = ExtractionService(token_tracker)
        
        # Process document - get pages with text
        pages = doc_processor.process_document(request.document)
        logger.info(f"Processed {len(pages)} pages from document")
        
        # Extract line items from each page
        pagewise_line_items = []
        total_item_count = 0
        
        for page_no, text in pages:
            if not text.strip():
                logger.warning(f"Page {page_no} has no text, skipping")
                continue
            
            page_data = extraction_service.process_page(page_no, text)
            pagewise_line_items.append(page_data)
            total_item_count += len(page_data["bill_items"])
        
        # Get token usage
        token_usage = token_tracker.get_usage()
        
        # Build response
        response = ExtractBillResponse(
            is_success=True,
            token_usage=TokenUsage(**token_usage),
            data=ExtractBillData(
                pagewise_line_items=[
                    PageLineItems(**item) for item in pagewise_line_items
                ],
                total_item_count=total_item_count
            )
        )
        
        logger.info(f"Successfully extracted {total_item_count} items across {len(pagewise_line_items)} pages")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )


