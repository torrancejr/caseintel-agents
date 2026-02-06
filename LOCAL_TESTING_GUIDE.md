# 🧪 Local Testing Guide - CaseIntel AI Agents

## Quick Start

### 1. Start the Python Agents API

```bash
cd agents
source venv/bin/activate  # or: venv\Scripts\activate on Windows
uvicorn src.api.main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Check Health Status

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-06T...",
  "version": "1.0.0"
}
```

### 3. Test Document Analysis

Create a test file `test_analyze.sh`:

```bash
#!/bin/bash

# Test document analysis endpoint
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6" \
  -d '{
    "document_url": "https://caseintel-documents.s3.amazonaws.com/test-document.pdf",
    "case_id": "test-case-123",
    "callback_url": "http://localhost:4000/api/webhooks/agents"
  }' | python -m json.tool
```

Make it executable:
```bash
chmod +x test_analyze.sh
./test_analyze.sh
```

## Current Status

✅ **Working:**
- FastAPI server starts successfully
- AWS Bedrock connection (125 models available)
- ChromaDB vector database
- Embedding model (Amazon Titan v2, 1024 dimensions)

⚠️ **Needs Attention:**
- Database connection (trying port 5432 instead of 5433)
- Agent imports in verification script

## Troubleshooting

### Database Connection Issue

If you see: `connection to server at "localhost" (::1), port 5432 failed`

**Fix:** The DATABASE_URL in `.env` is correct (port 5433), but SQLAlchemy might be parsing it incorrectly.

Check your `.env` file:
```bash
DATABASE_URL=postgresql://caseintel:caseintel_dev@localhost:5433/caseintel
```

Test the connection manually:
```bash
psql -h localhost -p 5433 -U caseintel -d caseintel
# Password: caseintel_dev
```

### Virtual Environment Not Activated

If you see `command not found: uvicorn`:

```bash
cd agents
source venv/bin/activate  # Activate the virtual environment
```

Or use the full path:
```bash
./venv/bin/uvicorn src.api.main:app --reload --port 8000
```

## Testing Workflow

### Phase 1: Basic API Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **List Available Models** (optional)
   ```bash
   curl http://localhost:8000/api/v1/models \
     -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
   ```

### Phase 2: Document Analysis Testing

1. **Upload a test document to S3** (or use existing URL)

2. **Trigger analysis**
   ```bash
   curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Content-Type: application/json" \
     -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6" \
     -d '{
       "document_url": "YOUR_S3_URL_HERE",
       "case_id": "test-case-123"
     }'
   ```

3. **Check status**
   ```bash
   curl http://localhost:8000/api/v1/status/JOB_ID \
     -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
   ```

4. **Get results**
   ```bash
   curl http://localhost:8000/api/v1/results/JOB_ID \
     -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"
   ```

### Phase 3: Integration with Backend

1. **Start the NestJS backend** (in another terminal)
   ```bash
   cd backend/caseintel-backend
   npm run start:dev
   ```

2. **Test the full flow:**
   - Upload document via frontend (http://localhost:3000)
   - Backend stores in S3
   - Backend calls agents API
   - Agents process document
   - Results stored in database
   - Frontend displays results

## Environment Variables Checklist

Make sure these are set in `agents/.env`:

- ✅ `AWS_ACCESS_KEY_ID` - Your AWS access key
- ✅ `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- ✅ `AWS_REGION=us-east-1`
- ✅ `DATABASE_URL=postgresql://caseintel:caseintel_dev@localhost:5433/caseintel`
- ✅ `CASEINTEL_API_KEY` - API key for authentication
- ✅ `S3_BUCKET=caseintel-documents`
- ✅ `CHROMA_PERSIST_DIR=./chroma_db`

## Next Steps

Once local testing is working:

1. ✅ Verify all 6 agents work correctly
2. ✅ Test with real legal documents
3. ✅ Measure processing times and costs
4. ✅ Document any issues or improvements
5. 🚀 Ready for AWS deployment planning

## Useful Commands

```bash
# Start agents API
cd agents && ./venv/bin/uvicorn src.api.main:app --reload --port 8000

# Start backend API
cd backend/caseintel-backend && npm run start:dev

# Start frontend
cd frontend-web/caseintel-frontend && npm run dev

# Check PostgreSQL
psql -h localhost -p 5433 -U caseintel -d caseintel

# View logs
tail -f agents/logs/app.log  # if logging to file

# Run tests
cd agents && pytest tests/
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Cost Monitoring

Track your AWS Bedrock usage:
- Classification (Haiku): ~$0.01 per document
- Privilege/Hot Doc/Content (Sonnet): ~$0.45 per document
- Embeddings (Titan): ~$0.01 per document
- **Total**: ~$0.54 per 100-page document

Monitor in AWS Console:
https://console.aws.amazon.com/billing/home#/bills

---

**Status**: Agents API is running on port 8000 ✅  
**Next**: Fix database connection and test document analysis
