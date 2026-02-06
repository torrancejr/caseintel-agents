# CaseIntel AI Agents — Cursor Project Specification

> **Project:** caseintel-agents
> **Domain:** caseintel.io
> **Purpose:** AI-powered document analysis pipeline for legal case management
> **Stack:** Python 3.11 · FastAPI · Anthropic Claude · LangChain · LangGraph · ChromaDB/Pinecone · PostgreSQL · AWS (S3, Bedrock) · Docker

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Agent Pipeline](#agent-pipeline)
4. [Agent Specifications](#agent-specifications)
5. [RAG System](#rag-system)
6. [API Layer](#api-layer)
7. [Frontend Integration](#frontend-integration)
8. [Database Schema](#database-schema)
9. [Security & Auth](#security--auth)
10. [AWS Configuration](#aws-configuration)
11. [Deployment](#deployment)
12. [Implementation Phases](#implementation-phases)
13. [Coding Standards](#coding-standards)

---

## Architecture Overview

```
User uploads document on caseintel.io (Next.js frontend)
        │
        ▼
  Next.js API route calls caseintel-agents service
        │
        ▼
  FastAPI receives document URL + case_id
        │
        ▼
  LangGraph orchestrates agent pipeline
        │
        ├─ Agent 1: Document Classifier
        ├─ Agent 2: Metadata Extractor
        ├─ Agent 3: Privilege Checker
        ├─ Agent 4: Hot Doc Detector
        ├─ Agent 5: Content Analyzer
        └─ Agent 6: Cross-Reference Engine
        │
        ▼
  Results stored in PostgreSQL + Vector DB
        │
        ▼
  Frontend tabs auto-populate via webhook/polling
```

The pipeline runs asynchronously. When a user uploads a document, the frontend receives an immediate acknowledgment with a job ID, then polls or subscribes for progress updates as each agent completes its work.

---

## Project Structure

```
caseintel-agents/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base agent class with shared logic
│   │   ├── classifier.py           # Agent 1: Document Classifier
│   │   ├── metadata_extractor.py   # Agent 2: Metadata Extractor
│   │   ├── privilege_checker.py    # Agent 3: Privilege Checker
│   │   ├── hot_doc_detector.py     # Agent 4: Hot Doc Detector
│   │   ├── content_analyzer.py     # Agent 5: Content Analyzer
│   │   └── cross_reference.py      # Agent 6: Cross-Reference Engine
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunking.py             # Document chunking strategies
│   │   ├── embeddings.py           # Embedding generation
│   │   └── retrieval.py            # Vector search and retrieval
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── discovery_pipeline.py   # LangGraph workflow orchestration
│   │   └── state.py                # Shared pipeline state definitions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLAlchemy models
│   │   └── schemas.py              # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── s3.py                   # S3 document fetch/store
│   │   ├── notifications.py        # Progress updates to frontend
│   │   └── db.py                   # Database session management
│   └── api/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app, CORS, auth middleware
│       ├── routes/
│       │   ├── analyze.py          # /api/v1/analyze endpoint
│       │   ├── status.py           # /api/v1/status/{job_id} endpoint
│       │   └── health.py           # /health endpoint
│       └── dependencies.py         # Auth, DB session dependencies
├── tests/
│   ├── test_agents/
│   ├── test_rag/
│   ├── test_workflows/
│   └── test_api/
├── scripts/
│   └── seed_vectors.py             # Initial vector DB population
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── railway.toml
└── README.md
```

---

## Agent Pipeline

### Pipeline State (LangGraph)

The pipeline uses LangGraph to orchestrate agents. Define a shared state object that flows through each node:

```python
# src/workflows/state.py
from typing import TypedDict, Optional
from enum import Enum

class DocumentType(str, Enum):
    EMAIL = "email"
    CONTRACT = "contract"
    DEPOSITION = "deposition"
    PLEADING = "pleading"
    MEDICAL_RECORD = "medical_record"
    CORRESPONDENCE = "correspondence"
    FINANCIAL = "financial"
    DISCOVERY_RESPONSE = "discovery_response"
    EXHIBIT = "exhibit"
    OTHER = "other"

class PrivilegeFlag(str, Enum):
    ATTORNEY_CLIENT = "attorney_client"
    WORK_PRODUCT = "work_product"
    CONFIDENTIAL = "confidential"
    NONE = "none"

class PipelineState(TypedDict):
    # Input
    document_url: str
    case_id: str
    job_id: str
    raw_text: str

    # Agent 1 output
    document_type: Optional[DocumentType]
    classification_confidence: Optional[float]

    # Agent 2 output
    dates: Optional[list[dict]]           # [{date, context, source_page}]
    people: Optional[list[dict]]          # [{name, role, context}]
    entities: Optional[list[dict]]        # [{name, type, context}]
    locations: Optional[list[dict]]       # [{name, context}]

    # Agent 3 output
    privilege_flags: Optional[list[PrivilegeFlag]]
    privilege_reasoning: Optional[str]
    privilege_confidence: Optional[float]

    # Agent 4 output
    is_hot_doc: Optional[bool]
    hot_doc_reasons: Optional[list[dict]] # [{type, excerpt, reasoning}]
    hot_doc_score: Optional[float]        # 0.0 - 1.0

    # Agent 5 output
    summary: Optional[str]
    key_facts: Optional[list[str]]
    legal_issues: Optional[list[str]]
    draft_narrative: Optional[str]

    # Agent 6 output
    related_documents: Optional[list[dict]]   # [{doc_id, relevance, relationship}]
    timeline_events: Optional[list[dict]]     # [{date, event, source}]
    witness_mentions: Optional[list[dict]]    # [{name, doc_id, context}]

    # Pipeline metadata
    status: str                               # "processing", "completed", "failed"
    current_agent: Optional[str]
    progress_percent: int
    errors: list[dict]
```

### LangGraph Workflow Definition

```python
# src/workflows/discovery_pipeline.py
from langgraph.graph import StateGraph, END
from src.workflows.state import PipelineState

def build_pipeline() -> StateGraph:
    workflow = StateGraph(PipelineState)

    # Add agent nodes
    workflow.add_node("classify", classify_document)
    workflow.add_node("extract_metadata", extract_metadata)
    workflow.add_node("check_privilege", check_privilege)
    workflow.add_node("detect_hot_docs", detect_hot_docs)
    workflow.add_node("analyze_content", analyze_content)
    workflow.add_node("cross_reference", cross_reference)

    # Define edges — sequential pipeline
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract_metadata")
    workflow.add_edge("extract_metadata", "check_privilege")
    workflow.add_edge("check_privilege", "detect_hot_docs")
    workflow.add_edge("detect_hot_docs", "analyze_content")
    workflow.add_edge("analyze_content", "cross_reference")
    workflow.add_edge("cross_reference", END)

    return workflow.compile()
```

Agents 2-4 can optionally run in parallel since they are independent. For Phase 1, keep them sequential for simplicity. Parallelize in Phase 2.

---

## Agent Specifications

### Base Agent Pattern

All agents inherit from a base class that handles Claude API calls and error handling:

```python
# src/agents/base.py
from anthropic import Anthropic
import os

class BaseAgent:
    def __init__(self, name: str, model: str = "claude-sonnet-4-20250514"):
        self.name = name
        self.model = model
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def run(self, state: dict) -> dict:
        """Override in subclasses. Returns updated state fields."""
        raise NotImplementedError

    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text

    def _call_claude_structured(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        """Call Claude with tool_use to get structured JSON output."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            tools=[{
                "name": "structured_output",
                "description": "Return structured analysis results",
                "input_schema": schema
            }],
            tool_choice={"type": "tool", "name": "structured_output"}
        )
        for block in response.content:
            if block.type == "tool_use":
                return block.input
        return {}
```

### Agent 1: Document Classifier

**Purpose:** Identify the type of legal document uploaded.

**Categories:** Email, Contract, Deposition, Pleading, Medical Record, Correspondence, Financial Document, Discovery Response, Exhibit, Other.

**System Prompt Guidelines:**
- Analyze the document structure, formatting, headers, and content patterns
- Consider legal-specific markers: Bates numbers, case captions, signature blocks, header/footer patterns
- Return classification with confidence score (0.0–1.0)
- If confidence is below 0.7, flag for human review

**Output Schema:**
```json
{
    "document_type": "contract",
    "confidence": 0.95,
    "reasoning": "Document contains parties, recitals, numbered clauses, signature blocks",
    "sub_type": "employment_agreement"
}
```

### Agent 2: Metadata Extractor

**Purpose:** Extract all dates, people, entities, and locations from the document with source citations.

**System Prompt Guidelines:**
- Extract every date mentioned, with the surrounding context and page/paragraph reference
- Identify all people by name, infer their role where possible (plaintiff, witness, attorney, signatory)
- Extract organizations, companies, government bodies
- Extract locations with context
- Normalize date formats to ISO 8601
- Deduplicate entities that appear multiple times

**Output Schema:**
```json
{
    "dates": [
        {"date": "2024-03-15", "context": "Agreement effective date", "source_page": 1}
    ],
    "people": [
        {"name": "John Smith", "role": "plaintiff", "mentions": 12, "first_appearance": "page 1"}
    ],
    "entities": [
        {"name": "Acme Corp", "type": "corporation", "role": "defendant"}
    ],
    "locations": [
        {"name": "New York, NY", "context": "Governing law jurisdiction"}
    ]
}
```

### Agent 3: Privilege Checker

**Purpose:** Scan for potential attorney-client privilege, work product doctrine, and confidentiality issues.

**System Prompt Guidelines:**
- Look for communications between attorney and client
- Identify work product: legal analysis, strategy memos, litigation preparation
- Flag confidentiality markings: "CONFIDENTIAL", "PRIVILEGED", "ATTORNEY WORK PRODUCT"
- Check for inadvertent disclosure indicators
- Consider the document type from Agent 1 as context
- Return privilege flags with reasoning and confidence
- When in doubt, flag as potentially privileged (err on the side of caution)

**Output Schema:**
```json
{
    "privilege_flags": ["attorney_client"],
    "confidence": 0.85,
    "reasoning": "Email between in-house counsel and CEO discussing litigation strategy",
    "privileged_excerpts": [
        {"text": "Our legal position on this claim...", "type": "attorney_client", "page": 2}
    ],
    "recommendation": "review_required"
}
```

### Agent 4: Hot Doc Detector

**Purpose:** Flag documents that contain smoking guns, contradictions, key admissions, or other case-critical content.

**System Prompt Guidelines:**
- Identify admissions against interest
- Flag contradictions with known case facts (requires case context from RAG)
- Detect smoking gun language: explicit acknowledgment of wrongdoing, cover-up language, destruction of evidence references
- Score severity: critical (immediate attorney review), high (flag for review), medium (note for reference)
- Provide exact excerpts with page references
- Cross-reference against case theory and key issues

**Output Schema:**
```json
{
    "is_hot_doc": true,
    "severity": "critical",
    "score": 0.92,
    "flags": [
        {
            "type": "admission",
            "excerpt": "We knew about the defect before shipping...",
            "page": 3,
            "reasoning": "Direct admission of prior knowledge contradicting deposition testimony"
        }
    ]
}
```

### Agent 5: Content Analyzer

**Purpose:** Generate comprehensive summary, extract key facts, identify legal issues, and draft narrative sections.

**System Prompt Guidelines:**
- Generate a concise executive summary (2-3 paragraphs)
- Extract key facts as discrete, citable statements
- Identify legal issues and causes of action implicated
- Draft narrative paragraphs that could be used in a brief or memo
- Highlight evidentiary gaps where more documentation is needed
- Tailor analysis based on document type from Agent 1

**Output Schema:**
```json
{
    "summary": "This employment agreement between...",
    "key_facts": [
        "Non-compete clause extends 24 months post-termination",
        "Governing law is New York"
    ],
    "legal_issues": [
        "Enforceability of non-compete under NY law",
        "Ambiguous termination for cause definition"
    ],
    "draft_narrative": "The evidence establishes that...",
    "evidence_gaps": [
        "No documentation of performance reviews referenced in Section 4.2"
    ]
}
```

### Agent 6: Cross-Reference Engine

**Purpose:** Link the analyzed document to related documents, timeline events, and witness mentions across the case.

**System Prompt Guidelines:**
- Use RAG to find semantically similar documents in the case
- Build timeline events from extracted dates + context
- Map witness mentions across all documents in the case
- Identify document chains (email threads, contract amendments, related filings)
- Generate a witness consistency report when contradictions are found
- Score document relationships by relevance

**Output Schema:**
```json
{
    "related_documents": [
        {"doc_id": "doc_456", "title": "Smith Deposition", "relevance": 0.89, "relationship": "contradicts"}
    ],
    "timeline_events": [
        {"date": "2024-03-15", "event": "Contract executed", "source_doc": "current", "source_page": 12}
    ],
    "witness_mentions": [
        {"name": "John Smith", "appearances": [
            {"doc_id": "current", "context": "Signatory", "page": 12},
            {"doc_id": "doc_789", "context": "Deponent", "page": 1}
        ]}
    ],
    "consistency_flags": [
        {"witness": "John Smith", "issue": "Deposition states no knowledge of contract terms, but is signatory"}
    ]
}
```

---

## RAG System

### Chunking Strategy

```python
# src/rag/chunking.py

# Use a legal-document-aware chunking strategy:
# 1. Respect document structure: don't split across section headers, clauses, or paragraphs
# 2. Chunk size: 1000 tokens with 200 token overlap
# 3. Metadata per chunk: page number, section header, document_id, case_id
# 4. For contracts: chunk by clause
# 5. For depositions: chunk by Q&A exchange
# 6. For emails: chunk by message (don't split a single email)
```

### Embedding & Storage

```python
# src/rag/embeddings.py

# Use one of:
# Option A: ChromaDB (simpler, good for single-server deployment)
# Option B: Pinecone (managed, better for production scale)

# Embedding model: Use Anthropic's or OpenAI's embedding model
# Namespace per case: isolate case data in separate collections/namespaces
# Metadata filters: document_type, date_range, privilege_status, witness_name
```

### Retrieval

```python
# src/rag/retrieval.py

# For Agent 6 cross-referencing:
# 1. Embed the current document summary
# 2. Query vector DB with case_id filter
# 3. Return top-k related chunks with metadata
# 4. Use MMR (Maximal Marginal Relevance) to ensure diversity
# 5. Re-rank results using Claude for relevance scoring

# For Ask AI tab:
# 1. User question → embed
# 2. Retrieve top-k chunks across all case documents
# 3. Pass chunks + question to Claude for answer generation
# 4. Include source citations in response
```

---

## API Layer

### Endpoints

```
GET  /health                          → Health check
POST /api/v1/analyze                  → Submit document for analysis (auth required)
GET  /api/v1/status/{job_id}          → Check pipeline progress (auth required)
GET  /api/v1/results/{job_id}         → Get completed analysis results (auth required)
POST /api/v1/ask                      → Ask AI question about case docs (auth required)
GET  /api/v1/case/{case_id}/timeline  → Get case timeline (auth required)
GET  /api/v1/case/{case_id}/witnesses → Get witness map (auth required)
```

### Authentication

All endpoints except `/health` require API key authentication:

```python
# src/api/dependencies.py
from fastapi import Header, HTTPException
import os

API_KEY = os.getenv("CASEINTEL_API_KEY")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### CORS Configuration

```python
# src/api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://caseintel.io",
        "https://www.caseintel.io",
        "http://localhost:3000",     # Local dev only — remove in production
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### Request/Response Schemas

```python
# src/models/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnalyzeRequest(BaseModel):
    document_url: str       # S3 presigned URL or direct URL
    case_id: str
    callback_url: Optional[str] = None  # Webhook for completion notification

class AnalyzeResponse(BaseModel):
    job_id: str
    status: str             # "queued"
    message: str

class StatusResponse(BaseModel):
    job_id: str
    status: str             # "processing", "completed", "failed"
    current_agent: Optional[str]
    progress_percent: int
    agents_completed: list[str]
    started_at: datetime
    completed_at: Optional[datetime]

class ResultsResponse(BaseModel):
    job_id: str
    case_id: str
    document_type: str
    classification_confidence: float
    metadata: dict           # dates, people, entities, locations
    privilege: dict          # flags, reasoning, confidence
    hot_doc: dict            # is_hot, score, flags
    analysis: dict           # summary, key_facts, legal_issues
    cross_references: dict   # related_docs, timeline, witnesses
```

---

## Frontend Integration

### How Each Tab Gets Populated

When the agent pipeline completes, results flow to the frontend tabs:

| Frontend Tab | Data Source | Agents Involved |
|---|---|---|
| **Timeline** | `timeline_events` + `dates` | Agent 2 (extract) + Agent 6 (cross-ref) |
| **Witnesses** | `people` + `witness_mentions` + `consistency_flags` | Agent 2 (extract) + Agent 6 (cross-ref) |
| **Ask AI** | RAG over all processed docs | All agents populate the vector DB |
| **Narrative** | `draft_narrative` + `key_facts` + `evidence_gaps` | Agent 5 (analyze) |
| **Opposition** | `people` (filtered by role) + `entities` | Agent 2 (extract) + Agent 5 (analyze) |
| **Contracts** | Full pipeline on contract-type docs | Agent 1 (classify) + Agent 5 (analyze) |
| **Hot Docs** | `hot_doc_reasons` + `score` | Agent 4 (detect) |
| **Documents** | All pipeline outputs | All agents |

### Real-Time Progress Updates

The frontend should poll `GET /api/v1/status/{job_id}` every 2 seconds during processing. Display progress like:

```
Analyzing Document...
✓ Classified as Contract
✓ Extracted key terms
⚠️ Unusual clause detected (Line 247)
✓ Added to timeline
[78% Complete]
```

Progress mapping:
- Agent 1 complete → 15%
- Agent 2 complete → 35%
- Agent 3 complete → 50%
- Agent 4 complete → 65%
- Agent 5 complete → 80%
- Agent 6 complete → 100%

### Badge/Notification Updates

After pipeline completion, the frontend should update tab badges:
- Timeline tab badge: show count of new dates added
- Witnesses tab: "+N new witnesses identified"
- Hot Docs: warning icon if any flagged documents need review

---

## Database Schema

```sql
-- Jobs table: tracks pipeline execution
CREATE TABLE analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id VARCHAR(255) NOT NULL,
    document_url TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'queued',
    current_agent VARCHAR(100),
    progress_percent INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Results table: stores agent outputs
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES analysis_jobs(id),
    case_id VARCHAR(255) NOT NULL,
    document_type VARCHAR(100),
    classification_confidence FLOAT,
    metadata JSONB,          -- dates, people, entities, locations
    privilege_flags JSONB,
    hot_doc_data JSONB,
    analysis JSONB,          -- summary, key_facts, legal_issues
    cross_references JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Timeline events extracted by agents
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    event_description TEXT NOT NULL,
    source_document_id UUID,
    source_page INTEGER,
    created_by VARCHAR(50) DEFAULT 'agent',  -- 'agent' or 'user'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Witness tracking across documents
CREATE TABLE witness_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id VARCHAR(255) NOT NULL,
    witness_name VARCHAR(500) NOT NULL,
    role VARCHAR(100),
    document_id UUID,
    context TEXT,
    page_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_jobs_case ON analysis_jobs(case_id);
CREATE INDEX idx_results_case ON analysis_results(case_id);
CREATE INDEX idx_timeline_case_date ON timeline_events(case_id, date);
CREATE INDEX idx_witness_case ON witness_mentions(case_id, witness_name);
```

---

## Security & Auth

### Environment Variables

```bash
# .env (NEVER commit this file)
ANTHROPIC_API_KEY=sk-ant-...
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
CASEINTEL_API_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/caseintel
S3_BUCKET=caseintel-documents
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
```

### Database Connection Security

```python
from sqlalchemy import create_engine

engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)
```

### S3 Encryption

```python
s3_client.put_object(
    Bucket='caseintel-documents',
    Key=f'cases/{case_id}/{filename}',
    Body=file_content,
    ServerSideEncryption='AES256'
)
```

---

## AWS Configuration

### IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": ["arn:aws:s3:::caseintel-documents/*"]
        }
    ]
}
```

---

## Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
anthropic==0.18.0
langchain==0.1.6
langchain-anthropic==0.1.1
langgraph==0.0.20
chromadb==0.4.22
pinecone-client==3.0.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
pydantic==2.6.0
pydantic-settings==2.1.0
boto3==1.34.0
```

### Railway Deployment (Optional)

```toml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

---

## Implementation Phases

### Phase 1: Foundation (Days 1–14)

**Goal:** Replace basic LLM calls with the agent pipeline. No UX changes — "Run Workflow" button calls the new Python service.

Tasks:
1. Set up FastAPI project structure with all files and folders
2. Implement `BaseAgent` class with Claude API integration
3. Build Agent 1 (Classifier) and Agent 2 (Metadata Extractor) — these deliver the most visible value
4. Create the LangGraph pipeline with just these two agents
5. Set up PostgreSQL schema and database connection
6. Implement `/api/v1/analyze` and `/api/v1/status/{job_id}` endpoints
7. Connect Next.js frontend to call the new service instead of direct LLM calls
8. Deploy to Railway or AWS ECS
9. Test end-to-end: upload → classify → extract → store → display

### Phase 2: Full Pipeline + Transparency (Days 15–21)

**Goal:** Add remaining agents. Show real-time progress in the UI.

Tasks:
1. Implement Agent 3 (Privilege Checker)
2. Implement Agent 4 (Hot Doc Detector)
3. Implement Agent 5 (Content Analyzer)
4. Set up ChromaDB or Pinecone for RAG
5. Implement Agent 6 (Cross-Reference Engine) with RAG retrieval
6. Add real-time progress updates — frontend polls status endpoint, displays which agent is running
7. Implement tab badge updates after pipeline completion
8. Add error handling and retry logic for failed agents
9. Parallelize Agents 2–4 in the LangGraph workflow

### Phase 3: Automatic + Smart (Days 22–30)

**Goal:** Remove the manual trigger. Documents auto-analyze on upload. Smart notifications.

Tasks:
1. Wire document upload to automatically trigger the pipeline (no "Run Workflow" button)
2. Add webhook callback to notify frontend on completion
3. Implement smart notifications: "Document analysis complete — 1 hot doc flagged"
4. Build the Ask AI endpoint with RAG across all case documents
5. Implement witness consistency reports in Agent 6
6. Add draft narrative generation to Agent 5
7. Performance tuning: caching, batch processing for bulk uploads
8. Add monitoring and logging for production observability

---

## Coding Standards

### General Rules

- **Python 3.11+** with type hints on all function signatures
- **Pydantic v2** for all data validation and schemas
- **Async/await** for all I/O-bound operations (API calls, DB queries, S3)
- **Structured logging** with `structlog` or Python's `logging` module — include `job_id` and `case_id` in all log entries
- **Error handling:** Each agent wraps its logic in try/except. A failed agent should not crash the pipeline — log the error, store it in state, and continue to the next agent
- **No hardcoded secrets.** Everything goes through environment variables

### Agent Development Rules

- Every agent must inherit from `BaseAgent`
- Every agent must return a partial state dict (only the fields it's responsible for)
- Use Claude's structured output (tool_use) for all agent responses — never parse free-text
- Include a `confidence` score with every classification or flag
- When confidence is below threshold (0.7), mark the result for human review
- System prompts should be stored as constants at the top of each agent file, not inline
- Test each agent independently with sample documents before integrating into the pipeline

### Prompt Engineering Rules

- System prompts should be explicit about the legal domain context
- Include examples of expected output format in the system prompt
- For privilege checking: instruct the model to err on the side of caution
- For hot doc detection: provide case context from RAG so the agent can identify contradictions
- Keep prompts focused — each agent does one job well

### Testing

- Unit tests for each agent with mocked Claude responses
- Integration tests for the full pipeline with test documents
- Test with real legal document types: contracts, depositions, emails, pleadings
- Verify privilege detection catches common patterns
- Verify hot doc detection with known smoking gun documents

---

## Key Design Decisions

1. **Anthropic Claude over OpenAI:** Legal work requires strong reasoning about privilege, contradictions, and nuance. Claude excels at careful analysis and following complex instructions.

2. **LangGraph over simple chains:** The pipeline needs state management, conditional routing (skip privilege check for public filings), and eventually parallel execution. LangGraph handles this natively.

3. **Structured output via tool_use:** Forces consistent JSON schemas from every agent. No regex parsing of free text. Reliable, typed data flows through the pipeline.

4. **Separate Python service:** Keeps the agent logic decoupled from the Next.js frontend. Can scale independently. Can be called by other services in the future.

5. **RAG per case:** Each case gets its own namespace/collection in the vector DB. This ensures cross-reference searches only find related documents within the same case, preventing data leakage between clients.

6. **Sequential then parallel:** Phase 1 runs agents sequentially for simplicity and debuggability. Phase 2 parallelizes independent agents (2, 3, 4) while keeping dependencies (1 must run first, 6 must run last).
