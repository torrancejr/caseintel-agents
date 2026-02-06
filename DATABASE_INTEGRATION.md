# 🗄️ CaseIntel AI Agents - Database Integration

## Overview

The AI Agents system integrates seamlessly with the existing CaseIntel backend database. This document explains the integration strategy, schema alignment, and migration process.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CaseIntel Backend (NestJS)                  │
│                                                               │
│  Tables: cases, documents, classifications, users, firms     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Foreign Keys
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              CaseIntel AI Agents (Python/FastAPI)            │
│                                                               │
│  Tables: analysis_jobs, analysis_results,                    │
│          agent_timeline_events, witness_mentions,            │
│          agent_execution_logs                                │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema Integration

### Backend Tables (Existing)

These tables are created by the backend and must exist before running agent migrations:

1. **cases** - Case management
   - `id` (UUID) - Primary key
   - `title`, `description`, `status`
   - `firm_id` - Multi-tenancy

2. **documents** - Document storage
   - `id` (UUID) - Primary key
   - `case_id` - Links to cases
   - `original_filename`, `storage_key`
   - `status` - Processing status

3. **classifications** - AI classification results
   - `id` (UUID) - Primary key
   - `document_id` - Links to documents
   - `privilege`, `privilege_type`, `privilege_confidence`
   - `relevance_score`, `issue_tags`

4. **users** - User management
   - `id` (UUID) - Primary key
   - `email`, `firm_id`

5. **firms** - Firm/organization management
   - `id` (UUID) - Primary key
   - `name`, `subscription_tier`

### Agent Tables (New)

These tables are created by the agent migration and extend the backend schema:

1. **analysis_jobs** - Tracks agent pipeline execution
   - `id` (UUID) - Primary key
   - `document_id` → `documents.id` (FK)
   - `case_id` → `cases.id` (FK)
   - `status`, `current_agent`, `progress_percent`

2. **analysis_results** - Complete agent analysis
   - `id` (UUID) - Primary key
   - `job_id` → `analysis_jobs.id` (FK)
   - `document_id` → `documents.id` (FK)
   - `case_id` → `cases.id` (FK)
   - Agent-specific fields (classification, metadata, privilege, etc.)

3. **agent_timeline_events** - Extracted timeline events
   - `id` (UUID) - Primary key
   - `case_id` → `cases.id` (FK)
   - `document_id` → `documents.id` (FK)
   - `event_date`, `event_description`, `significance`

4. **witness_mentions** - Witness tracking
   - `id` (UUID) - Primary key
   - `case_id` → `cases.id` (FK)
   - `document_id` → `documents.id` (FK)
   - `witness_name`, `role`, `context`

5. **agent_execution_logs** - Agent performance logs
   - `id` (UUID) - Primary key
   - `job_id` → `analysis_jobs.id` (FK)
   - `agent_name`, `status`, `duration_ms`, `cost_usd`

## Data Flow

### Document Analysis Workflow

```
1. Backend: User uploads document
   ↓
2. Backend: Creates 'documents' record
   ↓
3. Backend: Triggers agent analysis (webhook/API call)
   ↓
4. Agents: Creates 'analysis_jobs' record
   ↓
5. Agents: Runs 6 AI agents in sequence
   ├─ Classifier
   ├─ Metadata Extractor
   ├─ Privilege Checker
   ├─ Hot Doc Detector
   ├─ Content Analyzer
   └─ Cross-Reference Engine
   ↓
6. Agents: Creates 'analysis_results' record
   ↓
7. Agents: Updates 'analysis_jobs' status
   ↓
8. Backend: Reads agent results
   ↓
9. Backend: Updates 'classifications' record
   ↓
10. Backend: Notifies user (completion)
```

### Data Synchronization

The agents system complements the backend classification system:

| Data Type | Backend Table | Agent Table | Relationship |
|-----------|---------------|-------------|--------------|
| Privilege | `classifications.privilege` | `analysis_results.privilege_flags` | Complementary |
| Classification | `classifications.issue_tags` | `analysis_results.document_type` | Complementary |
| Summary | `classifications.summary` | `analysis_results.summary` | Complementary |
| Metadata | `classifications.entities` | `analysis_results.metadata` | Complementary |
| Timeline | `timeline_events` (if exists) | `agent_timeline_events` | Separate |
| Witnesses | N/A | `witness_mentions` | New |

## Migration Process

### Prerequisites

1. ✅ Backend database is set up
2. ✅ Backend tables exist (cases, documents, classifications, users, firms)
3. ✅ PostgreSQL 12+ with UUID extension
4. ✅ Database user has CREATE TABLE permissions

### Running the Migration

#### Option 1: Using the Python script (Recommended)

```bash
cd agents
python scripts/run_migration.py
```

The script will:
- Check for backend tables
- Run the migration SQL
- Verify tables were created
- Verify views were created

#### Option 2: Using psql directly

```bash
cd agents
psql -h localhost -U your_user -d caseintel_db -f migrations/001-create-agents-tables.sql
```

#### Option 3: Using Docker

```bash
docker-compose exec postgres psql -U caseintel -d caseintel -f /migrations/001-create-agents-tables.sql
```

### Verification

After migration, verify the setup:

```bash
python scripts/verify_setup.py
```

This checks:
- ✅ All agent tables exist
- ✅ Foreign keys are valid
- ✅ Indexes are created
- ✅ Views are accessible

## Database Views

The migration creates 3 views for common queries:

### 1. v_document_analysis
Complete document analysis combining backend and agent data.

```sql
SELECT * FROM v_document_analysis 
WHERE case_id = 'your-case-id'
ORDER BY uploaded_at DESC;
```

