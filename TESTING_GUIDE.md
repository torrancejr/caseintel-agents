# 🧪 Testing Guide - CaseIntel Agents

## Quick Start

### Run the Complete Test

This will upload a test document, trigger all 6 agents, and show you the results:

```bash
cd agents
./run_test_analysis.sh
```

**What it does:**
1. ✅ Uploads test document to S3
2. ✅ Creates test case and document in database
3. ✅ Triggers AI analysis (all 6 agents)
4. ✅ Monitors progress in real-time
5. ✅ Shows results in multiple formats

**Expected output:**
- Document type: Email
- Hot document: YES (contains "smoking gun")
- Privilege: Privileged (attorney-client communication)
- Timeline events: 4 events extracted
- Witnesses: 5 people identified

## Test Document

The test document (`test_documents/sample_legal_email.txt`) is a realistic legal email that will trigger all agents:

**What the agents will find:**
- 📄 **Classifier**: Email, legal correspondence
- 📋 **Metadata**: 4 dates, 5 people, case number
- 🔒 **Privilege**: Attorney-client privileged (high confidence)
- 🔥 **Hot Doc**: YES - contains "smoking gun" evidence
- 📝 **Content**: Settlement discussion, safety defect
- 🔗 **Cross-Ref**: Timeline events, witness mentions

## Viewing Results

### Option 1: Via the Test Script (Easiest)

The test script shows a summary automatically:

```bash
./run_test_analysis.sh
```

### Option 2: Via Database (Most Detailed)

```bash
# View recent jobs
./view_results.sh

# View specific job details
./view_results.sh <job_id>
```

### Option 3: Via API

```bash
# Get results as JSON
curl http://localhost:8000/api/v1/results/JOB_ID \
  -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6" \
  | python3 -m json.tool
```

### Option 4: Direct Database Queries

```bash
# Connect to database
psql -h localhost -p 5433 -U caseintel -d caseintel
# Password: caseintel_dev
```

Then run queries:

```sql
-- View all recent jobs
SELECT id, status, progress_percent, started_at 
FROM analysis_jobs 
ORDER BY started_at DESC 
LIMIT 5;

-- View results for a specific job
SELECT 
    document_type,
    is_hot_doc,
    hot_doc_severity,
    privilege_recommendation,
    privilege_confidence
FROM analysis_results 
WHERE job_id = 'YOUR_JOB_ID';

-- View timeline events
SELECT event_date, event_description, significance
FROM agent_timeline_events
WHERE case_id = '00000000-0000-0000-0000-000000000003'
ORDER BY event_date;

-- View witnesses
SELECT witness_name, role, context
FROM witness_mentions
WHERE case_id = '00000000-0000-0000-0000-000000000003';

-- View agent performance
SELECT agent_name, duration_ms, tokens_used, cost_usd
FROM agent_execution_logs
WHERE job_id = 'YOUR_JOB_ID'
ORDER BY started_at;
```

## Understanding the Results

### 1. Document Classification

```json
{
  "document_type": "email",
  "document_sub_type": "legal_correspondence",
  "classification_confidence": 0.95
}
```

**What it means:** The classifier identified this as a legal email with 95% confidence.

### 2. Metadata Extraction

```json
{
  "dates": [
    {"date": "2024-01-15", "context": "Email date"},
    {"date": "2023-03-03", "context": "Internal safety report"},
    {"date": "2023-04-02", "context": "Plaintiff injured"},
    {"date": "2024-01-30", "context": "Response deadline"}
  ],
  "people": [
    {"name": "Sarah Johnson", "role": "Attorney"},
    {"name": "Michael Chen", "role": "Client"},
    {"name": "Dr. Robert Martinez", "role": "Witness"},
    {"name": "Jennifer Williams", "role": "Witness"},
    {"name": "Thomas Anderson", "role": "Witness"}
  ]
}
```

**What it means:** Extracted all key dates and people mentioned in the document.

### 3. Privilege Analysis

```json
{
  "privilege_flags": ["attorney_client", "work_product"],
  "privilege_recommendation": "privileged",
  "privilege_confidence": 0.98,
  "privilege_reasoning": "Document contains explicit attorney-client privilege markings..."
}
```

**What it means:** This document is attorney-client privileged and should not be produced in discovery.

### 4. Hot Document Detection

