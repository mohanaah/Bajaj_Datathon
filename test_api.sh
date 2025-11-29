#!/bin/bash

# Test script for Bill Extraction API

# Base URL (change if your API is running on a different host/port)
BASE_URL="http://localhost:8000"

echo "Testing Bill Extraction API..."
echo "================================"
echo ""

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -X GET "${BASE_URL}/health"
echo -e "\n\n"

# Test 2: Extract bill data (using working sample URL from Postman collection)
echo "2. Testing extract-bill-data endpoint..."
curl -X POST "${BASE_URL}/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
  }' | python -m json.tool
echo -e "\n\n"

echo "Test completed!"

