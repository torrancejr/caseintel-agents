#!/bin/bash

# CaseIntel Agents API Test Script
# Tests the local API endpoints

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"

echo "============================================"
echo "CaseIntel Agents API - Local Testing"
echo "============================================"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
echo "GET $API_URL/health"
echo ""
curl -s $API_URL/health | python3 -m json.tool
echo ""
echo ""

# Test 2: API Documentation
echo "2️⃣  API Documentation Available:"
echo "   Swagger UI: $API_URL/docs"
echo "   ReDoc: $API_URL/redoc"
echo ""
echo ""

# Test 3: Test Analysis Endpoint (without actual document)
echo "3️⃣  Testing Analysis Endpoint Structure..."
echo "POST $API_URL/api/v1/analyze"
echo ""
echo "Note: This will fail without a real document URL, but shows the endpoint is accessible"
echo ""
curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "document_url": "test",
    "case_id": "test-case"
  }' | python3 -m json.tool 2>&1 | head -20
echo ""
echo ""

echo "============================================"
echo "✅ API is running on port 8000"
echo ""
echo "Next steps:"
echo "1. Fix database connection (port 5433)"
echo "2. Upload a test document to S3"
echo "3. Run full document analysis test"
echo "============================================"