```json
{
  "is_hot_doc": true,
  "hot_doc_severity": "critical",
  "hot_doc_score": 0.92,
  "hot_doc_data": {
    "flags": ["smoking_gun", "prior_knowledge", "financial_motive"],
    "reasons": [
      "Contains evidence of prior knowledge of safety defect",
      "Shows financial motivation to delay recall",
      "Explicit admission in internal memo"
    ]
  }
}
```

**What it means:** This is a critical "smoking gun" document that could significantly impact the case.

### 5. Content Analysis

```json
{
  "summary": "Attorney-client communication discussing settlement negotiations...",
  "key_facts": [
    "Plaintiff demanding $2.5M settlement",
    "Internal memo shows prior knowledge of safety defect",
    "Product recall delayed for financial reasons",
    "Plaintiff injured on April 2, 2023"
  ],
  "legal_issues": [
    {
      "issue": "Product Liability",
      "description": "Prior knowledge of safety defect",
      "importance": "high"
    }
  ]
}
```

**What it means:** AI-generated summary and key facts from the document.

### 6. Cross-References

```json
{
  "timeline_events": [
    {"date": "2023-03-03", "event": "Internal safety report completed"},
    {"date": "2023-03-15", "event": "Product recall decision delayed"},
    {"date": "2023-04-02", "event": "Plaintiff injured"},
    {"date": "2023-05-10", "event": "Lawsuit filed"}
  ],
  "witnesses": [
    {"name": "Dr. Robert Martinez", "role": "Engineering Director"},
    {"name": "Jennifer Williams", "role": "VP of Operations"},
    {"name": "Thomas Anderson", "role": "CEO"}
  ]
}
```

**What it means:** Extracted timeline and witness information for case building.

## Database Tables Explained

### `analysis_jobs`
Tracks the overall analysis pipeline execution.

**Key columns:**
- `id` - Job ID (use this to query results)
- `status` - queued, processing, completed, failed
- `progress_percent` - 0-100%
- `current_agent` - Which agent is running

### `analysis_results`
Stores the complete analysis from all 6 agents.

**Key columns:**
- `document_type` - Classification result
- `is_hot_doc` - Boolean flag
- `privilege_recommendation` - privileged/not_privileged/needs_review
- `summary` - AI-generated summary
- `key_facts` - JSON array of key facts

### `agent_timeline_events`
Timeline events extracted from documents.

**Key columns:**
- `event_date` - Date of the event
- `event_description` - What happened
- `significance` - critical/important/notable/minor

### `witness_mentions`
Tracks all witness mentions across documents.

**Key columns:**
- `witness_name` - Person's name
- `role` - Their role in the case
- `context` - Where they were mentioned

### `agent_execution_logs`
Performance metrics for each agent.

**Key columns:**
- `agent_name` - Which agent ran
- `duration_ms` - How long it took
- `tokens_used` - AI tokens consumed
- `cost_usd` - Cost in dollars

## Cost Tracking

Each test run costs approximately:

- Agent 1 (Classifier): ~$0.01
- Agent 2 (Metadata): ~$0.01
- Agent 3 (Privilege): ~$0.05
- Agent 4 (Hot Doc): ~$0.05
- Agent 5 (Content): ~$0.08
- Agent 6 (Cross-Ref): ~$0.01
- **Total: ~$0.21 per document**

View costs in database:
```sql
SELECT 
    agent_name,
    SUM(cost_usd) as total_cost,
    AVG(duration_ms) as avg_duration_ms
FROM agent_execution_logs
GROUP BY agent_name;
```

## Troubleshooting

### Test fails to start

```bash
# Check API is running
curl http://localhost:8000/health

# Check database connection
python test_db_connection.py

# Check AWS credentials
aws sts get-caller-identity
```

### Can't see results

```bash
# List recent jobs
./view_results.sh

# Check job status
psql -h localhost -p 5433 -U caseintel -d caseintel \
  -c "SELECT id, status FROM analysis_jobs ORDER BY started_at DESC LIMIT 5;"
```

### Analysis takes too long

Normal processing time:
- Small document (< 1 page): 10-20 seconds
- Medium document (1-5 pages): 30-60 seconds
- Large document (> 5 pages): 1-3 minutes

If it takes longer, check:
```bash
# View agent logs
./view_results.sh JOB_ID
```

## Next Steps

Once the test works:

1. ✅ Try with your own documents
2. ✅ Test with different document types (contracts, depositions, etc.)
3. ✅ Integrate with your NestJS backend
4. ✅ Build frontend UI to display results
5. 🚀 Deploy to AWS

---

**Ready to test?** Run: `./run_test_analysis.sh`
