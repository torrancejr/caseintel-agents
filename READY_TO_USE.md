# 🚀 Ready to Use - Quick Start

Your CaseIntel AI Agents project is fully configured and ready to use!

## Quick Setup (3 Steps)

### 1. Update AWS Credentials

Edit `.env` file:

```bash
# Replace these with your actual AWS credentials
AWS_ACCESS_KEY_ID=your-actual-aws-access-key
AWS_SECRET_ACCESS_KEY=your-actual-aws-secret-key
AWS_REGION=us-east-1
```

### 2. Verify Setup

```bash
source venv/bin/activate
python scripts/verify_setup.py
```

### 3. Start Services

```bash
# Start database and vector store
docker-compose up -d

# Run the API
uvicorn src.api.main:app --reload
```

That's it! Your API is now running at http://localhost:8000

## Test Your Setup

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-05T...",
  "version": "1.0.0"
}
```

### API Documentation

Open in browser: http://localhost:8000/docs

### Test Bedrock Connection

```bash
python scripts/test_bedrock.py
```

## What's Configured

✅ **6 AI Agents** - All using AWS Bedrock
- Document Classifier (Claude 3 Haiku)
- Metadata Extractor (Claude 3 Haiku)
- Privilege Checker (Claude 3.5 Sonnet)
- Hot Doc Detector (Claude 3.5 Sonnet)
- Content Analyzer (Claude 3.5 Sonnet)
- Cross-Reference Engine (Claude 3 Haiku)

✅ **RAG System** - Amazon Titan embeddings
- ChromaDB vector store
- 1024-dimensional embeddings
- Case-isolated collections

✅ **Database** - PostgreSQL
- Document storage
- Case management
- Analysis results

✅ **API** - FastAPI
- 7 REST endpoints
- OpenAPI documentation
- Authentication ready

## Development Models (Active)

You're using cost-effective development models:

| Agent | Model | Cost per 10K tokens |
|-------|-------|---------------------|
| Classifier | Claude 3 Haiku | $0.0025 |
| Metadata | Claude 3 Haiku | $0.0025 |
| Privilege | Claude 3.5 Sonnet | $0.03 |
| Hot Doc | Claude 3.5 Sonnet | $0.03 |
| Content | Claude 3.5 Sonnet | $0.03 |
| Cross-Ref | Claude 3 Haiku | $0.0025 |
| Embeddings | Amazon Titan | $0.02 per 1M |

## API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. Analyze Document
```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "case_id": "case-123",
  "document_id": "doc-456",
  "document_text": "Your document text here...",
  "document_metadata": {
    "filename": "contract.pdf",
    "source": "discovery"
  }
}
```

### 3. Get Analysis Status
```bash
GET /api/v1/status/{document_id}
```

### 4. Search Documents
```bash
POST /api/v1/search
Content-Type: application/json

{
  "case_id": "case-123",
  "query": "confidential agreements",
  "top_k": 5
}
```

### 5. Get Hot Documents
```bash
GET /api/v1/hot-docs/{case_id}
```

### 6. Get Privileged Documents
```bash
GET /api/v1/privileged/{case_id}
```

### 7. Get Cross-References
```bash
GET /api/v1/cross-references/{document_id}
```

## Example Workflow

### 1. Upload and Analyze a Document

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "case_id": "case-001",
    "document_id": "doc-001",
    "document_text": "CONFIDENTIAL ATTORNEY-CLIENT COMMUNICATION\n\nThis email discusses legal strategy for the upcoming trial...",
    "document_metadata": {
      "filename": "email_2024_01_15.pdf",
      "source": "email",
      "date": "2024-01-15"
    }
  }'
```

### 2. Check Analysis Status

```bash
curl http://localhost:8000/api/v1/status/doc-001 \
  -H "X-API-Key: dev-api-key-change-in-production"
```

### 3. Search Similar Documents

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "case_id": "case-001",
    "query": "attorney-client privilege",
    "top_k": 5
  }'
```

### 4. Get Hot Documents

```bash
curl http://localhost:8000/api/v1/hot-docs/case-001 \
  -H "X-API-Key: dev-api-key-change-in-production"
```

## Monitoring

### Check Logs

```bash
# API logs
docker-compose logs -f api

# Database logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

### Check AWS Costs

1. Go to AWS Console → Cost Explorer
2. Filter by Service: "Amazon Bedrock"
3. Group by: Model ID

### Set Budget Alerts

```bash
# AWS Console → Budgets → Create Budget
# Set alert for daily Bedrock costs
```

## Troubleshooting

### API Not Starting

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Restart API
uvicorn src.api.main:app --reload
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### AWS Credentials Error

```bash
# Test AWS credentials
aws sts get-caller-identity

# If not working, reconfigure
aws configure
```

### Model Access Error

1. Go to AWS Console → Bedrock → Model Access
2. Enable required models:
   - Claude 3 Haiku
   - Claude 3.5 Sonnet
   - Amazon Titan Embed Text v2
3. Wait 2-3 minutes for activation
4. Test again

## Switching to Production

When ready for production:

1. Update `.env`:
```bash
ENVIRONMENT=production

# Comment out development models
# MODEL_CLASSIFIER=anthropic.claude-3-haiku-20240307-v1:0

# Uncomment production models
MODEL_CLASSIFIER=anthropic.claude-haiku-4-5-20251001-v1:0
MODEL_METADATA=anthropic.claude-haiku-4-5-20251001-v1:0
MODEL_PRIVILEGE=anthropic.claude-sonnet-4-5-20250929-v1:0
MODEL_HOTDOC=anthropic.claude-sonnet-4-5-20250929-v1:0
MODEL_CONTENT=anthropic.claude-sonnet-4-5-20250929-v1:0
MODEL_CROSSREF=anthropic.claude-haiku-4-5-20251001-v1:0
```

2. Restart services:
```bash
docker-compose restart
```

No code changes needed!

## Documentation

- **README.md** - Full project documentation
- **QUICKSTART.md** - Detailed quick start guide
- **SETUP_COMPLETE.md** - Complete setup summary
- **DEVELOPMENT_MODELS.md** - Model configuration guide
- **BEDROCK_SETUP.md** - AWS Bedrock setup
- **CLAUDE_45_UPGRADE.md** - Claude 4.5 information

## Support

Need help?

1. Run verification: `python scripts/verify_setup.py`
2. Check documentation files
3. Review API docs: http://localhost:8000/docs
4. Check AWS Bedrock console
5. Review CloudWatch logs

## Summary

✅ All agents configured with AWS Bedrock
✅ Development models active (Claude 3.5/3)
✅ RAG system using Amazon Titan embeddings
✅ PostgreSQL and ChromaDB ready
✅ FastAPI with 7 endpoints
✅ Docker deployment configured
✅ Production models ready to enable

**You're ready to start analyzing documents!** 🎉

Just update your AWS credentials and run `python scripts/verify_setup.py`.
