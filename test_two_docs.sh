#!/bin/bash

set -e

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"

echo "============================================"
echo "🧪 Testing Two Documents"
echo "============================================"
echo ""

# Test 1: Email about product liability
echo "📧 Test 1: Analyzing Product Liability Email..."
DOC1_TEXT=$(cat test_documents/test_email_1.txt)

# Use a real case ID from the database (Smith v. Johnson)
PAYLOAD1=$(cat <<EOF
{
  "document_text": $(echo "$DOC1_TEXT" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()))'),
  "case_id": "8e9cd5a1-fb40-4a98-8576-5883a3b6e3f5"
}
EOF
)

RESPONSE1=$(curl -s -X POST "$API_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "$PAYLOAD1")

echo "Response:"
echo "$RESPONSE1" | python3 -m json.tool
echo ""

# Test 2: Settlement Agreement
echo "📄 Test 2: Analyzing Settlement Agreement..."
DOC2_TEXT=$(cat test_documents/test_contract_2.txt)

# Use a real case ID from the database (Bill vs. Sam #928)
PAYLOAD2=$(cat <<EOF
{
  "document_text": $(echo "$DOC2_TEXT" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()))'),
  "case_id": "91254f0f-b6c3-4e3f-993b-40571603b44a"
}
EOF
)

RESPONSE2=$(curl -s -X POST "$API_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "$PAYLOAD2")

echo "Response:"
echo "$RESPONSE2" | python3 -m json.tool
echo ""

echo "============================================"
echo "✅ Both documents submitted for analysis!"
echo "============================================"
echo ""
echo "The AI agents are now processing both documents."
echo "This typically takes 30-60 seconds per document."
echo ""
