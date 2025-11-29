# Bill Extraction API

A comprehensive OCR and LLM-based solution for extracting line item details from medical bills and invoices.

## Problem Statement

This solution extracts structured data from medical bills/invoices including:
- Individual line item details (name, amount, rate, quantity)
- Sub-totals (where they exist)
- Final totals
- Ensures no double-counting and no missing items

## Solution Architecture

### Components

1. **Document Processor** (`utils/document_processor.py`)
   - Downloads documents from URLs
   - Handles PDF and image formats
   - Converts PDFs to images using `pdf2image`
   - Performs OCR using Tesseract

2. **Extraction Service** (`services/extraction_service.py`)
   - Uses LLM (OpenAI GPT-4o or Anthropic Claude) for intelligent extraction
   - Detects page types (Bill Detail, Final Bill, Pharmacy)
   - Extracts structured line items with validation
   - Handles various bill formats and structures

3. **Token Tracker** (`utils/token_tracker.py`)
   - Tracks token usage across all LLM calls
   - Provides accurate token counts for billing

4. **API Endpoint** (`main.py`)
   - FastAPI-based REST API
   - Follows the exact schema specified in requirements
   - Handles errors gracefully

### Technology Stack

- **OCR**: Tesseract OCR
- **LLM**: Groq Compound (default, configurable to OpenAI GPT-4o or Anthropic Claude)
- **API Framework**: FastAPI
- **Image Processing**: Pillow, pdf2image
- **Token Counting**: tiktoken

## Setup Instructions

### Prerequisites

1. Python 3.8+
2. Tesseract OCR installed on your system
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "OCR Project"
```

2. Create and activate virtual environment:
```bash
python -m venv portfolio_env
source portfolio_env/bin/activate  # On Windows: portfolio_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
- `GROQ_API_KEY`: Your Groq API key (default provider, already configured)
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)

5. Update Tesseract path in `config.py` if needed:
```python
TESSERACT_CMD = "/usr/local/bin/tesseract"  # Update for your system
```

## Running the API

### Development Mode

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Endpoint

`POST /extract-bill-data`

### Request

```json
{
    "document": "https://example.com/bill.pdf"
}
```

### Response

```json
{
    "is_success": true,
    "token_usage": {
        "total_tokens": 5000,
        "input_tokens": 3000,
        "output_tokens": 2000
    },
    "data": {
        "pagewise_line_items": [
            {
                "page_no": "1",
                "page_type": "Bill Detail",
                "bill_items": [
                    {
                        "item_name": "Consultation Charge",
                        "item_amount": 1000.00,
                        "item_rate": 1000.00,
                        "item_quantity": 1.0
                    }
                ]
            }
        ],
        "total_item_count": 1
    }
}
```

### Testing with cURL

**Health Check:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Extract Bill Data:**
```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https"
  }'
```

**Pretty Print JSON Response:**
```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "YOUR_DOCUMENT_URL_HERE"
  }' | python -m json.tool
```

**Using the test script:**
```bash
chmod +x test_api.sh
./test_api.sh
```

## Features

### 1. Multi-format Support
- PDF documents (multi-page)
- Image formats (PNG, JPG, etc.)

### 2. Intelligent Extraction
- LLM-powered extraction understands various bill formats
- Handles different column structures
- Detects page types automatically

### 3. Accurate Totals
- Extracts individual line items without double-counting
- Calculates totals correctly
- Handles subtotals appropriately

### 4. Robust Error Handling
- Graceful handling of OCR failures
- LLM response validation
- Comprehensive logging

### 5. Token Tracking
- Accurate token usage tracking
- Supports both OpenAI and Anthropic models

## Solution Approach

### Extraction Strategy

1. **OCR Processing**: Convert documents to text using Tesseract OCR
2. **Page Type Detection**: Classify each page as Bill Detail, Final Bill, or Pharmacy
3. **Structured Extraction**: Use LLM to extract line items in structured format
4. **Validation**: Ensure all required fields are present and valid
5. **Aggregation**: Count total items across all pages

### Handling Different Bill Formats

The solution handles various bill formats including:
- Tabular bills with columns (Description, Qty, Rate, Amount)
- Category-based bills (Consultation, Room Charges, etc.)
- Pharmacy bills with medication details
- Bills with subtotals and final totals

### Accuracy Improvements

- Uses high-resolution OCR (300 DPI for PDFs)
- LLM-based extraction understands context and structure
- Validates extracted data before returning
- Handles edge cases (missing quantities, rates, etc.)

## Project Structure

```
OCR Project/
├── main.py                      # FastAPI application
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── utils/
│   ├── document_processor.py    # Document download and OCR
│   ├── token_tracker.py         # Token usage tracking
│   └── logger.py                # Logging setup
├── services/
│   └── extraction_service.py    # LLM-based extraction
└── README.md                    # This file
```

## Logging

Logs are written to `logs/` directory with daily rotation. Check logs for debugging and monitoring.

## Future Improvements

1. Support for more document formats
2. Fine-tuned models for better accuracy
3. Caching for frequently accessed documents
4. Batch processing support
5. Webhook support for async processing

## License

MIT License

## Author

Bill Extraction API - HackRx Datathon Solution


