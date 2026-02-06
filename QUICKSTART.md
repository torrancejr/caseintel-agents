# CaseIntel AI Agents - Quick Start Guide

Get up and running with CaseIntel AI Agents in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, but recommended)
- Anthropic API key
- PostgreSQL database (or use Docker Compose)

## Option 1: Docker Compose (Recommended)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/yourusername/caseintel-agents.git
cd caseintel-agents

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

### Step 2: Set Required Environment Variables

Edit `.env` and set at minimum:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
CASEINTEL_API_KEY=your-secure-random-key
DATABASE_URL=postgresql://caseintel:caseintel_dev_password@postgres:5432/caseintel
```

### Step 3: Start Services

```bash
# Start all services (API + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f api

# Check health
curl http://localhost:8000/health
```

### Step 4: Test the API

```bash
# Get API documentation
open http://localhost:8000/docs

# Test health endpoint
curl http://localhost:8000/health

# Submit a document for analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secure-random-key" \
  -d '{
    "document_url": "https://example.com/document.pdf",
    "case_id": "case123"
  }'

# Check job status (use job_id from previous response)
curl http://localhost:8000/api/v1/status/{job_id} \
  -H "X-API-Key: your-secure-random-key"
```

## Option 2: Local Development

### Step 1: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up PostgreSQL

```bash
# Install PostgreSQL (if not already installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Create database
createdb caseintel

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://yourusername@localhost:5432/caseintel
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env
```

Required variables:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
DATABASE_URL=postgresql://user@localhost:5432/caseintel
CASEINTEL_API_KEY=your-secure-random-key
CHROMA_PERSIST_DIR=./chroma_db
ENVIRONMENT=development
```

### Step 4: Run the Application

```bash
# Run with uvicorn
uvicorn src.api.main:app --reload --port 8000

# Or run directly
python -m src.api.main
```

### Step 5: Verify Setup

```bash
# Run verification script
python scripts/verify_setup.py

# Seed vector database (optional)
python scripts/seed_vectors.py

# Run tests
pytest tests/ -v
```

## Quick API Examples

### 1. Analyze a Document

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "document_url": "https://s3.amazonaws.com/bucket/contract.pdf",
    "case_id": "case_001",
    "callback_url": "https://yourapp.com/webhook"
  }'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Document analysis queued successfully"
}
```

### 2. Check Job Status

```bash
curl http://localhost:8000/api/v1/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: your-api-key"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "current_agent": "MetadataExtractor",
  "progress_percent": 35,
  "agents_completed": ["DocumentClassifier"],
  "started_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get Results

```bash
curl http://localhost:8000/api/v1/results/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: your-api-key"
```

### 4. Ask AI a Question

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "case_id": "case_001",
    "question": "What are the key terms of the employment agreement?"
  }'
```

### 5. Get Case Timeline

```bash
curl http://localhost:8000/api/v1/case/case_001/timeline \
  -H "X-API-Key: your-api-key"
```

### 6. Get Case Witnesses

```bash
curl http://localhost:8000/api/v1/case/case_001/witnesses \
  -H "X-API-Key: your-api-key"
```

## Accessing API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### API Key Issues

```bash
# Verify API key is set
echo $CASEINTEL_API_KEY

# Check .env file
cat .env | grep CASEINTEL_API_KEY
```

### Anthropic API Issues

```bash
# Test Anthropic API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### View Logs

```bash
# Docker Compose logs
docker-compose logs -f api

# Local development logs
# Logs are printed to console when running with --reload
```

### Reset Everything

```bash
# Stop and remove all containers
docker-compose down -v

# Remove ChromaDB data
rm -rf chroma_db/

# Start fresh
docker-compose up -d
```

## Next Steps

1. **Read the full documentation**: See `README.md` for detailed information
2. **Review the specification**: Check `CASEINTEL_AGENTS.md` for system design
3. **Explore the code**: Start with `src/api/main.py` and `src/workflows/discovery_pipeline.py`
4. **Run tests**: `pytest tests/ -v`
5. **Customize agents**: Modify system prompts in `src/agents/` files
6. **Deploy to production**: See deployment section in `README.md`

## Common Use Cases

### Analyze a Contract

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "your-api-key"
    },
    json={
        "document_url": "https://example.com/contract.pdf",
        "case_id": "case_001"
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")
```

### Poll for Results

```python
import time
import requests

def wait_for_completion(job_id, api_key):
    while True:
        response = requests.get(
            f"http://localhost:8000/api/v1/status/{job_id}",
            headers={"X-API-Key": api_key}
        )
        status = response.json()
        
        print(f"Progress: {status['progress_percent']}% - {status['current_agent']}")
        
        if status["status"] == "completed":
            break
        
        time.sleep(2)
    
    # Get results
    response = requests.get(
        f"http://localhost:8000/api/v1/results/{job_id}",
        headers={"X-API-Key": api_key}
    )
    return response.json()

results = wait_for_completion(job_id, "your-api-key")
print(f"Document Type: {results['classification']['document_type']}")
print(f"Summary: {results['analysis']['summary']}")
```

## Support

- **Documentation**: See `README.md` and `CASEINTEL_AGENTS.md`
- **Issues**: Open an issue on GitHub
- **Email**: support@caseintel.io

## Success! 🎉

You're now ready to use CaseIntel AI Agents for legal document analysis!

Visit http://localhost:8000/docs to explore the API interactively.
