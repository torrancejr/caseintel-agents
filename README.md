# CaseIntel AI Agents

AI-powered document analysis pipeline for legal case management. Built with FastAPI, Anthropic Claude, LangGraph, and ChromaDB.

## Overview

CaseIntel AI Agents is a sophisticated document analysis system that processes legal documents through a 6-agent pipeline:

1. **Document Classifier** - Identifies document type (contract, deposition, email, etc.)
2. **Metadata Extractor** - Extracts dates, people, entities, and locations
3. **Privilege Checker** - Scans for attorney-client privilege and confidentiality issues
4. **Hot Doc Detector** - Flags smoking guns, admissions, and contradictions
5. **Content Analyzer** - Generates summaries, key facts, and legal narratives
6. **Cross-Reference Engine** - Links documents and builds case timelines

## Architecture

```
User uploads document → FastAPI receives request → LangGraph orchestrates agents
→ Results stored in PostgreSQL + ChromaDB → Frontend displays analysis
```

## Features

- ✅ **6-Agent Pipeline** - Comprehensive document analysis
- ✅ **RAG System** - Ask AI questions about case documents
- ✅ **Timeline Building** - Automatic case timeline generation
- ✅ **Witness Tracking** - Cross-document witness mention analysis
- ✅ **Hot Doc Detection** - Automatic flagging of critical documents
- ✅ **Privilege Checking** - Attorney-client privilege detection
- ✅ **Vector Search** - ChromaDB for semantic document retrieval
- ✅ **Async Processing** - Background job processing with progress updates
- ✅ **S3 Integration** - Document storage and retrieval

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **AI**: Anthropic Claude (claude-sonnet-4-20250514)
- **Orchestration**: LangGraph, LangChain
- **Database**: PostgreSQL, SQLAlchemy
- **Vector DB**: ChromaDB (or Pinecone)
- **Storage**: AWS S3
- **Deployment**: Docker, Railway

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Anthropic API key
- AWS credentials (for S3)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/caseintel-agents.git
cd caseintel-agents
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Initialize database**
```bash
# The application will create tables on startup
# For production, use Alembic migrations
```

6. **Run the application**
```bash
uvicorn src.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Using Docker Compose

```bash
# Set environment variables in .env file
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## API Endpoints

### Health Check
```
GET /health
```

### Document Analysis
```
POST /api/v1/analyze
Content-Type: application/json
X-API-Key: your-api-key

{
  "document_url": "https://s3.amazonaws.com/bucket/document.pdf",
  "case_id": "case123",
  "callback_url": "https://yourapp.com/webhook"
}
```

### Check Status
```
GET /api/v1/status/{job_id}
X-API-Key: your-api-key
```

### Get Results
```
GET /api/v1/results/{job_id}
X-API-Key: your-api-key
```

### Ask AI
```
POST /api/v1/ask
Content-Type: application/json
X-API-Key: your-api-key

{
  "case_id": "case123",
  "question": "What evidence do we have of prior knowledge?"
}
```

### Case Timeline
```
GET /api/v1/case/{case_id}/timeline
X-API-Key: your-api-key
```

### Case Witnesses
```
GET /api/v1/case/{case_id}/witnesses
X-API-Key: your-api-key
```

## Project Structure

```
caseintel-agents/
├── src/
│   ├── agents/              # AI agents (6 agents)
│   │   ├── base.py
│   │   ├── classifier.py
│   │   ├── metadata_extractor.py
│   │   ├── privilege_checker.py
│   │   ├── hot_doc_detector.py
│   │   ├── content_analyzer.py
│   │   └── cross_reference.py
│   ├── workflows/           # LangGraph orchestration
│   │   ├── state.py
│   │   └── discovery_pipeline.py
│   ├── rag/                 # RAG system
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   └── retrieval.py
│   ├── models/              # Database models
│   │   ├── database.py
│   │   └── schemas.py
│   ├── services/            # Services
│   │   ├── db.py
│   │   ├── s3.py
│   │   └── notifications.py
│   └── api/                 # FastAPI application
│       ├── main.py
│       ├── dependencies.py
│       └── routes/
│           ├── health.py
│           ├── analyze.py
│           └── status.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── railway.toml
└── README.md
```

## Environment Variables

See `.env.example` for all required environment variables:

- `ANTHROPIC_API_KEY` - Anthropic API key
- `DATABASE_URL` - PostgreSQL connection string
- `CASEINTEL_API_KEY` - API key for authentication
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `S3_BUCKET` - S3 bucket name
- `CHROMA_PERSIST_DIR` - ChromaDB storage directory

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
# Format code
black src/

# Lint
flake8 src/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### AWS ECS

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Deploy to ECS cluster

### Docker

```bash
# Build image
docker build -t caseintel-agents .

# Run container
docker run -p 8000:8000 --env-file .env caseintel-agents
```

## Implementation Phases

### Phase 1: Foundation (Complete)
- ✅ All 6 agents implemented
- ✅ LangGraph pipeline orchestration
- ✅ Database models and API endpoints
- ✅ Basic RAG system with ChromaDB

### Phase 2: Enhancement (Next)
- ⏳ Parallel agent execution (Agents 2-4)
- ⏳ Real-time progress updates via WebSockets
- ⏳ Enhanced error handling and retry logic
- ⏳ Production embedding model integration

### Phase 3: Automation (Future)
- ⏳ Automatic analysis on document upload
- ⏳ Smart notifications and alerts
- ⏳ Batch processing for bulk uploads
- ⏳ Performance optimization and caching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Proprietary - CaseIntel.io

## Support

For issues and questions:
- Email: support@caseintel.io
- Documentation: https://docs.caseintel.io

## Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [ChromaDB](https://www.trychroma.com/)
