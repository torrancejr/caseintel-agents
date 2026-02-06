#!/bin/bash

API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
BASE_URL="http://localhost:8001"
CASE_ID="00000000-0000-0000-0000-000000000003"

echo "=== Testing Document Analysis ==="
echo ""

# Document 1
echo "📄 Analyzing Document 1: Product Defect Email..."
DOC1_TEXT=$(cat test_documents/test_email_1.txt)
RESPONSE1=$(curl -s -X POST "$BASE_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"document_text\": $(echo "$DOC1_TEXT" | jq -Rs .),
    \"case_id\": \"$CASE_ID\"
  }")

JOB_ID1=$(echo "$RESPONSE1" | jq -r '.job_id')
echo "✅ Job ID: $JOB_ID1"
echo ""

# Wait a bit
echo "⏳ Waiting 3 seconds before document 2..."
sleep 3

# Document 2
echo "📄 Analyzing Document 2: CEO Recall Decision Memo..."
DOC2_TEXT=$(cat test_documents/test_memo_2.txt)
RESPONSE2=$(curl -s -X POST "$BASE_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"document_text\": $(echo "$DOC2_TEXT" | jq -Rs .),
    \"case_id\": \"$CASE_ID\"
  }")

JOB_ID2=$(echo "$RESPONSE2" | jq -r '.job_id')
echo "✅ Job ID: $JOB_ID2"
echo ""

# Wait for processing
echo "⏳ Waiting 30 seconds for analysis to complete..."
sleep 30

# Check results
echo ""
echo "=== Document 1 Results ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/results/$JOB_ID1" | jq '.'

echo ""
echo "=== Document 2 Results ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/results/$JOB_ID2" | jq '.'

echo ""
echo "=== Case Timeline (should show events from both documents) ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/case/$CASE_ID/timeline" | jq '.timeline | length' | xargs -I {} echo "Total events: {}"

echo ""
echo "=== Case Witnesses (should show cross-references) ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/case/$CASE_ID/witnesses" | jq '.witnesses[] | {name: .name, appearances: .appearances | length}'

echo ""
echo "✅ Test complete!"
