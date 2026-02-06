#!/bin/bash

# Test API Key Authentication

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"

echo "============================================"
echo "🔐 API Key Authentication Test"
echo "============================================"
echo ""

# Test 1: With correct API key
echo "1️⃣  Testing with CORRECT API key..."
echo ""
RESPONSE=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "document_url": "test",
    "case_id": "test"
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>&1 | head -10
echo ""

if echo "$RESPONSE" | grep -q "Invalid API key"; then
    echo "❌ FAILED: API key not accepted"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check agents/.env has: CASEINTEL_API_KEY=$API_KEY"
    echo "2. Restart the agents API"
    echo "3. Check src/api/dependencies.py for API key validation"
else
    echo "✅ PASSED: API key accepted"
fi

echo ""
echo "============================================"
echo ""

# Test 2: With wrong API key
echo "2️⃣  Testing with WRONG API key (should fail)..."
echo ""
RESPONSE=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key-12345" \
  -d '{
    "document_url": "test",
    "case_id": "test"
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>&1
echo ""

if echo "$RESPONSE" | grep -q "Invalid API key"; then
    echo "✅ PASSED: Invalid key correctly rejected"
else
    echo "⚠️  WARNING: Invalid key was not rejected"
fi

echo ""
echo "============================================"
echo ""

# Test 3: Without API key
echo "3️⃣  Testing WITHOUT API key (should fail)..."
echo ""
RESPONSE=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "test",
    "case_id": "test"
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>&1
echo ""

if echo "$RESPONSE" | grep -q "detail"; then
    echo "✅ PASSED: Missing key correctly rejected"
else
    echo "⚠️  WARNING: Missing key was not rejected"
fi

echo ""
echo "============================================"
echo "Summary"
echo "============================================"
echo ""
echo "Your API key is:"
echo "  $API_KEY"
echo ""
echo "Make sure this EXACT key is in:"
echo "  1. agents/.env"
echo "  2. backend/caseintel-backend/.env"
echo ""
echo "To verify:"
echo "  cd agents && grep CASEINTEL_API_KEY .env"
echo "  cd backend/caseintel-backend && grep CASEINTEL_API_KEY .env"
echo ""
