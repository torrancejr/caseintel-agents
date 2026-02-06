#!/bin/bash

# Local Test (No S3 Required)
# Tests the agents with text content directly

set -e

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
TEST_FILE="test_documents/sample_legal_email.txt"

echo "============================================"
echo "🧪 CaseIntel Agents - Local Test"
echo "============================================"
echo ""

# Step 1: Create test data in database
echo "📝 Step 1: Creating test case and document in database..."
psql -h localhost -p 5433 -U caseintel -d caseintel << 'EOF'
-- Create or update test firm
INSERT INTO firms (id, name, "createdAt", "updatedAt", plan_code, included_seats, extra_seats, extra_seat_price_cents)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Test Law Firm for Agents',
  NOW(),
  NOW(),
  'free',
  5,
  0,
  0
)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  "updatedAt" = NOW();

-- Create test user (if not exists)
INSERT INTO users (id, email, "passwordHash", role, "firstName", "lastName", firm_id, "createdAt", "updatedAt", "betaAccessGranted", firm_role, is_active, user_type, email_verified, two_factor_enabled, system_role)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'test@testfirm.com',
  '$2b$10$dummyhashfortest',
  'attorney',
  'Test',
  'User',
  '00000000-0000-0000-0000-000000000001',
  NOW(),
  NOW(),
  false,
  'ATTORNEY',
  true,
  'standard',
  true,
  false,
  'USER'
)
ON CONFLICT (id) DO NOTHING;

-- Create test case
INSERT INTO cases (id, title, matter_number, firm_id, created_by, created_at, updated_at, status, is_deleted, portal_enabled)
VALUES (
  '00000000-0000-0000-0000-000000000003',
  'Smith v. Acme Corp.',
  '2023-CV-12345',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  'DISCOVERY',
  false,
  false
)
ON CONFLICT (id) DO NOTHING;

-- Create test document
INSERT INTO documents (id, original_filename, storage_key, mime_type, size_bytes, status, case_id, uploaded_by, uploaded_at, updated_at, download_allowed)
VALUES (
  '00000000-0000-0000-0000-000000000004',
  'Sample Legal Email - Settlement Discussion.txt',
  'local/test_document.txt',
  'text/plain',
  1024,
  'processed',
  '00000000-0000-0000-0000-000000000003',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  true
)
ON CONFLICT (id) DO NOTHING;

SELECT 'Test data created successfully!' as status;
EOF

echo "✅ Test case and document created"
echo ""

# Step 2: Read test document content
echo "📄 Step 2: Reading test document..."
DOCUMENT_TEXT=$(cat "$TEST_FILE")
echo "✅ Document loaded (${#DOCUMENT_TEXT} characters)"
echo ""

# Step 3: Trigger AI analysis with text content
echo "🤖 Step 3: Triggering AI analysis (6 agents)..."
echo ""

# Create JSON payload with escaped text
PAYLOAD=$(cat <<EOF
{
  "document_text": $(echo "$DOCUMENT_TEXT" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()))'),
  "case_id": "00000000-0000-0000-0000-000000000003",
  "document_id": "00000000-0000-0000-0000-000000000004"
}
EOF
)

RESPONSE=$(curl -s -X POST "$API_URL/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "$PAYLOAD")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Extract job_id
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to start analysis. Check the error above."
    exit 1
fi

echo "✅ Analysis started!"
echo "📋 Job ID: $JOB_ID"
echo ""

# Step 4: Monitor progress
echo "⏳ Step 4: Monitoring progress (this may take 30-60 seconds)..."
echo ""

for i in {1..60}; do
    sleep 2
    STATUS_RESPONSE=$(curl -s "$API_URL/api/v1/status/$JOB_ID" \
      -H "X-API-Key: $API_KEY")
    
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "")
    PROGRESS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress_percent', 0))" 2>/dev/null || echo "0")
    CURRENT_AGENT=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_agent', ''))" 2>/dev/null || echo "")
    
    printf "\r[%2d] Status: %-12s | Progress: %3s%% | Agent: %-20s" "$i" "$STATUS" "$PROGRESS" "$CURRENT_AGENT"
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo ""
        echo "✅ Analysis completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo ""
        echo "❌ Analysis failed!"
        echo "$STATUS_RESPONSE" | python3 -m json.tool
        exit 1
    fi
done

echo ""
echo "============================================"
echo "📊 Results Summary"
echo "============================================"
echo ""

# Quick summary from database
psql -h localhost -p 5433 -U caseintel -d caseintel << EOF
\echo '📄 Document Classification'
\echo '─────────────────────────'
SELECT 
    document_type as "Type",
    document_sub_type as "Sub-Type",
    ROUND(classification_confidence * 100) || '%' as "Confidence"
FROM analysis_results WHERE job_id = '$JOB_ID';

\echo ''
\echo '🔒 Privilege Analysis'
\echo '────────────────────'
SELECT 
    privilege_recommendation as "Recommendation",
    ROUND(privilege_confidence * 100) || '%' as "Confidence",
    privilege_flags as "Flags"
FROM analysis_results WHERE job_id = '$JOB_ID';

\echo ''
\echo '🔥 Hot Document Analysis'
\echo '───────────────────────'
SELECT 
    CASE WHEN is_hot_doc THEN '🔥 YES' ELSE 'No' END as "Is Hot Doc",
    hot_doc_severity as "Severity",
    ROUND(hot_doc_score * 100) || '%' as "Score"
FROM analysis_results WHERE job_id = '$JOB_ID';

\echo ''
\echo '📅 Timeline Events'
\echo '─────────────────'
SELECT 
    TO_CHAR(event_date, 'YYYY-MM-DD') as "Date",
    event_type as "Type",
    significance as "Significance",
    LEFT(event_description, 60) || '...' as "Description"
FROM agent_timeline_events
WHERE case_id = '00000000-0000-0000-0000-000000000003'
ORDER BY event_date;

\echo ''
\echo '👥 Witnesses Identified'
\echo '──────────────────────'
SELECT 
    witness_name as "Name",
    role as "Role"
FROM witness_mentions
WHERE case_id = '00000000-0000-0000-0000-000000000003'
ORDER BY witness_name;

\echo ''
\echo '⚡ Agent Performance'
\echo '──────────────────'
SELECT 
    agent_name as "Agent",
    status as "Status",
    duration_ms || 'ms' as "Duration",
    tokens_used as "Tokens",
    '$' || ROUND(cost_usd::numeric, 4) as "Cost"
FROM agent_execution_logs
WHERE job_id = '$JOB_ID'
ORDER BY started_at;
EOF

echo ""
echo "============================================"
echo "✅ Test Complete!"
echo "============================================"
echo ""
echo "📋 Job ID: $JOB_ID"
echo ""
echo "View detailed results:"
echo "  ./view_results.sh $JOB_ID"
echo ""
echo "Or query the database:"
echo "  psql -h localhost -p 5433 -U caseintel -d caseintel"
echo "  SELECT * FROM analysis_results WHERE job_id = '$JOB_ID' \\gx"
echo ""
