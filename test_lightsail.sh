#!/bin/bash

# Lightsail endpoint
API_URL="https://caseintel-agents-1.d4yxwvs7jcr9e.us-east-1.cs.amazonlightsail.com"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
CASE_ID="00000000-0000-0000-0000-000000000003"

echo "================================================"
echo "Testing CaseIntel Agents on AWS Lightsail"
echo "================================================"
echo ""

# Read document contents
DOC1_TEXT=$(cat test_documents/test_email_1.txt)
DOC2_TEXT=$(cat test_documents/test_memo_2.txt)

# Test 1: Upload first document
echo "📄 Test 1: Analyzing test email..."
RESPONSE1=$(curl -s -X POST "${API_URL}/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d "{
    \"case_id\": \"${CASE_ID}\",
    \"document_text\": $(echo "$DOC1_TEXT" | jq -Rs .)
  }")

echo "Response: $RESPONSE1"
JOB_ID1=$(echo $RESPONSE1 | jq -r '.job_id // empty')
echo "✓ Job ID: $JOB_ID1"
echo ""

# Test 2: Upload second document
echo "📄 Test 2: Analyzing test memo..."
RESPONSE2=$(curl -s -X POST "${API_URL}/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d "{
    \"case_id\": \"${CASE_ID}\",
    \"document_text\": $(echo "$DOC2_TEXT" | jq -Rs .)
  }")

echo "Response: $RESPONSE2"
JOB_ID2=$(echo $RESPONSE2 | jq -r '.job_id // empty')
echo "✓ Job ID: $JOB_ID2"
echo ""

# Wait for processing
echo "⏳ Waiting 30 seconds for agents to process documents..."
sleep 30

# Check status of first document
echo ""
echo "📊 Checking status of first document..."
curl -s "${API_URL}/api/v1/status/${JOB_ID1}" \
  -H "X-API-Key: ${API_KEY}" | jq '.'

echo ""
echo "================================================"
echo "📋 Getting results for first document..."
echo "================================================"
curl -s "${API_URL}/api/v1/results/${JOB_ID1}" \
  -H "X-API-Key: ${API_KEY}" | jq '.'

echo ""
echo "================================================"
echo "📋 Getting results for second document..."
echo "================================================"
curl -s "${API_URL}/api/v1/results/${JOB_ID2}" \
  -H "X-API-Key: ${API_KEY}" | jq '.'

echo ""
echo "================================================"
echo "🔗 Getting case timeline..."
echo "================================================"
curl -s "${API_URL}/api/v1/case/${CASE_ID}/timeline" \
  -H "X-API-Key: ${API_KEY}" | jq '.'

echo ""
echo "✅ Test complete!"
