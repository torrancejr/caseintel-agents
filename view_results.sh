#!/bin/bash

# View Analysis Results from Database
# Usage: ./view_results.sh [job_id]

DB_HOST="localhost"
DB_PORT="5433"
DB_USER="caseintel"
DB_NAME="caseintel"

if [ -z "$1" ]; then
    echo "============================================"
    echo "📊 Recent Analysis Jobs"
    echo "============================================"
    echo ""
    
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    id,
    status,
    current_agent,
    progress_percent,
    TO_CHAR(started_at, 'YYYY-MM-DD HH24:MI:SS') as started,
    TO_CHAR(completed_at, 'YYYY-MM-DD HH24:MI:SS') as completed
FROM analysis_jobs
ORDER BY started_at DESC
LIMIT 10;
EOF
    
    echo ""
    echo "To view details of a specific job:"
    echo "  ./view_results.sh <job_id>"
    echo ""
    exit 0
fi

JOB_ID="$1"

echo "============================================"
echo "📊 Analysis Results for Job: $JOB_ID"
echo "============================================"
echo ""

# Job Status
echo "1️⃣  Job Status"
echo "─────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    status,
    current_agent,
    progress_percent || '%' as progress,
    TO_CHAR(started_at, 'YYYY-MM-DD HH24:MI:SS') as started,
    TO_CHAR(completed_at, 'YYYY-MM-DD HH24:MI:SS') as completed,
    EXTRACT(EPOCH FROM (completed_at - started_at)) || 's' as duration
FROM analysis_jobs
WHERE id = '$JOB_ID';
EOF
echo ""

# Classification Results
echo "2️⃣  Document Classification"
echo "──────────────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    document_type,
    document_sub_type,
    ROUND(classification_confidence * 100) || '%' as confidence
FROM analysis_results
WHERE job_id = '$JOB_ID';
EOF
echo ""

# Privilege Analysis
echo "3️⃣  Privilege Analysis"
echo "─────────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    privilege_recommendation,
    ROUND(privilege_confidence * 100) || '%' as confidence,
    privilege_flags,
    LEFT(privilege_reasoning, 200) || '...' as reasoning_preview
FROM analysis_results
WHERE job_id = '$JOB_ID';
EOF
echo ""

# Hot Doc Analysis
echo "4️⃣  Hot Document Analysis"
echo "────────────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    CASE WHEN is_hot_doc THEN '🔥 YES' ELSE 'No' END as is_hot_doc,
    hot_doc_severity,
    ROUND(hot_doc_score * 100) || '%' as score,
    hot_doc_data
FROM analysis_results
WHERE job_id = '$JOB_ID';
EOF
echo ""

# Content Summary
echo "5️⃣  Content Summary"
echo "──────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    LEFT(summary, 300) || '...' as summary,
    key_facts,
    legal_issues
FROM analysis_results
WHERE job_id = '$JOB_ID';
EOF
echo ""

# Timeline Events
echo "6️⃣  Timeline Events Extracted"
echo "────────────────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    TO_CHAR(event_date, 'YYYY-MM-DD') as date,
    event_type,
    significance,
    LEFT(event_description, 100) as description
FROM agent_timeline_events
WHERE document_id = (
    SELECT document_id FROM analysis_jobs WHERE id = '$JOB_ID'
)
ORDER BY event_date;
EOF
echo ""

# Witness Mentions
echo "7️⃣  Witnesses Mentioned"
echo "──────────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    witness_name,
    role,
    mention_type,
    LEFT(context, 100) as context_preview
FROM witness_mentions
WHERE document_id = (
    SELECT document_id FROM analysis_jobs WHERE id = '$JOB_ID'
)
ORDER BY witness_name;
EOF
echo ""

# Agent Execution Logs
echo "8️⃣  Agent Performance"
echo "────────────────────"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
SELECT 
    agent_name,
    status,
    duration_ms || 'ms' as duration,
    model_id,
    tokens_used,
    '$' || ROUND(cost_usd::numeric, 4) as cost
FROM agent_execution_logs
WHERE job_id = '$JOB_ID'
ORDER BY started_at;
EOF
echo ""

echo "============================================"
echo "✅ Results displayed!"
echo "============================================"
echo ""
echo "To view full JSON data:"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo "  SELECT * FROM analysis_results WHERE job_id = '$JOB_ID' \\gx"
echo ""