**Columns:**
- Document info (id, filename, status)
- Analysis job info (status, progress)
- Backend classification (privilege, relevance_score)
- Agent results (document_type, is_hot_doc, summary)

### 2. v_hot_documents
All hot documents with severity and scores.

```sql
SELECT * FROM v_hot_documents 
WHERE case_id = 'your-case-id'
ORDER BY hot_doc_score DESC;
```

**Columns:**
- Document info
- Hot doc score and severity
- Hot doc data (flags, reasons)
- Summary

### 3. v_privilege_analysis
Privilege analysis combining backend and agent results.

```sql
SELECT * FROM v_privilege_analysis 
WHERE case_id = 'your-case-id'
AND (backend_privilege != 'unclassified' OR agent_privilege_flags IS NOT NULL);
```

**Columns:**
- Document info
- Backend privilege (status, type, confidence)
- Agent privilege (flags, confidence, recommendation)
- Review status

## API Integration

### Backend → Agents

The backend triggers agent analysis via API:

```typescript
// Backend: After document upload
const response = await fetch('http://agents-api:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.AGENTS_API_KEY
  },
  body: JSON.stringify({
    case_id: document.caseId,
    document_id: document.id,
    document_text: extractedText,
    document_metadata: {
      filename: document.originalFilename,
      mime_type: document.mimeType
    }
  })
});
```

### Agents → Backend

The agents system reads from and writes to the shared database:

```python
# Agents: Read document info
document = session.query(Document).filter_by(id=document_id).first()

# Agents: Create analysis job
job = AnalysisJob(
    document_id=document_id,
    case_id=document.case_id,
    status='processing'
)
session.add(job)
session.commit()

# Agents: Store results
result = AnalysisResult(
    job_id=job.id,
    document_id=document_id,
    case_id=document.case_id,
    document_type='email',
    is_hot_doc=True,
    # ... other fields
)
session.add(result)
session.commit()
```

## Performance Considerations

### Indexes

The migration creates indexes for:

1. **Foreign Keys** - All FK columns
2. **Status Columns** - For filtering by status
3. **Date Columns** - For sorting and filtering
4. **JSONB Columns** - GIN indexes for efficient querying

### Query Optimization

For efficient JSONB queries:

```sql
-- Find documents with specific privilege flag
SELECT * FROM analysis_results 
WHERE privilege_flags @> '["attorney_client"]'::jsonb;

-- Find documents mentioning specific person
SELECT * FROM analysis_results 
WHERE metadata @> '{"people": [{"name": "John Doe"}]}'::jsonb;

-- Find hot documents with specific flag
SELECT * FROM analysis_results 
WHERE is_hot_doc = TRUE
AND hot_doc_data @> '{"flags": ["smoking_gun"]}'::jsonb;
```

### Connection Pooling

Both backend and agents use connection pooling:

**Backend (TypeORM):**
```typescript
{
  type: 'postgres',
  host: process.env.DB_HOST,
  port: 5432,
  username: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  poolSize: 10,
  maxQueryExecutionTime: 5000
}
```

**Agents (SQLAlchemy):**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## Multi-Tenancy

Both systems enforce multi-tenancy through `firm_id`:

1. **Backend** - All queries filter by `firm_id`
2. **Agents** - All queries filter by `case_id` (which links to `firm_id`)

```sql
-- Backend: Get firm's documents
SELECT d.* FROM documents d
JOIN cases c ON d.case_id = c.id
WHERE c.firm_id = 'firm-uuid';

-- Agents: Get case's analysis results
SELECT * FROM analysis_results
WHERE case_id = 'case-uuid';
```

## Monitoring

### Agent Performance

```sql
-- Average agent execution time
SELECT 
    agent_name,
    AVG(duration_ms) AS avg_duration_ms,
    AVG(tokens_used) AS avg_tokens,
    SUM(cost_usd) AS total_cost
FROM agent_execution_logs
WHERE status = 'completed'
AND created_at > NOW() - INTERVAL '7 days'
GROUP BY agent_name
ORDER BY total_cost DESC;
```

### Job Status

```sql
-- Current job status distribution
SELECT 
    status,
    COUNT(*) AS count,
    AVG(progress_percent) AS avg_progress
FROM analysis_jobs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY status;
```

### Hot Document Detection

```sql
-- Hot documents by severity
SELECT 
    hot_doc_severity,
    COUNT(*) AS count,
    AVG(hot_doc_score) AS avg_score
FROM analysis_results
WHERE is_hot_doc = TRUE
GROUP BY hot_doc_severity
ORDER BY avg_score DESC;
```

## Troubleshooting

### Foreign Key Errors

If you get foreign key constraint errors:

```sql
-- Check if backend tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('cases', 'documents', 'classifications');
```

### Missing UUID Extension

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Or for PostgreSQL 13+
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Permission Errors

```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

## Rollback

To rollback the migration (⚠️ **DESTRUCTIVE**):

```sql
-- Drop agent tables
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

## Next Steps

After successful migration:

1. ✅ Run verification: `python scripts/verify_setup.py`
2. ✅ Test database connection
3. ✅ Start agents API: `uvicorn src.api.main:app --reload`
4. ✅ Test analysis endpoint
5. ✅ Integrate with backend

## Summary

✅ **Schema Aligned** - Agent tables integrate with backend schema
✅ **Foreign Keys** - Proper relationships maintained
✅ **Views Created** - Common queries optimized
✅ **Indexes Added** - Performance optimized
✅ **Multi-Tenancy** - Firm isolation maintained
✅ **Migration Script** - Automated setup
✅ **Verification** - Comprehensive checks

The agents system is now ready to integrate with your backend! 🚀
