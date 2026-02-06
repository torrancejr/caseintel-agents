# CaseIntel AI Agents - Database Migrations

## Overview

These migrations create the database tables for the AI Agents system that integrate with the existing CaseIntel backend.

## Prerequisites

**IMPORTANT:** The backend database must be set up first! These migrations depend on existing backend tables:
- `cases`
- `documents`
- `classifications`
- `users`
- `firms`

## Migration Files

### 001-create-agents-tables.sql
Creates the core tables for the AI agents system:

1. **analysis_jobs** - Tracks AI agent pipeline execution
2. **analysis_results** - Stores complete agent analysis results
3. **agent_timeline_events** - Timeline events extracted by agents
4. **witness_mentions** - Witness mentions across documents
5. **agent_execution_logs** - Detailed agent execution logs

Also creates:
- Indexes for performance
- Views for common queries
- Triggers for automatic timestamp updates

## Running Migrations

### Option 1: Using psql (Recommended)

```bash
# From the agents directory
cd agents

# Connect to your database and run the migration
psql -h localhost -U your_user -d caseintel_db -f migrations/001-create-agents-tables.sql
```

### Option 2: Using the migration script

```bash
# From the agents directory
python scripts/run_migration.py
```

### Option 3: Using Docker

```bash
# If using docker-compose
docker-compose exec postgres psql -U caseintel -d caseintel -f /migrations/001-create-agents-tables.sql
```

## Verification

After running the migration, verify tables were created:

```sql
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN (
    'analysis_jobs',
    'analysis_results',
    'agent_timeline_events',
    'witness_mentions',
    'agent_execution_logs'
)
ORDER BY table_name;
```

Expected output: 5 tables

## Database Schema

### analysis_jobs
Tracks the execution of the AI agent pipeline for each document.

**Key columns:**
- `document_id` - Links to backend `documents` table
- `case_id` - Links to backend `cases` table
- `status` - Job status (queued, processing, completed, failed)
- `current_agent` - Currently executing agent
- `progress_percent` - Progress percentage (0-100)

### analysis_results
Stores the complete analysis results from all 6 AI agents.

**Key columns:**
- `job_id` - Links to `analysis_jobs`
- `document_id` - Links to backend `documents` table
- `case_id` - Links to backend `cases` table
- `document_type` - Classification result
- `metadata` - Extracted metadata (JSONB)
- `privilege_flags` - Privilege detection results (JSONB)
- `is_hot_doc` - Hot document flag
- `hot_doc_data` - Hot document analysis (JSONB)
- `summary` - Content summary
- `cross_references` - Cross-reference data (JSONB)

### agent_timeline_events
Timeline events extracted by AI agents from documents.

**Key columns:**
- `case_id` - Links to backend `cases` table
- `document_id` - Links to backend `documents` table
- `event_date` - Date of the event
- `event_description` - Description of the event
- `significance` - Event significance (critical, important, notable, minor)

### witness_mentions
Tracks witness mentions across all documents for consistency analysis.

**Key columns:**
- `case_id` - Links to backend `cases` table
- `document_id` - Links to backend `documents` table
- `witness_name` - Name of the witness
- `normalized_name` - Normalized name for matching
- `role` - Witness role (plaintiff, defendant, witness, expert, attorney)

### agent_execution_logs
Detailed logs of agent execution for debugging and monitoring.

**Key columns:**
- `job_id` - Links to `analysis_jobs`
- `agent_name` - Name of the agent
- `status` - Execution status (started, completed, failed, skipped)
- `model_id` - Model used for execution
- `tokens_used` - Number of tokens used
- `cost_usd` - Cost in USD
- `duration_ms` - Execution duration in milliseconds

## Views

### v_document_analysis
Complete document analysis combining backend classification and agent results.

```sql
SELECT * FROM v_document_analysis WHERE case_id = 'your-case-id';
```

### v_hot_documents
Summary of all hot documents.

```sql
SELECT * FROM v_hot_documents WHERE case_id = 'your-case-id' ORDER BY hot_doc_score DESC;
```

### v_privilege_analysis
Privilege analysis combining backend and agent results.

```sql
SELECT * FROM v_privilege_analysis WHERE case_id = 'your-case-id';
```

## Integration with Backend

The agents system integrates with the backend through:

1. **Foreign Keys** - Direct references to backend tables
2. **Complementary Data** - Agents add additional analysis to backend `classifications`
3. **Shared Case Context** - All data is case-isolated using `case_id`

### Data Flow

```
Backend Document Upload
    ↓
Backend creates 'documents' record
    ↓
Agents create 'analysis_jobs' record
    ↓
Agents process document (6 agents)
    ↓
Agents create 'analysis_results' record
    ↓
Backend reads agent results
    ↓
Backend updates 'classifications' record
```

## Rollback

If you need to rollback (⚠️ **DESTRUCTIVE** - will delete data):

```sql
-- Drop tables in reverse order (respects foreign keys)
DROP TABLE IF EXISTS agent_execution_logs CASCADE;
DROP TABLE IF EXISTS witness_mentions CASCADE;
DROP TABLE IF EXISTS agent_timeline_events CASCADE;
DROP TABLE IF EXISTS analysis_results CASCADE;
DROP TABLE IF EXISTS analysis_jobs CASCADE;

-- Drop views
DROP VIEW IF EXISTS v_document_analysis;
DROP VIEW IF EXISTS v_hot_documents;
DROP VIEW IF EXISTS v_privilege_analysis;

-- Drop trigger function
DROP FUNCTION IF EXISTS update_updated_at_column();
```

## Performance Considerations

### Indexes
The migration creates indexes for:
- Foreign key columns
- Status columns
- Date columns
- JSONB columns (GIN indexes)

### JSONB Queries
For efficient JSONB queries, use the GIN indexes:

```sql
-- Find documents with specific privilege flag
SELECT * FROM analysis_results 
WHERE privilege_flags @> '["attorney_client"]'::jsonb;

-- Find documents mentioning specific entity
SELECT * FROM analysis_results 
WHERE metadata @> '{"people": [{"name": "John Doe"}]}'::jsonb;
```

## Monitoring

### Check Job Status

```sql
SELECT status, COUNT(*) 
FROM analysis_jobs 
GROUP BY status;
```

### Check Agent Performance

```sql
SELECT 
    agent_name,
    AVG(duration_ms) AS avg_duration_ms,
    AVG(tokens_used) AS avg_tokens,
    SUM(cost_usd) AS total_cost
FROM agent_execution_logs
WHERE status = 'completed'
GROUP BY agent_name
ORDER BY total_cost DESC;
```

### Check Hot Documents

```sql
SELECT 
    hot_doc_severity,
    COUNT(*) 
FROM analysis_results 
WHERE is_hot_doc = TRUE
GROUP BY hot_doc_severity;
```

## Troubleshooting

### Foreign Key Errors

If you get foreign key errors, ensure the backend tables exist:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('cases', 'documents', 'classifications', 'users', 'firms');
```

### Permission Errors

Ensure your database user has the necessary permissions:

```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

### UUID Extension

If you get UUID errors, ensure the extension is enabled:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Or for PostgreSQL 13+
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

## Next Steps

After running the migration:

1. ✅ Verify tables were created
2. ✅ Test with sample data
3. ✅ Run the agents verification script: `python scripts/verify_setup.py`
4. ✅ Start the agents API: `uvicorn src.api.main:app --reload`
5. ✅ Test document analysis endpoint

## Support

For issues or questions:
- Check the main README.md
- Run `python scripts/verify_setup.py`
- Review the migration SQL file for comments
- Check PostgreSQL logs for errors
