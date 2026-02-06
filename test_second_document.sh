#!/bin/bash

# Test Second Document - Internal Safety Memo
# This will show cross-references to the first document

set -e

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
TEST_FILE="test_documents/internal_safety_memo.txt"
CASE_ID="00000000-0000-0000-0000-000000000003"

echo "============================================"
echo "🧪 Testing Second Document - Cross-References"
echo "============================================"
echo ""

# Create second document in database
echo "📝 Creating second document in database..."
DOC_ID=$(psql -h localhost -p 5433 -U caseintel -d caseintel -t -A -q -c "
INSERT INTO documents (id, original_filename, storage_key, mime_type, size_bytes, status, case_id, uploaded_by, uploaded_at, updated_at, download_allowed)
VALUES (
  gen_random_uuid(),
  'Internal Safety Memo - March 3 2023.txt',
  'local/internal_safety_memo.txt',
  'text/plain',
  2048,
  'processed',
  '$CASE_ID',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  true
)
RETURNING id;
" 2>/dev/null | head -n 1)

echo "✅ Document created: $DOC_ID"
echo ""

# Read document content
echo "📄 Reading document..."
DOCUMENT_TEXT=$(cat "$TEST_FILE")
echo "✅ Document loaded (${#DOCUMENT_TEXT} characters)"
echo ""

# Trigger analysis
echo "🤖 Triggering AI analysis..."

RESPONSE=$(python3 analyze_document.py "$TEST_FILE" "$CASE_ID" "$DOC_ID" "$API_KEY")

JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to start analysis"
    echo "$RESPONSE" | python3 -m json.tool
    exit 1
fi

echo "✅ Analysis started: $JOB_ID"
echo ""

# Monitor progress
echo "⏳ Monitoring progress..."
for i in {1..60}; do
    sleep 2
    STATUS_RESPONSE=$(curl -s "$API_URL/api/v1/status/$JOB_ID" -H "X-API-Key: $API_KEY")
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "")
    
    printf "\r[%2d] Status: %-12s" "$i" "$STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Analysis completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ Analysis failed!"
        exit 1
    fi
done

echo ""
echo "============================================"
echo "📊 Cross-Reference Results"
echo "============================================"
echo ""

# Get results and show cross-references
echo "Fetching cross-reference data..."
curl -s -H "X-API-Key: $API_KEY" \
  "$API_URL/api/v1/results/$JOB_ID" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
xref = data.get('cross_references', {})

print('🔗 Related Documents:')
for doc in xref.get('related_documents', []):
    print(f\"  - {doc.get('title')}: {doc.get('explanation')}\")

print('\n📅 Timeline Events:')
for event in xref.get('timeline_events', []):
    print(f\"  - {event.get('date')}: {event.get('event')}\")

print('\n👥 Witnesses:')
for witness in xref.get('witness_mentions', []):
    print(f\"  - {witness.get('name')}: {len(witness.get('appearances', []))} appearances\")
"

echo ""
echo "============================================"
echo "✅ Test Complete!"
echo "============================================"
echo ""
echo "📋 Job ID: $JOB_ID"
echo "📄 Document ID: $DOC_ID"
echo ""
echo "View full results:"
echo "  curl -H \"X-API-Key: $API_KEY\" http://localhost:8000/api/v1/results/$JOB_ID | python3 -m json.tool"
echo ""
echo "View case timeline (both documents):"
echo "  curl -H \"X-API-Key: $API_KEY\" http://localhost:8000/api/v1/case/$CASE_ID/timeline | python3 -m json.tool"
echo ""
echo "View case witnesses (both documents):"
echo "  curl -H \"X-API-Key: $API_KEY\" http://localhost:8000/api/v1/case/$CASE_ID/witnesses | python3 -m json.tool"
echo ""
