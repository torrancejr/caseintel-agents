# ⚡ CaseIntel Quick Start Guide

Get your CaseIntel AI Agents system running in 5 minutes!

## Prerequisites

- Python 3.12 (already installed ✅)
- Docker & Docker Compose
- AWS Account with Bedrock access
- Git (for version control)

## Step 1: AWS Setup (2 minutes)

### Enable Bedrock Models

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Model Access**
3. Click **Enable specific models**
4. Enable these models:
   - ✅ Claude 3 Haiku (`anthropic.claude-3-haiku-20240307-v1:0`)
   - ✅ Claude 3.5 Sonnet (`us.anthropic.claude-3-5-sonnet-20241022-v2:0`)
   - ✅ Amazon Titan Embed Text v2 (`amazon.titan-embed-text-v2:0`)
5. Wait 2-3 minutes for activation

### Get AWS Credentials

```bash
# Option 1: Use AWS CLI
aws configure
# Enter your Access Key ID and Secret Access Key

# Option 2: Get from IAM Console
# Go to IAM → Users → Your User → Security Credentials
# Create Access Key if needed
```

## Step 2: Configure Environment (1 minute)

Edit `.env` file and update these values:

```bash
# Replace with your actual AWS credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Keep these as-is for development
DATABASE_URL=postgresql://caseintel:caseintel_dev_password@localhost:5432/caseintel
CASEINTEL_API_KEY=dev-api-key-change-in-production
```

## Step 3: Verify Setup (1 minute)

```bash
# Activate virtual environment
source venv/bin/activate

# Run verification script
python scripts/verify_setup.py
```

Expected output:
```
✅ All required environment variables set
✅ Model configuration complete
✅ All required Python modules installed
✅ All agents imported successfully
✅ Database connection successful
✅ AWS Bedrock access successful
✅ Embedding model working: amazon.titan-embed-text-v2:0
✅ ChromaDB working
```

## Step 4: Start Services (1 minute)

```bash
# Start PostgreSQL and ChromaDB
docker-compose up -d

# Wait 10 seconds for services to start
sleep 10

# Start the API
uvicorn src.api.main:app --reload
```

## Step 5: Test the API (30 seconds)

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

You should see the interactive API documentation!

## Your First Document Analysis

### Analyze a Document

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "case_id": "case-001",
    "document_id": "doc-001",
    "document_text": "CONFIDENTIAL ATTORNEY-CLIENT COMMUNICATION\n\nDear Client,\n\nThis email discusses our legal strategy for the upcoming trial. We believe the opposing party'\''s key witness testimony can be challenged based on inconsistencies in their deposition.\n\nBest regards,\nJohn Smith, Esq.",
    "document_metadata": {
      "filename": "email_2024_01_15.pdf",
      "source": "email",
      "date": "2024-01-15"
    }
  }'
```

### Expected Response

```json
{
  "document_id": "doc-001",
  "status": "completed",
  "results": {
    "classification": {
      "document_type": "email",
      "confidence": 0.95
    },
    "metadata": {
      "date": "2024-01-15",
      "author": "John Smith, Esq.",
      "subject": "Legal Strategy Discussion"
    },
    "privilege": {
      "is_privileged": true,
      "confidence": 0.98,
      "reasoning": "Contains attorney-client communication discussing legal strategy"
    },
    "hot_doc": {
      "is_hot": true,
      "importance_score": 0.85,
      "reasoning": "Discusses key witness testimony and trial strategy"
    },
    "content_analysis": {
      "summary": "Attorney email to client discussing trial strategy...",
      "key_points": [
        "Legal strategy discussion",
        "Witness testimony challenges",
        "Deposition inconsistencies"
      ]
    }
  }
}
```

## Common Commands

### Start Services
```bash
docker-compose up -d
uvicorn src.api.main:app --reload
```

### Stop Services
```bash
# Stop API (Ctrl+C in terminal)
# Stop Docker services
docker-compose down
```

### View Logs
```bash
# API logs (in terminal where uvicorn is running)

# Docker logs
docker-compose logs -f postgres
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Check Service Status
```bash
docker-compose ps
```

## API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/v1/analyze` | POST | Analyze document |
| `/api/v1/status/{doc_id}` | GET | Get analysis status |
| `/api/v1/search` | POST | Semantic search |
| `/api/v1/hot-docs/{case_id}` | GET | Get hot documents |
| `/api/v1/privileged/{case_id}` | GET | Get privileged docs |
| `/api/v1/cross-references/{doc_id}` | GET | Get related docs |

## Troubleshooting

### API Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill the process
kill -9 <PID>

# Try again
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
# Test credentials
aws sts get-caller-identity

# If error, reconfigure
aws configure
```

### Model Access Error

1. Go to AWS Console → Bedrock → Model Access
2. Verify models are enabled (green checkmark)
3. Wait 2-3 minutes if just enabled
4. Test again: `python scripts/test_bedrock.py`

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify imports
python -c "import fastapi, boto3, chromadb, langgraph"
```

## Next Steps

### 1. Process More Documents

Use the `/api/v1/analyze` endpoint to process your documents.

### 2. Search Documents

Use semantic search to find relevant documents:

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

### 3. Get Hot Documents

```bash
curl http://localhost:8000/api/v1/hot-docs/case-001 \
  -H "X-API-Key: dev-api-key-change-in-production"
```

### 4. Monitor Costs

- Go to AWS Console → Cost Explorer
- Filter by Service: "Amazon Bedrock"
- Set up budget alerts

### 5. Customize Configuration

Edit `.env` to:
- Change API keys
- Adjust model selection
- Configure S3 bucket
- Set log levels

### 6. Deploy to Production

When ready:
1. Update `.env` with production models
2. Use production database (RDS)
3. Deploy with Docker Compose
4. Set up monitoring and alerts

## Development Tips

### Use API Documentation

The interactive docs at http://localhost:8000/docs let you:
- Test all endpoints
- See request/response schemas
- Try different parameters
- View authentication requirements

### Monitor Logs

Keep an eye on logs for:
- Processing times
- Error messages
- Token usage
- Cost estimates

### Test with Small Documents

Start with small documents (1-2 pages) to:
- Verify functionality
- Check quality
- Estimate costs
- Debug issues

### Use Development Models

Your current setup uses cost-effective models:
- Claude 3.5 Sonnet for complex tasks
- Claude 3 Haiku for simple tasks
- Same pricing as Claude 4.5
- Proven and stable

## Resources

- **API Docs**: http://localhost:8000/docs
- **Project Summary**: PROJECT_SUMMARY.md
- **Setup Guide**: SETUP_COMPLETE.md
- **Model Guide**: DEVELOPMENT_MODELS.md
- **Bedrock Setup**: BEDROCK_SETUP.md
- **Full README**: README.md

## Support

Need help?

1. Run verification: `python scripts/verify_setup.py`
2. Test Bedrock: `python scripts/test_bedrock.py`
3. Check logs: `docker-compose logs -f`
4. Review documentation files
5. Check AWS Bedrock console

## Summary

✅ **5-Minute Setup**
1. Enable AWS Bedrock models (2 min)
2. Configure `.env` (1 min)
3. Verify setup (1 min)
4. Start services (1 min)
5. Test API (30 sec)

✅ **You're Ready!**
- 6 AI agents running
- RAG system active
- API endpoints available
- Documentation complete

**Start analyzing documents now!** 🚀

```bash
# Quick test
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{"case_id":"test","document_id":"test-1","document_text":"Test document"}'
```
