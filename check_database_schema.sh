#!/bin/bash

# Check Database Schema
# Shows what tables and columns actually exist

echo "============================================"
echo "📊 Database Schema Check"
echo "============================================"
echo ""

echo "🔍 Checking backend tables..."
echo ""

psql -h localhost -p 5433 -U caseintel -d caseintel << 'EOF'
-- List all tables
\echo '📋 All Tables:'
\echo '─────────────'
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

\echo ''
\echo '📄 Documents Table Schema:'
\echo '─────────────────────────'
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'documents'
ORDER BY ordinal_position;

\echo ''
\echo '📁 Cases Table Schema:'
\echo '────────────────────'
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'cases'
ORDER BY ordinal_position;

\echo ''
\echo '👥 Users Table Schema:'
\echo '────────────────────'
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

\echo ''
\echo '🏢 Firms Table Schema:'
\echo '────────────────────'
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'firms'
ORDER BY ordinal_position;

\echo ''
\echo '🤖 Agent Tables:'
\echo '───────────────'
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE '%analysis%' OR table_name LIKE '%agent%' OR table_name LIKE '%witness%'
ORDER BY table_name;

\echo ''
\echo '📊 Sample Data Count:'
\echo '───────────────────'
SELECT 
    'firms' as table_name, COUNT(*) as count FROM firms
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'cases', COUNT(*) FROM cases
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'analysis_jobs', COUNT(*) FROM analysis_jobs
UNION ALL
SELECT 'analysis_results', COUNT(*) FROM analysis_results;
EOF

echo ""
echo "============================================"
echo "✅ Schema check complete!"
echo "============================================"
echo ""
echo "Next: We need to either:"
echo "1. Fix S3 permissions to upload test documents"
echo "2. Modify the API to accept raw text (for local testing)"
echo "3. Use existing documents in the database"
echo ""
