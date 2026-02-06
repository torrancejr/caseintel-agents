#!/bin/bash

# Complete End-to-End Test of CaseIntel Agents
# This script will:
# 1. Upload test document to S3
# 2. Create test case and document in database
# 3. Trigger AI analysis
# 4. Show results in multiple ways

set -e  # Exit on error

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
S3_BUCKET="caseintel-documents"
TEST_FILE="test_documents/sample_legal_email.txt"

echo "============================================"
echo "🧪 CaseIntel Agents - End-to-End Test"
echo "============================================"
echo ""

# Step 1: Upload to S3
echo "📤 Step 1: Uploading test document to S3..."
S3_KEY="test/$(date +%Y%m%d_%H%M%S)_sample_legal_email.txt"
aws s3 cp "$TEST_FILE" "s3://$S3_BUCKET/$S3_KEY"
S3_URL="s3://$S3_BUCKET/$S3_KEY"
echo "✅ Uploaded to: $S3_URL"
echo ""

# Step 2: Create test case and document in database
echo "📝 Step 2: Creating test case and document in database..."
psql -h localhost -p 5433 -U caseintel -d caseintel << EOF
-- Create test firm (if not exists)
INSERT INTO firms (id, name, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Test Law Firm',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Create test user (if not exists)
INSERT INTO users (id, email, first_name, last_name, firm_id, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'test@testfirm.com',
  'Test',
  'User',
  '00000000-0000-0000-0000-000000000001',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Create test case
INSERT INTO cases (id, name, case_number, firm_id, created_by_id, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000003',
  'Smith v. Acme Corp.',
  '2023-CV-12345',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Create test document
INSERT INTO documents (id, name, s3_key, case_id, uploaded_by_id, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000004',
  'Sample Legal Email - Settlement Discussion',
  '$S3_KEY',
  '00000000-0000-0000-0000-000000000003',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

SELECT 'Test data created successfully!' as status;
EOF

echo "✅ Test case and document created"
echo ""

# Step 3: Trigger AI analysis
echo "🤖 Step 3: Triggering AI analysis (6 agents)..."
echo ""
RESPONSE=$(curl -s -X POST "$API_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"document_url\": \"$S3_URL\",
    \"case_id\": \"00000000-0000-0000-0000-000000000003\",
    \"document_id\": \"00000000-0000-0000-0000-000000000004\"
  }")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Extract job_id from response
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to start analysis. Check the error above."
    exit 1
fi

echo "✅ Analysis started!"
echo "📋 Job ID: $JOB_ID"
echo ""

# Step 4: Monitor progress
echo "⏳ Step 4: Monitoring progress..."
echo ""

for i in {1..30}; do
    sleep 2
    STATUS_RESPONSE=$(curl -s "$API_URL/api/v1/status/$JOB_ID" \
      -H "X-API-Key: $API_KEY")
    
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "")
    PROGRESS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress_percent', 0))" 2>/dev/null || echo "0")
    CURRENT_AGENT=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_agent', ''))" 2>/dev/null || echo "")
    
    echo "[$i] Status: $STATUS | Progress: $PROGRESS% | Agent: $CURRENT_AGENT"
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Analysis completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ Analysis failed!"
        echo "$STATUS_RESPONSE" | python3 -m json.tool
        exit 1
    fi
done

echo ""
echo "============================================"
echo "📊 Results Available!"
echo "============================================"
echo ""

# Step 5: Show results
echo "🔍 Step 5: Viewing Results..."
echo ""

echo "Option 1: Via API"
echo "─────────────────"
curl -s "$API_URL/api/v1/results/$JOB_ID" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -50
echo ""
echo "(Full results available at: $API_URL/api/v1/results/$JOB_ID)"
echo ""
echo ""

echo "Option 2: Via Database"
echo "─────────────────────"
echo ""
echo "To view in database, run:"
echo ""
echo "  psql -h localhost -p 5433 -U caseintel -d caseintel"
echo "  Password: caseintel_dev"
echo ""
echo "Then run these queries:"
echo ""
echo "  -- View analysis job"
echo "  SELECT * FROM analysis_jobs WHERE id = '$JOB_ID';"
echo ""
echo "  -- View analysis results"
echo "  SELECT "
echo "    document_type,"
echo "    classification_confidence,"
echo "    is_hot_doc,"
echo "    hot_doc_severity,"
echo "    privilege_recommendation,"
echo "    privilege_confidence"
echo "  FROM analysis_results WHERE job_id = '$JOB_ID';"
echo ""
echo "  -- View timeline events"
echo "  SELECT event_date, event_description, significance"
echo "  FROM agent_timeline_events"
echo "  WHERE case_id = '00000000-0000-0000-0000-000000000003'"
echo "  ORDER BY event_date;"
echo ""
echo "  -- View witness mentions"
echo "  SELECT witness_name, role, context"
echo "  FROM witness_mentions"
echo "  WHERE case_id = '00000000-0000-0000-0000-000000000003';"
echo ""
echo ""

echo "Option 3: Quick Summary"
echo "──────────────────────"
psql -h localhost -p 5433 -U caseintel -d caseintel << EOF
SELECT 
    '📄 Document Type' as metric,
    document_type as value
FROM analysis_results WHERE job_id = '$JOB_ID'
UNION ALL
SELECT 
    '🔥 Hot Document?',
    CASE WHEN is_hot_doc THEN 'YES - ' || hot_doc_severity ELSE 'No' END
FROM analysis_results WHERE job_id = '$JOB_ID'
UNION ALL
SELECT 
    '🔒 Privilege Status',
    privilege_recommendation || ' (' || ROUND(privilege_confidence * 100) || '% confidence)'
FROM analysis_results WHERE job_id = '$JOB_ID'
UNION ALL
SELECT 
    '📅 Timeline Events',
    COUNT(*)::text
FROM agent_timeline_events WHERE case_id = '00000000-0000-0000-0000-000000000003'
UNION ALL
SELECT 
    '👥 Witnesses Found',
    COUNT(DISTINCT witness_name)::text
FROM witness_mentions WHERE case_id = '00000000-0000-0000-0000-000000000003';
EOF

echo ""
echo "============================================"
echo "✅ Test Complete!"
echo "============================================"
echo ""
echo "📋 Job ID: $JOB_ID"
echo "📁 S3 Location: $S3_URL"
echo "🔗 API Results: $API_URL/api/v1/results/$JOB_ID"
echo ""
echo "Next steps:"
echo "1. Review the results above"
echo "2. Check the database for detailed analysis"
echo "3. View the API documentation: $API_URL/docs"
echo ""
