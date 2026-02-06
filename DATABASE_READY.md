# ✅ Database Integration Complete

## Summary

Your CaseIntel AI Agents database schema is now fully aligned with your backend and ready to use!

## What's Been Done

### 1. Schema Analysis ✅
- Analyzed backend TypeORM entities (NestJS)
- Identified key tables: cases, documents, classifications, users, firms
- Mapped relationships and foreign keys

### 2. Database Models Updated ✅
- Updated `agents/src/models/database.py` to match backend schema
- Changed `case_id` from String to UUID with proper foreign keys
- Changed `document_id` to UUID with proper foreign keys
- Added `document_id` foreign key to `AnalysisJob`
- Renamed `TimelineEvent` to `AgentTimelineEvent` (avoid conflicts)
- Added `AgentExecutionLog` model for monitoring
- Added proper timestamps with timezone support
- Added `updated_at` columns with auto-update

### 3. Migration Created ✅
- Created `migrations/001-create-agents-tables.sql`
- Creates 5 tables:
  - `analysis_jobs` - Pipeline execution tracking
  - `analysis_results` - Complete agent analysis
  - `agent_timeline_events` - Extracted timeline events
  - `witness_mentions` - Witness tracking
  - `agent_execution_logs` - Performance monitoring
- Creates 3 views for common queries
- Creates indexes for performance
- Creates triggers for auto-timestamps
- Includes comprehensive comments

### 4. Migration Script Created ✅
- Created `scripts/run_migration.py`
- Checks for backend tables before running
- Runs migration SQL
- Verifies tables and views
- Provides clear error messages

### 5. Documentation Created ✅
- `migrations/README.md` - Migration guide
- `DATABASE_INTEGRATION.md` - Complete integration docs
- `DATABASE_READY.md` - This summary

## Database Schema

### Backend Tables (Existing)
```
cases
├── id (UUID)
├── title
├── firm_id
└── status

documents
├── id (UUID)
├── case_id → cases.id
├── original_filename
└── status

classifications
├── id (UUID)
├── document_id → documents.id
├── privilege
└── privilege_type
```

### Agent Tables (New)
```
analysis_jobs
├── id (UUID)
├── document_id → documents.id
├── case_id → cases.id
└── status

analysis_results
├── id (UUID)
├── job_id → analysis_jobs.id
├── document_id → documents.id
├── case_id → cases.id
├── document_type
├── metadata (JSONB)
├── privilege_flags (JSONB)
├── is_hot_doc
├── hot_doc_data (JSONB)
├── summary
└── cross_references (JSONB)

agent_timeline_events
├── id (UUID)
├── case_id → cases.id
├── document_id → documents.id
├── event_date
└── event_description

witness_mentions
├── id (UUID)
├── case_id → cases.id
├── document_id → documents.id
└── witness_name

agent_execution_logs
├── id (UUID)
├── job_id → analysis_jobs.id
├── agent_name
├── duration_ms
└── cost_usd
```

## Next Steps

### 1. Run the Migration

```bash
cd agents

# Option 1: Using the Python script (Recommended)
python scripts/run_migration.py

# Option 2: Using psql directly
psql -h localhost -U your_user -d caseintel_db -f migrations/001-create-agents-tables.sql
```

### 2. Verify Setup

```bash
python scripts/verify_setup.py
```

This will check:
- ✅ Environment variables
- ✅ Python dependencies
- ✅ Agent configuration
- ✅ Database connection
- ✅ AWS Bedrock access
- ✅ Embedding model
- ✅ ChromaDB

### 3. Test Database Connection

```python
from models.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM analysis_jobs"))
    print(f"✅ Database connected! Jobs count: {result.fetchone()[0]}")
```

### 4. Start the API

```bash
# Start services
docker-compose up -d

# Start API
uvicorn src.api.main:app --reload
```

### 5. Test Analysis Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "case_id": "your-case-uuid",
    "document_id": "your-document-uuid",
    "document_text": "Test document content",
    "document_metadata": {
      "filename": "test.pdf"
    }
  }'
```

## Integration Points

### Backend → Agents

The backend triggers agent analysis:

```typescript
// After document upload
await fetch('http://agents-api:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.AGENTS_API_KEY
  },
  body: JSON.stringify({
    case_id: document.caseId,
    document_id: document.id,
    document_text: extractedText
  })
});
```

### Agents → Backend

The agents read/write shared database:

```python
# Read document
document = session.query(Document).filter_by(id=document_id).first()

# Create analysis job
job = AnalysisJob(
    document_id=document_id,
    case_id=document.case_id,
    status='processing'
)
session.add(job)
session.commit()

# Store results
result = AnalysisResult(
    job_id=job.id,
    document_id=document_id,
    case_id=document.case_id,
    # ... agent results
)
session.add(result)
session.commit()
```

## Database Views

### v_document_analysis
Complete document analysis combining backend and agent data.

```sql
SELECT * FROM v_document_analysis 
WHERE case_id = 'your-case-id'
ORDER BY uploaded_at DESC;
```

### v_hot_documents
All hot documents with scores and severity.

```sql
SELECT * FROM v_hot_documents 
WHERE case_id = 'your-case-id'
ORDER BY hot_doc_score DESC;
```

### v_privilege_analysis
Privilege analysis combining backend and agent results.

```sql
SELECT * FROM v_privilege_analysis 
WHERE case_id = 'your-case-id';
```

## Monitoring Queries

### Agent Performance

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

### Job Status

```sql
SELECT status, COUNT(*) 
FROM analysis_jobs 
GROUP BY status;
```

### Hot Documents

```sql
SELECT 
    hot_doc_severity,
    COUNT(*) 
FROM analysis_results 
WHERE is_hot_doc = TRUE
GROUP BY hot_doc_severity;
```

## Files Created

### Migration Files
- ✅ `migrations/001-create-agents-tables.sql` - Main migration
- ✅ `migrations/README.md` - Migration guide
- ✅ `scripts/run_migration.py` - Migration runner

### Documentation
- ✅ `DATABASE_INTEGRATION.md` - Complete integration docs
- ✅ `DATABASE_READY.md` - This summary

### Updated Files
- ✅ `src/models/database.py` - Updated models

## Verification Checklist

Before running the migration:

- [ ] Backend database is set up
- [ ] Backend tables exist (cases, documents, classifications)
- [ ] PostgreSQL 12+ with UUID extension
- [ ] Database user has CREATE TABLE permissions
- [ ] DATABASE_URL is set in .env
- [ ] AWS credentials are set in .env

After running the migration:

- [ ] All 5 agent tables created
- [ ] All 3 views created
- [ ] Foreign keys are valid
- [ ] Indexes are created
- [ ] Triggers are working
- [ ] `python scripts/verify_setup.py` passes

## Troubleshooting

### Foreign Key Errors

```sql
-- Check if backend tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('cases', 'documents', 'classifications');
```

### UUID Extension Missing

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Or for PostgreSQL 13+
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Permission Errors

```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

## Support

For issues:
1. Check `migrations/README.md`
2. Check `DATABASE_INTEGRATION.md`
3. Run `python scripts/verify_setup.py`
4. Check PostgreSQL logs
5. Review migration SQL comments

## Summary

✅ **Schema Aligned** - Matches backend TypeORM entities
✅ **Foreign Keys** - Proper relationships to backend tables
✅ **Migration Ready** - SQL script and Python runner
✅ **Documentation** - Complete integration guide
✅ **Verification** - Automated checks
✅ **Views Created** - Common queries optimized
✅ **Monitoring** - Performance tracking tables

**Your database is ready to integrate with the backend!** 🚀

Run the migration and start analyzing documents!
