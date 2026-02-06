# Design Document: CaseIntel Phased Roadmap

## Overview

This design document provides a comprehensive 12-month phased rollout plan for transforming CaseIntel from a production-ready MVP with manual triggers into a fully automated, scalable legal document intelligence platform. The roadmap covers five distinct phases, each building upon the previous to add automation, parallel processing, advanced AI capabilities, and enterprise-scale infrastructure.

### Current State (Phase 1)

**Architecture:**
- **Frontend**: React + TypeScript (Vercel)
- **Backend**: NestJS + GraphQL (Railway)
- **AI Agents**: Python + FastAPI + LangGraph (Railway)
- **Database**: PostgreSQL (Railway/AWS RDS)
- **AI Models**: AWS Bedrock (Claude 3.5 Sonnet, Claude 3 Haiku)
- **Vector DB**: ChromaDB (local/embedded)
- **Storage**: AWS S3

**Current Workflow:**
1. User uploads document → Frontend
2. Backend stores in S3, extracts text (OCR)
3. **[MANUAL]** User clicks "Analyze" button
4. Backend calls Python Agents API
5. 6 AI agents run sequentially via LangGraph
6. Results stored in PostgreSQL
7. Frontend displays results

**Limitations:**
- Manual trigger required
- Sequential agent processing (slow)
- No batch processing
- No real-time updates
- Single Railway instance (scaling limits)

### Target State (Phase 5)

**Architecture:**
- **Frontend**: React + TypeScript (Vercel/CloudFront)
- **Backend**: NestJS + GraphQL (AWS ECS/Fargate)
- **AI Agents**: Python + FastAPI + LangGraph (AWS ECS/Lambda)
- **Database**: PostgreSQL (AWS RDS Multi-AZ)
- **AI Models**: AWS Bedrock (Claude 4.5 Sonnet, Claude 4.5 Haiku)
- **Vector DB**: Pinecone or AWS OpenSearch
- **Storage**: AWS S3 with lifecycle policies
- **Queue**: AWS SQS or BullMQ with Redis
- **Cache**: Redis (ElastiCache)
- **Monitoring**: CloudWatch, X-Ray, DataDog

**Target Workflow:**
1. User uploads document → Automatic trigger
2. Event-driven architecture initiates pipeline
3. Parallel agent processing (2-4 run simultaneously)
4. Real-time progress updates via WebSocket
5. Batch processing for bulk uploads
6. Predictive analytics and cross-case intelligence
7. Proactive alerts and notifications

## Architecture

### Phase 1: Current MVP (Baseline)

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)               │
│                     Hosted on Vercel                         │
└─────────────────────────────────────────────────────────────┘
                              │ GraphQL
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend API (NestJS + TypeORM)                │
│                   Hosted on Railway                          │
│  - User Auth, Case Mgmt, Document Mgmt, OCR, Billing        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │  AI Agents   │    │   AWS S3     │
│   Railway    │    │   (Python)   │    │  Documents   │
│              │    │   Railway    │    │   Storage    │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │ AWS Bedrock  │
                  │ Claude 3.5   │
                  │ ChromaDB     │
                  └──────────────┘
```

**Key Characteristics:**
- Single Railway instance for backend
- Single Railway instance for agents
- Synchronous processing
- Manual triggers
- No caching layer
- Basic monitoring


### Phase 2: Automated Workflows (Months 1-2)

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)               │
│                     Hosted on Vercel                         │
│                  + WebSocket for real-time updates           │
└─────────────────────────────────────────────────────────────┘
                              │ GraphQL + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend API (NestJS + TypeORM)                │
│                   Hosted on Railway → AWS ECS                │
│  - Event-driven architecture                                 │
│  - Webhook triggers for document upload                      │
│  - GraphQL subscriptions for progress                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │  AI Agents   │    │   AWS S3     │
│   AWS RDS    │    │   (Python)   │    │  Documents   │
│              │    │   AWS ECS    │    │   Storage    │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │ AWS Bedrock  │
                  │ Claude 3.5   │
                  │ ChromaDB     │
                  └──────────────┘
```

**Key Changes:**
- Automatic document processing (no manual trigger)
- WebSocket/GraphQL subscriptions for real-time updates
- Migration from Railway to AWS ECS begins
- Event-driven architecture with webhooks
- Improved error handling and retry logic

**New Components:**
- WebSocket server for real-time updates
- Event bus for document upload events
- Notification service (email, Slack)

### Phase 3: Parallel Processing & Batch Operations (Months 3-4)

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)               │
│                     Hosted on Vercel                         │
│                  + Real-time progress tracking               │
└─────────────────────────────────────────────────────────────┘
                              │ GraphQL + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend API (NestJS + TypeORM)                │
│                   Hosted on AWS ECS (Auto-scaling)           │
│  - Job queue management                                      │
│  - Batch upload handling                                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │ Message Queue│    │   AWS S3     │
│   AWS RDS    │    │  AWS SQS or  │    │  Documents   │
│   Multi-AZ   │    │  BullMQ+Redis│    │   Storage    │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │  AI Agents   │
                  │   (Python)   │
                  │   AWS ECS    │
                  │  (Multiple   │
                  │   Workers)   │
                  └──────┬───────┘
                         │
                         ▼
                ┌──────────────┐
                │ AWS Bedrock  │
                │ Claude 3.5   │
                │ + LangGraph  │
                │ Parallel     │
                │ Execution    │
                └──────────────┘
```

**Key Changes:**
- Message queue for asynchronous job processing
- LangGraph workflow modified for parallel agent execution
- Multiple worker instances for agents
- Batch processing capability (10-100 documents at once)
- Auto-scaling based on queue depth

**New Components:**
- AWS SQS or BullMQ with Redis
- Worker pool for agent processing
- Job scheduler and priority queue
- Progress aggregation service


### Phase 4: Advanced Workflows & Intelligence (Months 5-6)

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)               │
│                     Hosted on CloudFront + S3                │
│  - Advanced timeline visualization                           │
│  - Hot doc alerts dashboard                                  │
│  - Privilege review workflow UI                              │
└─────────────────────────────────────────────────────────────┘
                              │ GraphQL + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend API (NestJS + TypeORM)                │
│                   Hosted on AWS ECS (Auto-scaling)           │
│  - Advanced workflow orchestration                           │
│  - Multi-channel notifications (Email, Slack, SMS)           │
│  - Privilege review automation                               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │ Message Queue│    │   AWS S3     │
│   AWS RDS    │    │   AWS SQS    │    │  + Glacier   │
│   Multi-AZ   │    │              │    │  (Archive)   │
│  + Read      │    └──────┬───────┘    └──────────────┘
│  Replicas    │           │
└──────────────┘           ▼
                  ┌──────────────┐
                  │  AI Agents   │
                  │   (Python)   │
                  │   AWS ECS    │
                  │  + Lambda    │
                  │  (Serverless)│
                  └──────┬───────┘
                         │
                         ▼
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ AWS Bedrock  │ │   Pinecone   │ │    Redis     │
│ Claude 4.5   │ │  (Vectors)   │ │  (Cache)     │
│ Sonnet/Haiku │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

**Key Changes:**
- Privilege review automation with confidence scoring
- Timeline conflict detection and resolution
- Hot doc severity scoring and multi-channel alerts
- Witness consistency checking across documents
- Contract comparison workflows
- Serverless functions for lightweight tasks

**New Components:**
- Pinecone for production-grade vector search
- Redis cache for frequently accessed data
- Twilio integration for SMS alerts
- Slack webhook integration
- Advanced notification routing engine

### Phase 5: Scale & Predictive Intelligence (Months 7-12)

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)               │
│                     Hosted on CloudFront + S3                │
│  - Predictive analytics dashboard                            │
│  - Multi-case intelligence views                             │
│  - Advanced reporting and exports                            │
└─────────────────────────────────────────────────────────────┘
                              │ GraphQL + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend API (NestJS + TypeORM)                │
│                   Hosted on AWS ECS (Auto-scaling)           │
│  - Multi-case analytics engine                               │
│  - Predictive modeling service                               │
│  - Advanced reporting engine                                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │ Message Queue│    │   AWS S3     │
│   AWS RDS    │    │   AWS SQS    │    │  + Glacier   │
│   Multi-AZ   │    │              │    │  (Archive)   │
│  + Read      │    └──────┬───────┘    └──────────────┘
│  Replicas    │           │
│  + Analytics │           ▼
│  Warehouse   │  ┌──────────────┐
└──────────────┘  │  AI Agents   │
                  │   (Python)   │
                  │   AWS ECS    │
                  │  + Lambda    │
                  │  (Serverless)│
                  └──────┬───────┘
                         │
                         ▼
        ┌────────────────┼────────────────┬────────────────┐
        ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ AWS Bedrock  │ │   Pinecone   │ │    Redis     │ │  CloudWatch  │
│ Claude 4.5   │ │  (Vectors)   │ │  (Cache)     │ │  + X-Ray     │
│ Sonnet/Haiku │ │              │ │              │ │  + DataDog   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**Key Changes:**
- Predictive analytics for case outcomes
- Multi-case pattern recognition
- Advanced reporting and data warehouse
- Comprehensive monitoring and observability
- Cost optimization and reserved capacity
- Enterprise-grade security and compliance

**New Components:**
- Analytics data warehouse (Redshift or Snowflake)
- Predictive modeling service
- Advanced monitoring stack (DataDog, X-Ray)
- Cost optimization tools
- Compliance and audit logging


## Components and Interfaces

### Backend API (NestJS)

**Current Endpoints:**
- `POST /graphql` - GraphQL API
- `GET /health` - Health check
- `POST /webhooks/stripe` - Stripe webhooks

**Phase 2 Additions:**
- `POST /webhooks/document-upload` - Internal webhook for document events
- `WS /subscriptions` - GraphQL subscriptions for real-time updates

**Phase 3 Additions:**
- `POST /api/v1/batch/analyze` - Batch document analysis
- `GET /api/v1/batch/status/:batchId` - Batch status
- `POST /api/v1/jobs/priority` - Set job priority

**Phase 4 Additions:**
- `POST /api/v1/alerts/configure` - Configure alert preferences
- `GET /api/v1/timeline/conflicts/:caseId` - Get timeline conflicts
- `POST /api/v1/privilege/review` - Submit privilege review decision

**Phase 5 Additions:**
- `GET /api/v1/analytics/predictions/:caseId` - Get case predictions
- `GET /api/v1/analytics/multi-case` - Cross-case analytics
- `POST /api/v1/reports/generate` - Generate custom reports

### Python Agents Service (FastAPI)

**Current Endpoints:**
- `POST /api/v1/analyze` - Analyze single document
- `GET /api/v1/status/:jobId` - Get analysis status
- `GET /health` - Health check

**Phase 2 Additions:**
- `POST /api/v1/analyze/async` - Async analysis with callback
- `POST /api/v1/webhook/callback` - Receive completion callbacks

**Phase 3 Additions:**
- `POST /api/v1/batch/analyze` - Batch analysis
- `GET /api/v1/batch/status/:batchId` - Batch status
- `POST /api/v1/agents/parallel` - Trigger parallel agent execution

**Phase 4 Additions:**
- `POST /api/v1/privilege/deep-analysis` - Deep privilege analysis
- `POST /api/v1/timeline/extract-events` - Extract timeline events
- `POST /api/v1/hotdoc/severity` - Analyze hot doc severity
- `POST /api/v1/witness/consistency` - Check witness consistency

**Phase 5 Additions:**
- `POST /api/v1/predict/outcome` - Predict case outcome
- `POST /api/v1/analyze/multi-case` - Multi-case pattern analysis
- `GET /api/v1/models/performance` - Model performance metrics

### LangGraph Workflow

**Current Workflow (Sequential):**
```python
workflow = StateGraph(PipelineState)
workflow.add_node("classify", classify_document)
workflow.add_node("extract_metadata", extract_metadata)
workflow.add_node("check_privilege", check_privilege)
workflow.add_node("detect_hot_docs", detect_hot_docs)
workflow.add_node("analyze_content", analyze_content)
workflow.add_node("cross_reference", cross_reference)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "extract_metadata")
workflow.add_edge("extract_metadata", "check_privilege")
workflow.add_edge("check_privilege", "detect_hot_docs")
workflow.add_edge("detect_hot_docs", "analyze_content")
workflow.add_edge("analyze_content", "cross_reference")
workflow.add_edge("cross_reference", END)
```

**Phase 3 Workflow (Parallel):**
```python
workflow = StateGraph(PipelineState)
workflow.add_node("classify", classify_document)
workflow.add_node("extract_metadata", extract_metadata)
workflow.add_node("check_privilege", check_privilege)
workflow.add_node("detect_hot_docs", detect_hot_docs)
workflow.add_node("analyze_content", analyze_content)
workflow.add_node("cross_reference", cross_reference)

# Classifier runs first
workflow.set_entry_point("classify")

# Agents 2-4 run in parallel after classifier
workflow.add_conditional_edges(
    "classify",
    lambda x: ["extract_metadata", "check_privilege", "detect_hot_docs"],
    {
        "extract_metadata": "extract_metadata",
        "check_privilege": "check_privilege",
        "detect_hot_docs": "detect_hot_docs"
    }
)

# Wait for all parallel agents to complete
workflow.add_edge(["extract_metadata", "check_privilege", "detect_hot_docs"], "analyze_content")
workflow.add_edge("analyze_content", "cross_reference")
workflow.add_edge("cross_reference", END)
```

### Database Schema Evolution

**Phase 1 (Current):**
- `users`, `firms`, `cases`, `documents`
- `classifications`, `timeline_events`, `witnesses`
- `analysis_jobs`, `analysis_results`
- `witness_mentions`, `agent_execution_logs`

**Phase 2 Additions:**
```sql
-- Webhook events tracking
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100),
    payload JSONB,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Real-time subscriptions
CREATE TABLE active_subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    case_id UUID REFERENCES cases(id),
    subscription_type VARCHAR(50),
    connection_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Phase 3 Additions:**
```sql
-- Batch jobs
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    total_documents INTEGER,
    completed_documents INTEGER DEFAULT 0,
    failed_documents INTEGER DEFAULT 0,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Job queue
CREATE TABLE job_queue (
    id UUID PRIMARY KEY,
    batch_id UUID REFERENCES batch_jobs(id),
    document_id UUID REFERENCES documents(id),
    priority INTEGER DEFAULT 0,
    status VARCHAR(50),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_job_queue_status_priority ON job_queue(status, priority DESC);
```

**Phase 4 Additions:**
```sql
-- Alert configurations
CREATE TABLE alert_configurations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50),
    channels JSONB, -- ["email", "slack", "sms"]
    thresholds JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Timeline conflicts
CREATE TABLE timeline_conflicts (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    event_date DATE,
    conflict_description TEXT,
    source_documents JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Privilege reviews
CREATE TABLE privilege_reviews (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    confidence_score FLOAT,
    auto_flagged BOOLEAN,
    reviewer_id UUID REFERENCES users(id),
    review_decision VARCHAR(50),
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);
```

**Phase 5 Additions:**
```sql
-- Predictive analytics
CREATE TABLE case_predictions (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    prediction_type VARCHAR(100),
    prediction_value JSONB,
    confidence_score FLOAT,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Multi-case patterns
CREATE TABLE cross_case_patterns (
    id UUID PRIMARY KEY,
    pattern_type VARCHAR(100),
    case_ids JSONB,
    pattern_description TEXT,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Model performance tracking
CREATE TABLE model_performance (
    id UUID PRIMARY KEY,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    measured_at TIMESTAMP DEFAULT NOW()
);
```


## Data Models

### PipelineState (LangGraph)

```python
from typing import TypedDict, Optional, List
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
    dates: Optional[List[dict]]
    people: Optional[List[dict]]
    entities: Optional[List[dict]]
    locations: Optional[List[dict]]
    
    # Agent 3 output
    privilege_flags: Optional[List[PrivilegeFlag]]
    privilege_reasoning: Optional[str]
    privilege_confidence: Optional[float]
    
    # Agent 4 output
    is_hot_doc: Optional[bool]
    hot_doc_reasons: Optional[List[dict]]
    hot_doc_score: Optional[float]
    
    # Agent 5 output
    summary: Optional[str]
    key_facts: Optional[List[str]]
    legal_issues: Optional[List[str]]
    draft_narrative: Optional[str]
    
    # Agent 6 output
    related_documents: Optional[List[dict]]
    timeline_events: Optional[List[dict]]
    witness_mentions: Optional[List[dict]]
    
    # Pipeline metadata
    status: str
    current_agent: Optional[str]
    progress_percent: int
    errors: List[dict]
```

### BatchJob Model

```typescript
interface BatchJob {
  id: string;
  caseId: string;
  totalDocuments: number;
  completedDocuments: number;
  failedDocuments: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  priority: number;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  estimatedCompletionTime?: Date;
}
```

### AlertConfiguration Model

```typescript
interface AlertConfiguration {
  id: string;
  userId: string;
  alertType: 'hot_doc' | 'privilege' | 'timeline_conflict' | 'deadline';
  channels: ('email' | 'slack' | 'sms' | 'in_app')[];
  thresholds: {
    hotDocSeverity?: 'critical' | 'high' | 'medium';
    privilegeConfidence?: number;
    deadlineDays?: number;
  };
  enabled: boolean;
  createdAt: Date;
}
```

### CasePrediction Model

```typescript
interface CasePrediction {
  id: string;
  caseId: string;
  predictionType: 'outcome' | 'settlement_value' | 'timeline' | 'risk_score';
  predictionValue: any;
  confidenceScore: number;
  modelVersion: string;
  factors: {
    factor: string;
    weight: number;
    value: any;
  }[];
  createdAt: Date;
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Phase Structure Completeness

*For any* phased roadmap document, it should contain exactly 5 distinct phases, each phase should have a defined timeline that collectively spans 12 months, and each phase should specify goals, success metrics, and completion criteria.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8**

### Property 2: Architecture Documentation Completeness

*For any* phase in the roadmap, the architecture section should document the complete system architecture, highlight changes from the previous phase, specify integration points between all major components (NestJS backend, React frontend, Python agents, AWS services), and describe data flow patterns.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**

### Property 3: Infrastructure Specification Completeness

*For any* phase in the roadmap, the infrastructure section should list all required AWS services, specify service types and configurations, document environment variables, define resource requirements, provide deployment order and dependencies, and include monthly cost estimates.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10**

### Property 4: Service Evolution Documentation

*For any* phase in the roadmap, the documentation should specify Python Agents Service API changes, database schema evolution with migration scripts, API versioning strategy, monitoring requirements, and all required documentation artifacts.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7**

### Property 5: Release and Testing Strategy Completeness

*For any* phase in the roadmap, the release strategy should define beta cohort selection, rollout percentages, feature flags, rollback plans, risk mitigation strategies, and testing requirements (unit, integration, end-to-end, performance).

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

## Error Handling

### Phase 1-2: Basic Error Handling

**Document Upload Errors:**
- S3 upload failures → Retry 3 times with exponential backoff
- OCR failures → Flag for manual review, notify user
- Invalid file formats → Reject with clear error message

**Agent Processing Errors:**
- AWS Bedrock API errors → Retry with exponential backoff
- Agent timeout (> 5 minutes) → Cancel and flag for review
- Partial agent failures → Store partial results, mark job as incomplete

**Database Errors:**
- Connection failures → Retry with connection pool
- Transaction failures → Rollback and retry
- Constraint violations → Log and return error to user

### Phase 3: Enhanced Error Handling

**Batch Processing Errors:**
- Individual document failures → Continue batch, track failed documents
- Queue overflow → Apply backpressure, throttle new submissions
- Worker crashes → Requeue jobs, restart workers

**Parallel Processing Errors:**
- Agent deadlocks → Timeout and restart
- Resource exhaustion → Scale up workers or queue jobs
- Partial parallel failures → Aggregate successful results, retry failures

### Phase 4-5: Advanced Error Handling

**Workflow Errors:**
- Timeline conflict detection failures → Log and continue
- Alert delivery failures → Retry with different channel
- Prediction model errors → Fall back to rule-based approach

**System-Wide Error Handling:**
- Circuit breakers for external services (AWS Bedrock, Pinecone)
- Graceful degradation (disable non-critical features)
- Automatic rollback on critical errors
- Dead letter queues for unprocessable jobs

## Testing Strategy

### Unit Testing

**Backend (NestJS):**
- Test all GraphQL resolvers
- Test webhook handlers
- Test business logic services
- Test database repositories
- Target: 80% code coverage

**Agents (Python):**
- Test each agent independently with mocked AWS Bedrock
- Test LangGraph workflow state transitions
- Test RAG retrieval logic
- Test error handling and retries
- Target: 85% code coverage

**Frontend (React):**
- Test all components with React Testing Library
- Test GraphQL queries and mutations
- Test WebSocket connections
- Test state management
- Target: 75% code coverage

### Integration Testing

**Phase 1-2:**
- End-to-end document upload → analysis → results flow
- Backend ↔ Agents API integration
- Database transaction integrity
- S3 upload and retrieval

**Phase 3:**
- Batch processing workflows
- Message queue integration
- Parallel agent execution
- Progress tracking accuracy

**Phase 4-5:**
- Multi-channel alert delivery
- Timeline conflict detection
- Privilege review workflows
- Predictive analytics pipeline

### Performance Testing

**Phase 1-2:**
- Single document processing: < 45 seconds (100 pages)
- API response time: < 200ms (p95)
- Database query performance: < 100ms (p95)

**Phase 3:**
- Batch processing: 100 documents in < 20 minutes
- Queue throughput: > 100 jobs/minute
- Parallel agent execution: 3x speedup vs sequential

**Phase 4-5:**
- Real-time alert delivery: < 5 seconds
- Timeline conflict detection: < 2 seconds per document
- Predictive analytics: < 10 seconds per case

### Load Testing

**Phase 3:**
- Simulate 10 concurrent users uploading 10 documents each
- Verify auto-scaling triggers correctly
- Verify no job loss under load

**Phase 5:**
- Simulate 100 concurrent users
- Verify system stability under sustained load
- Verify cost efficiency at scale


## Detailed Phase Specifications

### Phase 1: Current MVP (Baseline)

**Timeline:** Current state (Month 0)

**Goals:**
- Document current architecture and capabilities
- Establish baseline metrics
- Identify pain points and limitations

**Success Metrics:**
- Document processing time: 5-45 seconds per document
- Classification accuracy: ~95%
- Privilege detection accuracy: ~92%
- System uptime: 99.5%

**Infrastructure (Railway):**
- Backend: 1 instance (2 vCPU, 4GB RAM)
- Agents: 1 instance (2 vCPU, 4GB RAM)
- PostgreSQL: Shared database (2GB storage)

**Monthly Costs:**
- Railway: ~$30
- AWS Bedrock: ~$50-100
- AWS S3: ~$10
- AWS RDS: ~$50
- **Total: ~$140-190/month**

**Completion Criteria:**
- ✅ All current features documented
- ✅ Baseline metrics established
- ✅ Migration plan to Phase 2 approved

### Phase 2: Automated Workflows (Months 1-2)

**Timeline:** 8 weeks

**Goals:**
- Eliminate manual "Analyze" button
- Implement event-driven architecture
- Add real-time progress updates
- Begin AWS migration

**Success Metrics:**
- 100% automatic document processing
- Real-time updates with < 2 second latency
- Zero manual triggers required
- 99.9% uptime

**Key Features:**
1. **Automatic Document Processing**
   - Webhook triggers on document upload
   - Event-driven pipeline initiation
   - No user intervention required

2. **Real-Time Updates**
   - WebSocket or GraphQL subscriptions
   - Progress tracking per agent
   - Live status updates in UI

3. **Enhanced Notifications**
   - Email notifications on completion
   - Slack integration (optional)
   - In-app notifications

**Infrastructure Changes:**

**AWS Services to Deploy:**
- AWS ECS Fargate for backend (migrate from Railway)
- AWS ECS Fargate for agents (migrate from Railway)
- AWS RDS PostgreSQL Multi-AZ
- AWS S3 (existing)
- AWS CloudWatch for logging
- Application Load Balancer

**Deployment Order:**
1. Set up AWS VPC and networking
2. Deploy RDS PostgreSQL
3. Migrate database from Railway
4. Deploy backend to ECS
5. Deploy agents to ECS
6. Update DNS to point to ALB
7. Decommission Railway instances

**Environment Variables:**
```bash
# Backend (NestJS)
DATABASE_URL=postgresql://...
AWS_REGION=us-east-1
AWS_S3_BUCKET=caseintel-documents
AGENTS_API_URL=http://agents-service:8000
WEBSOCKET_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Agents (Python)
DATABASE_URL=postgresql://...
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_CLASSIFIER=anthropic.claude-3-haiku-20240307-v1:0
AWS_BEDROCK_MODEL_PRIVILEGE=us.anthropic.claude-3-5-sonnet-20241022-v2:0
CHROMADB_PATH=/data/chromadb
CALLBACK_WEBHOOK_URL=http://backend-service/webhooks/agent-complete
```

**Monthly Costs:**
- AWS ECS (Backend): ~$50 (0.5 vCPU, 1GB RAM)
- AWS ECS (Agents): ~$70 (1 vCPU, 2GB RAM)
- AWS RDS Multi-AZ: ~$120 (db.t3.small)
- AWS ALB: ~$20
- AWS CloudWatch: ~$10
- AWS Bedrock: ~$100-200 (increased usage)
- AWS S3: ~$15
- **Total: ~$385-485/month**

**Testing Requirements:**
- Unit tests for webhook handlers
- Integration tests for event-driven flows
- End-to-end tests for automatic processing
- Load test with 10 concurrent uploads

**Rollback Plan:**
1. Revert DNS to Railway instances
2. Keep Railway instances running for 1 week
3. Monitor for issues
4. Decommission Railway after successful migration

**Beta Rollout:**
- Week 1-2: Internal testing (5 beta users)
- Week 3-4: Beta cohort (10 users)
- Week 5-6: Expanded beta (25 users)
- Week 7-8: Full rollout (all users)

**Completion Criteria:**
- ✅ 100% automatic document processing
- ✅ Real-time updates working
- ✅ AWS migration complete
- ✅ Railway decommissioned
- ✅ Zero critical bugs for 1 week


### Phase 3: Parallel Processing & Batch Operations (Months 3-4)

**Timeline:** 8 weeks

**Goals:**
- Enable parallel agent execution
- Support batch document uploads
- Implement job queue system
- Improve processing speed by 3x

**Success Metrics:**
- Parallel processing: 3x faster than sequential
- Batch processing: 100 documents in < 20 minutes
- Queue throughput: > 100 jobs/minute
- 99.9% uptime maintained

**Key Features:**
1. **Parallel Agent Execution**
   - Agents 2-4 run simultaneously
   - LangGraph workflow modification
   - Resource optimization

2. **Batch Processing**
   - Upload 10-100 documents at once
   - Progress tracking per batch
   - Aggregate reporting

3. **Job Queue System**
   - Priority queue for urgent documents
   - Retry logic for failed jobs
   - Dead letter queue for unprocessable jobs

**Infrastructure Changes:**

**New AWS Services:**
- AWS SQS (Standard Queue) for job queue
- AWS ElastiCache Redis for caching
- Additional ECS tasks for workers

**ECS Configuration:**
- Backend: 2-4 tasks (auto-scaling)
- Agents: 4-8 tasks (auto-scaling based on queue depth)
- Auto-scaling triggers:
  - Scale up: Queue depth > 50 jobs
  - Scale down: Queue depth < 10 jobs

**LangGraph Workflow Changes:**
```python
# Modified workflow for parallel execution
workflow = StateGraph(PipelineState)

# Add all nodes
workflow.add_node("classify", classify_document)
workflow.add_node("extract_metadata", extract_metadata)
workflow.add_node("check_privilege", check_privilege)
workflow.add_node("detect_hot_docs", detect_hot_docs)
workflow.add_node("analyze_content", analyze_content)
workflow.add_node("cross_reference", cross_reference)

# Classifier runs first
workflow.set_entry_point("classify")

# Parallel execution of agents 2-4
workflow.add_conditional_edges(
    "classify",
    lambda x: ["extract_metadata", "check_privilege", "detect_hot_docs"],
    {
        "extract_metadata": "extract_metadata",
        "check_privilege": "check_privilege",
        "detect_hot_docs": "detect_hot_docs"
    }
)

# Wait for all parallel agents, then continue
workflow.add_edge(["extract_metadata", "check_privilege", "detect_hot_docs"], "analyze_content")
workflow.add_edge("analyze_content", "cross_reference")
workflow.add_edge("cross_reference", END)
```

**Database Schema Changes:**
```sql
-- Batch jobs table
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id),
    user_id UUID REFERENCES users(id),
    total_documents INTEGER NOT NULL,
    completed_documents INTEGER DEFAULT 0,
    failed_documents INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion_time TIMESTAMP
);

-- Job queue table
CREATE TABLE job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batch_jobs(id),
    document_id UUID REFERENCES documents(id),
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_job_queue_status_priority ON job_queue(status, priority DESC, created_at);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status, created_at);
```

**API Changes:**
```typescript
// New GraphQL mutations
mutation AnalyzeBatch($input: BatchAnalyzeInput!) {
  analyzeBatch(input: $input) {
    batchId
    totalDocuments
    estimatedCompletionTime
  }
}

mutation SetJobPriority($jobId: ID!, $priority: Int!) {
  setJobPriority(jobId: $jobId, priority: $priority) {
    success
  }
}

// New GraphQL subscriptions
subscription BatchProgress($batchId: ID!) {
  batchProgress(batchId: $batchId) {
    batchId
    completedDocuments
    failedDocuments
    currentDocument {
      id
      name
      progress
    }
  }
}
```

**Monthly Costs:**
- AWS ECS (Backend): ~$100 (auto-scaling 2-4 tasks)
- AWS ECS (Agents): ~$200 (auto-scaling 4-8 tasks)
- AWS RDS Multi-AZ: ~$120
- AWS ALB: ~$20
- AWS SQS: ~$5
- AWS ElastiCache Redis: ~$50 (cache.t3.small)
- AWS CloudWatch: ~$15
- AWS Bedrock: ~$300-500 (3x usage due to parallel processing)
- AWS S3: ~$20
- **Total: ~$830-1,030/month**

**Testing Requirements:**
- Unit tests for queue management
- Integration tests for parallel execution
- Load tests with 100 concurrent documents
- Stress tests for queue overflow scenarios
- Performance benchmarks (3x speedup validation)

**Rollback Plan:**
1. Disable batch upload feature via feature flag
2. Revert to sequential agent processing
3. Drain SQS queue
4. Scale down ECS tasks
5. Monitor for 24 hours before re-enabling

**Beta Rollout:**
- Week 1-2: Internal testing with 10-document batches
- Week 3-4: Beta cohort with 50-document batches
- Week 5-6: Expanded beta with 100-document batches
- Week 7-8: Full rollout

**Completion Criteria:**
- ✅ Parallel processing 3x faster than sequential
- ✅ Batch processing working for 100+ documents
- ✅ Auto-scaling functioning correctly
- ✅ Queue system stable under load
- ✅ Zero data loss in batch processing


### Phase 4: Advanced Workflows & Intelligence (Months 5-6)

**Timeline:** 8 weeks

**Goals:**
- Implement privilege review automation
- Add timeline conflict detection
- Build hot doc severity scoring
- Enable multi-channel alerts

**Success Metrics:**
- Privilege review time reduced by 80%
- Timeline conflicts detected automatically
- Hot doc alerts delivered in < 5 seconds
- 99.95% uptime

**Key Features:**
1. **Privilege Review Automation**
   - Confidence scoring (0-100%)
   - Auto-flag high confidence (>95%)
   - Review queue for medium confidence (70-95%)
   - Privilege log generation

2. **Timeline Automation**
   - Automatic event extraction
   - Conflict detection (same date, different facts)
   - Gap identification (> 30 days)
   - Statute of limitations tracking

3. **Hot Doc Severity Scoring**
   - Critical: Smoking gun, immediate review
   - High: Important, review within 24 hours
   - Medium: Notable, review within week

4. **Multi-Channel Alerts**
   - Email notifications
   - Slack integration
   - SMS via Twilio (critical alerts only)
   - In-app notifications

**Infrastructure Changes:**

**New AWS Services:**
- AWS Lambda for lightweight alert processing
- AWS SNS for notification routing
- AWS EventBridge for event orchestration
- Pinecone for production-grade vector search (replace ChromaDB)

**ECS Configuration:**
- Backend: 2-6 tasks (auto-scaling)
- Agents: 4-10 tasks (auto-scaling)
- Lambda functions: 10 concurrent executions

**Database Schema Changes:**
```sql
-- Alert configurations
CREATE TABLE alert_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50) NOT NULL,
    channels JSONB NOT NULL, -- ["email", "slack", "sms", "in_app"]
    thresholds JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Timeline conflicts
CREATE TABLE timeline_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id),
    event_date DATE NOT NULL,
    conflict_description TEXT NOT NULL,
    source_documents JSONB NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    resolved_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Privilege reviews
CREATE TABLE privilege_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    confidence_score FLOAT NOT NULL,
    auto_flagged BOOLEAN DEFAULT FALSE,
    privilege_type VARCHAR(50),
    reasoning TEXT,
    reviewer_id UUID REFERENCES users(id),
    review_decision VARCHAR(50),
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

-- Hot doc alerts
CREATE TABLE hot_doc_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    case_id UUID REFERENCES cases(id),
    severity VARCHAR(20) NOT NULL, -- critical, high, medium
    alert_reasons JSONB NOT NULL,
    score FLOAT NOT NULL,
    notified_users JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    acknowledged_at TIMESTAMP
);

CREATE INDEX idx_timeline_conflicts_case ON timeline_conflicts(case_id, resolved);
CREATE INDEX idx_privilege_reviews_document ON privilege_reviews(document_id);
CREATE INDEX idx_hot_doc_alerts_severity ON hot_doc_alerts(severity, acknowledged, created_at);
```

**API Changes:**
```typescript
// New GraphQL queries
query GetTimelineConflicts($caseId: ID!) {
  timelineConflicts(caseId: $caseId) {
    id
    eventDate
    conflictDescription
    sourceDocuments {
      id
      name
      excerpt
    }
    severity
    resolved
  }
}

query GetPrivilegeReviewQueue($caseId: ID!) {
  privilegeReviewQueue(caseId: $caseId) {
    id
    document {
      id
      name
    }
    confidenceScore
    privilegeType
    reasoning
  }
}

// New GraphQL mutations
mutation ConfigureAlerts($input: AlertConfigInput!) {
  configureAlerts(input: $input) {
    success
  }
}

mutation ResolveTimelineConflict($conflictId: ID!, $resolution: String!) {
  resolveTimelineConflict(conflictId: $conflictId, resolution: $resolution) {
    success
  }
}

mutation SubmitPrivilegeReview($reviewId: ID!, $decision: PrivilegeDecision!, $notes: String) {
  submitPrivilegeReview(reviewId: $reviewId, decision: $decision, notes: $notes) {
    success
  }
}
```

**Agent Enhancements:**

**Agent 3 (Privilege Checker) - Enhanced:**
```python
async def check_privilege_enhanced(state: PipelineState) -> dict:
    """Enhanced privilege checking with confidence scoring."""
    
    # Deep analysis with Claude 3.5 Sonnet
    result = await bedrock_client.invoke_model(
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        prompt=privilege_prompt,
        max_tokens=4096
    )
    
    confidence = result['confidence_score']
    
    # Auto-flag based on confidence
    if confidence > 0.95:
        action = "auto_flag"
    elif confidence > 0.70:
        action = "review_queue"
    else:
        action = "no_action"
    
    return {
        "privilege_flags": result['flags'],
        "privilege_confidence": confidence,
        "privilege_reasoning": result['reasoning'],
        "privilege_action": action
    }
```

**Agent 4 (Hot Doc Detector) - Enhanced:**
```python
async def detect_hot_docs_enhanced(state: PipelineState) -> dict:
    """Enhanced hot doc detection with severity scoring."""
    
    result = await bedrock_client.invoke_model(
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        prompt=hot_doc_prompt,
        max_tokens=4096
    )
    
    score = result['hot_doc_score']
    
    # Determine severity
    if score > 0.90:
        severity = "critical"
    elif score > 0.75:
        severity = "high"
    elif score > 0.60:
        severity = "medium"
    else:
        severity = "low"
    
    # Trigger alerts for critical/high
    if severity in ["critical", "high"]:
        await trigger_alerts(state['case_id'], state['document_id'], severity, result)
    
    return {
        "is_hot_doc": score > 0.60,
        "hot_doc_score": score,
        "hot_doc_severity": severity,
        "hot_doc_reasons": result['reasons']
    }
```

**Notification Service (Lambda):**
```python
import boto3
from twilio.rest import Client

sns = boto3.client('sns')
twilio_client = Client(account_sid, auth_token)

async def send_alert(alert_config, alert_data):
    """Send alert via configured channels."""
    
    for channel in alert_config['channels']:
        if channel == 'email':
            await send_email(alert_config['user_email'], alert_data)
        
        elif channel == 'slack':
            await send_slack(alert_config['slack_webhook'], alert_data)
        
        elif channel == 'sms' and alert_data['severity'] == 'critical':
            twilio_client.messages.create(
                to=alert_config['phone_number'],
                from_=twilio_phone,
                body=f"CRITICAL: {alert_data['message']}"
            )
        
        elif channel == 'in_app':
            await send_in_app_notification(alert_config['user_id'], alert_data)
```

**Monthly Costs:**
- AWS ECS (Backend): ~$150 (auto-scaling 2-6 tasks)
- AWS ECS (Agents): ~$300 (auto-scaling 4-10 tasks)
- AWS RDS Multi-AZ: ~$150 (db.t3.medium upgrade)
- AWS ALB: ~$20
- AWS SQS: ~$10
- AWS ElastiCache Redis: ~$50
- AWS Lambda: ~$20
- AWS SNS: ~$5
- AWS EventBridge: ~$5
- Pinecone: ~$70 (Starter plan)
- Twilio: ~$20 (SMS credits)
- AWS CloudWatch: ~$20
- AWS Bedrock: ~$500-700 (increased usage)
- AWS S3: ~$25
- **Total: ~$1,345-1,545/month**

**Testing Requirements:**
- Unit tests for privilege scoring logic
- Integration tests for alert delivery
- End-to-end tests for timeline conflict detection
- Load tests for alert system (100 alerts/minute)
- Failover tests for notification channels

**Rollback Plan:**
1. Disable advanced features via feature flags
2. Revert to basic privilege detection
3. Disable multi-channel alerts
4. Monitor for 48 hours
5. Re-enable features incrementally

**Beta Rollout:**
- Week 1-2: Internal testing (privilege review)
- Week 3-4: Beta cohort (timeline + alerts)
- Week 5-6: Expanded beta (all features)
- Week 7-8: Full rollout

**Completion Criteria:**
- ✅ Privilege review automation working
- ✅ Timeline conflicts detected accurately
- ✅ Hot doc alerts delivered reliably
- ✅ Multi-channel notifications functioning
- ✅ User satisfaction > 90%


### Phase 5: Scale & Predictive Intelligence (Months 7-12)

**Timeline:** 24 weeks

**Goals:**
- Implement predictive analytics
- Enable multi-case intelligence
- Build enterprise-grade infrastructure
- Achieve 99.99% uptime

**Success Metrics:**
- Predictive accuracy > 85%
- Multi-case pattern detection working
- System handles 1000+ documents/day
- 99.99% uptime
- Cost per document < $0.40

**Key Features:**
1. **Predictive Analytics**
   - Case outcome prediction
   - Settlement value estimation
   - Timeline prediction
   - Risk scoring

2. **Multi-Case Intelligence**
   - Cross-case pattern recognition
   - Similar case identification
   - Precedent analysis
   - Witness credibility tracking across cases

3. **Advanced Reporting**
   - Custom report generation
   - Data warehouse for analytics
   - Executive dashboards
   - Export to multiple formats

4. **Enterprise Features**
   - SSO integration (SAML, OAuth)
   - Advanced audit logging
   - Compliance reporting (GDPR, CCPA)
   - White-label options

**Infrastructure Changes:**

**New AWS Services:**
- AWS Redshift or Snowflake for data warehouse
- AWS SageMaker for custom ML models
- AWS Cognito for SSO
- AWS WAF for security
- AWS CloudFront for CDN
- AWS Backup for automated backups

**ECS Configuration:**
- Backend: 4-10 tasks (auto-scaling)
- Agents: 6-15 tasks (auto-scaling)
- Lambda functions: 50 concurrent executions
- Reserved capacity for cost optimization

**Database Schema Changes:**
```sql
-- Case predictions
CREATE TABLE case_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id),
    prediction_type VARCHAR(100) NOT NULL,
    prediction_value JSONB NOT NULL,
    confidence_score FLOAT NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    factors JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Cross-case patterns
CREATE TABLE cross_case_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(100) NOT NULL,
    case_ids JSONB NOT NULL,
    pattern_description TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    supporting_evidence JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Model performance tracking
CREATE TABLE model_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    measured_at TIMESTAMP DEFAULT NOW()
);

-- Audit logs (enhanced)
CREATE TABLE audit_logs_enhanced (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    firm_id UUID REFERENCES firms(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_case_predictions_case ON case_predictions(case_id, prediction_type);
CREATE INDEX idx_cross_case_patterns_type ON cross_case_patterns(pattern_type, created_at);
CREATE INDEX idx_audit_logs_user_action ON audit_logs_enhanced(user_id, action, created_at);
```

**API Changes:**
```typescript
// New GraphQL queries
query GetCasePredictions($caseId: ID!) {
  casePredictions(caseId: $caseId) {
    id
    predictionType
    predictionValue
    confidenceScore
    factors {
      factor
      weight
      value
    }
    createdAt
  }
}

query FindSimilarCases($caseId: ID!, $limit: Int = 10) {
  similarCases(caseId: $caseId, limit: $limit) {
    id
    name
    similarity
    commonFactors
    outcome
  }
}

query GetCrossCase Patterns($firmId: ID!, $patternType: String) {
  crossCasePatterns(firmId: $firmId, patternType: $patternType) {
    id
    patternType
    caseIds
    description
    confidenceScore
    supportingEvidence
  }
}

// New GraphQL mutations
mutation GenerateCustomReport($input: ReportInput!) {
  generateCustomReport(input: $input) {
    reportId
    downloadUrl
    expiresAt
  }
}

mutation RequestPrediction($caseId: ID!, $predictionType: PredictionType!) {
  requestPrediction(caseId: $caseId, predictionType: $predictionType) {
    predictionId
    estimatedCompletionTime
  }
}
```

**Predictive Analytics Service:**
```python
from sklearn.ensemble import RandomForestClassifier
import boto3

sagemaker = boto3.client('sagemaker-runtime')

class PredictiveAnalytics:
    """Predictive analytics for case outcomes."""
    
    async def predict_outcome(self, case_id: str) -> dict:
        """Predict case outcome based on historical data."""
        
        # Gather case features
        features = await self.extract_features(case_id)
        
        # Invoke SageMaker endpoint
        response = sagemaker.invoke_endpoint(
            EndpointName='caseintel-outcome-predictor',
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        prediction = json.loads(response['Body'].read())
        
        return {
            'prediction_type': 'outcome',
            'prediction_value': prediction['outcome'],
            'confidence_score': prediction['confidence'],
            'factors': prediction['factors']
        }
    
    async def extract_features(self, case_id: str) -> dict:
        """Extract features for prediction."""
        
        # Get case data
        case = await db.get_case(case_id)
        documents = await db.get_documents(case_id)
        
        features = {
            'document_count': len(documents),
            'hot_doc_count': sum(1 for d in documents if d.is_hot_doc),
            'privileged_doc_count': sum(1 for d in documents if d.is_privileged),
            'timeline_length_days': (case.latest_event - case.earliest_event).days,
            'witness_count': len(await db.get_witnesses(case_id)),
            'case_type': case.case_type,
            'jurisdiction': case.jurisdiction,
            # ... more features
        }
        
        return features
```

**Multi-Case Intelligence Service:**
```python
class MultiCaseIntelligence:
    """Cross-case pattern recognition."""
    
    async def find_similar_cases(self, case_id: str, limit: int = 10) -> list:
        """Find similar cases using vector similarity."""
        
        # Get case embedding
        case_embedding = await self.get_case_embedding(case_id)
        
        # Query Pinecone for similar cases
        results = pinecone_index.query(
            vector=case_embedding,
            top_k=limit,
            filter={"firm_id": firm_id}  # Respect multi-tenancy
        )
        
        similar_cases = []
        for match in results['matches']:
            case = await db.get_case(match['id'])
            similar_cases.append({
                'id': case.id,
                'name': case.name,
                'similarity': match['score'],
                'common_factors': await self.identify_common_factors(case_id, case.id),
                'outcome': case.outcome
            })
        
        return similar_cases
    
    async def detect_patterns(self, firm_id: str) -> list:
        """Detect patterns across all firm cases."""
        
        cases = await db.get_firm_cases(firm_id)
        
        patterns = []
        
        # Pattern 1: Recurring witnesses
        witness_patterns = await self.analyze_witness_patterns(cases)
        patterns.extend(witness_patterns)
        
        # Pattern 2: Common document types
        doc_type_patterns = await self.analyze_document_patterns(cases)
        patterns.extend(doc_type_patterns)
        
        # Pattern 3: Timeline similarities
        timeline_patterns = await self.analyze_timeline_patterns(cases)
        patterns.extend(timeline_patterns)
        
        return patterns
```

**Monthly Costs:**
- AWS ECS (Backend): ~$300 (auto-scaling 4-10 tasks)
- AWS ECS (Agents): ~$600 (auto-scaling 6-15 tasks)
- AWS RDS Multi-AZ: ~$200 (db.t3.large)
- AWS RDS Read Replicas: ~$200 (2 replicas)
- AWS ALB: ~$20
- AWS SQS: ~$15
- AWS ElastiCache Redis: ~$100 (cache.t3.medium)
- AWS Lambda: ~$50
- AWS SNS: ~$10
- AWS EventBridge: ~$10
- AWS Redshift: ~$300 (dc2.large, 2 nodes)
- AWS SageMaker: ~$200 (ml.t3.medium endpoint)
- AWS CloudFront: ~$50
- AWS WAF: ~$30
- AWS Backup: ~$20
- Pinecone: ~$200 (Standard plan)
- Twilio: ~$30
- AWS CloudWatch: ~$40
- AWS Bedrock: ~$800-1200 (high usage)
- AWS S3: ~$40
- **Total: ~$3,215-3,615/month**

**Cost Optimization Strategies:**
1. **Reserved Instances:**
   - RDS: 1-year reserved → Save 30% (~$120/month savings)
   - ElastiCache: 1-year reserved → Save 30% (~$30/month savings)

2. **Spot Instances:**
   - ECS tasks for non-critical workloads → Save 50% (~$200/month savings)

3. **S3 Lifecycle Policies:**
   - Move old documents to Glacier after 90 days → Save 80% on storage

4. **Bedrock Model Selection:**
   - Use Claude 4.5 Haiku for simple tasks → Save 50% on those calls
   - Cache common prompts → Save 10-20% overall

**Optimized Monthly Costs: ~$2,500-2,900/month**

**Testing Requirements:**
- Unit tests for prediction models
- Integration tests for multi-case queries
- Performance tests for data warehouse queries
- Security tests for SSO integration
- Compliance tests for audit logging

**Rollback Plan:**
1. Disable predictive features via feature flags
2. Revert to Phase 4 infrastructure
3. Maintain data warehouse for analytics
4. Monitor for 1 week before re-enabling

**Beta Rollout:**
- Months 7-8: Internal testing (predictive analytics)
- Months 9-10: Beta cohort (multi-case intelligence)
- Months 11-12: Full rollout (all features)

**Completion Criteria:**
- ✅ Predictive analytics accuracy > 85%
- ✅ Multi-case patterns detected reliably
- ✅ System handles 1000+ documents/day
- ✅ 99.99% uptime achieved
- ✅ Cost per document < $0.40
- ✅ Enterprise features working
- ✅ Customer satisfaction > 95%


## Deployment Strategy

### Railway to AWS Migration (Phase 2)

**Pre-Migration Checklist:**
- [ ] AWS account setup with proper IAM roles
- [ ] VPC and networking configured
- [ ] RDS PostgreSQL provisioned and tested
- [ ] S3 buckets created with proper permissions
- [ ] ECS clusters created
- [ ] Docker images built and pushed to ECR
- [ ] Environment variables configured in AWS Secrets Manager
- [ ] Load balancer configured with SSL certificates
- [ ] DNS records prepared (but not switched)

**Migration Steps:**

**Week 1: Infrastructure Setup**
1. Create AWS VPC with public/private subnets
2. Set up RDS PostgreSQL Multi-AZ
3. Configure security groups and NACLs
4. Set up Application Load Balancer
5. Create ECS clusters (backend and agents)

**Week 2: Database Migration**
1. Take snapshot of Railway PostgreSQL
2. Restore to AWS RDS
3. Verify data integrity
4. Set up replication from Railway to AWS (if possible)
5. Test database connectivity from ECS

**Week 3: Service Deployment**
1. Deploy backend to ECS (parallel to Railway)
2. Deploy agents to ECS (parallel to Railway)
3. Configure ALB to route to ECS services
4. Test all endpoints
5. Run integration tests

**Week 4: Cutover**
1. Enable read-only mode on Railway
2. Final database sync
3. Switch DNS to AWS ALB
4. Monitor for 24 hours
5. Decommission Railway instances

**Rollback Procedure:**
1. Switch DNS back to Railway
2. Re-enable write mode on Railway database
3. Investigate issues
4. Fix and retry migration

### Blue-Green Deployment Strategy

**For All Phases:**
1. Deploy new version to "green" environment
2. Run smoke tests on green
3. Gradually shift traffic: 10% → 25% → 50% → 100%
4. Monitor error rates and latency
5. If issues detected, shift traffic back to "blue"
6. Once stable, promote green to blue

**Traffic Shifting with ALB:**
```yaml
# Target groups for blue-green deployment
TargetGroupBlue:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: caseintel-backend-blue
    Port: 3000
    Protocol: HTTP
    VpcId: !Ref VPC

TargetGroupGreen:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: caseintel-backend-green
    Port: 3000
    Protocol: HTTP
    VpcId: !Ref VPC

# Listener rule for weighted routing
ListenerRule:
  Type: AWS::ElasticLoadBalancingV2::ListenerRule
  Properties:
    Actions:
      - Type: forward
        ForwardConfig:
          TargetGroups:
            - TargetGroupArn: !Ref TargetGroupBlue
              Weight: 90
            - TargetGroupArn: !Ref TargetGroupGreen
              Weight: 10
```

### Feature Flag Strategy

**Feature Flag Service:**
```typescript
// Feature flag configuration
interface FeatureFlags {
  automaticProcessing: boolean;
  batchUpload: boolean;
  parallelProcessing: boolean;
  privilegeReview: boolean;
  timelineConflicts: boolean;
  hotDocAlerts: boolean;
  predictiveAnalytics: boolean;
  multiCaseIntelligence: boolean;
}

// Feature flag service
class FeatureFlagService {
  async isEnabled(flag: keyof FeatureFlags, userId?: string): Promise<boolean> {
    // Check user-specific overrides
    if (userId) {
      const userOverride = await this.getUserOverride(userId, flag);
      if (userOverride !== null) return userOverride;
    }
    
    // Check global flag
    const globalFlag = await this.getGlobalFlag(flag);
    return globalFlag;
  }
  
  async enableForBeta(flag: keyof FeatureFlags, userIds: string[]): Promise<void> {
    // Enable feature for specific beta users
    for (const userId of userIds) {
      await this.setUserOverride(userId, flag, true);
    }
  }
}
```

### Monitoring and Alerting

**CloudWatch Dashboards:**
1. **System Health Dashboard**
   - ECS task health
   - RDS connections and CPU
   - ALB request count and latency
   - SQS queue depth

2. **Application Metrics Dashboard**
   - Document processing time (p50, p95, p99)
   - Agent execution time per agent
   - Error rates by endpoint
   - Bedrock API latency and costs

3. **Business Metrics Dashboard**
   - Documents processed per day
   - Active users
   - Revenue metrics
   - Cost per document

**CloudWatch Alarms:**
```yaml
# High error rate alarm
HighErrorRateAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: caseintel-high-error-rate
    MetricName: 5XXError
    Namespace: AWS/ApplicationELB
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SNSAlertTopic

# High latency alarm
HighLatencyAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: caseintel-high-latency
    MetricName: TargetResponseTime
    Namespace: AWS/ApplicationELB
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 2.0
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SNSAlertTopic

# Queue depth alarm
QueueDepthAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: caseintel-queue-depth-high
    MetricName: ApproximateNumberOfMessagesVisible
    Namespace: AWS/SQS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 100
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SNSAlertTopic
```

## Risk Mitigation

### Technical Risks

**Risk 1: AWS Bedrock Rate Limiting**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Implement exponential backoff with jitter
  - Request quota increase from AWS
  - Cache common responses
  - Implement circuit breaker pattern
  - Monitor rate limit metrics

**Risk 2: Database Performance Degradation**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Implement read replicas for queries
  - Add database connection pooling
  - Optimize slow queries
  - Implement caching layer (Redis)
  - Monitor query performance

**Risk 3: Cost Overruns**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Set up AWS Budgets with alerts
  - Implement cost allocation tags
  - Use reserved instances for predictable workloads
  - Optimize Bedrock model selection
  - Monitor cost per document metric

**Risk 4: Data Loss During Migration**
- **Probability:** Low
- **Impact:** Critical
- **Mitigation:**
  - Multiple database backups before migration
  - Parallel run Railway and AWS for 1 week
  - Verify data integrity with checksums
  - Test restore procedures
  - Maintain Railway backup for 30 days

**Risk 5: Parallel Processing Bugs**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Extensive testing with concurrent workloads
  - Implement idempotency for all operations
  - Add distributed tracing (X-Ray)
  - Gradual rollout with feature flags
  - Monitor for race conditions

**Risk 6: Third-Party Service Outages**
- **Probability:** Low
- **Impact:** High
- **Mitigation:**
  - Implement circuit breakers
  - Graceful degradation (disable non-critical features)
  - Multi-region failover for critical services
  - Status page for transparency
  - SLA monitoring

### Business Risks

**Risk 1: User Adoption of Automated Features**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Comprehensive user training
  - In-app tutorials and tooltips
  - Beta testing with power users
  - Gather feedback early and often
  - Provide manual override options

**Risk 2: Accuracy Issues with AI Predictions**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Display confidence scores prominently
  - Allow users to provide feedback
  - Continuous model retraining
  - Human review for critical decisions
  - Clear disclaimers about AI limitations

**Risk 3: Competitive Pressure**
- **Probability:** High
- **Impact:** Medium
- **Mitigation:**
  - Focus on small firm niche
  - Build strong customer relationships
  - Rapid feature development
  - Patent key innovations
  - Build switching costs (data lock-in)

**Risk 4: Regulatory Compliance**
- **Probability:** Low
- **Impact:** Critical
- **Mitigation:**
  - Legal review of AI usage
  - GDPR/CCPA compliance from day 1
  - Regular security audits
  - SOC 2 certification (Phase 5)
  - Maintain detailed audit logs


## Cost Analysis Summary

### Monthly Infrastructure Costs by Phase

| Phase | Timeline | Monthly Cost | Cost per Doc* | Key Changes |
|-------|----------|--------------|---------------|-------------|
| Phase 1 | Current | $140-190 | $0.70-0.95 | Railway baseline |
| Phase 2 | Months 1-2 | $385-485 | $0.55-0.70 | AWS migration, auto-processing |
| Phase 3 | Months 3-4 | $830-1,030 | $0.42-0.52 | Parallel processing, batch |
| Phase 4 | Months 5-6 | $1,345-1,545 | $0.45-0.55 | Advanced features, Pinecone |
| Phase 5 | Months 7-12 | $2,500-2,900 | $0.35-0.40 | Enterprise scale, optimized |

*Based on 200 documents/month (Phase 1), 700 docs/month (Phase 2), 2000 docs/month (Phase 3-4), 7000 docs/month (Phase 5)

### Cost Breakdown by Service (Phase 5)

| Service | Monthly Cost | Percentage | Optimization Opportunity |
|---------|--------------|------------|--------------------------|
| AWS Bedrock | $800-1,200 | 32-41% | Model selection, caching |
| AWS ECS | $900 | 31% | Reserved capacity, spot instances |
| AWS RDS | $400 | 14% | Reserved instances |
| Pinecone | $200 | 7% | Optimize vector dimensions |
| AWS Redshift | $300 | 10% | Right-size cluster |
| Other AWS | $200-300 | 7-10% | Various optimizations |

### Revenue Projections

**Pricing Tiers:**
- **Solo Plan:** $299/month (1 attorney, 100 docs/month)
- **Litigation Plan:** $499/month (2-3 attorneys, 500 docs/month)
- **Professional Plan:** $599/month (Litigation + 50 contract comparisons)
- **Enterprise Plan:** Custom pricing (10+ attorneys, unlimited docs)

**Customer Acquisition Targets:**

| Phase | Timeline | Customers | MRR | Infrastructure Cost | Gross Margin |
|-------|----------|-----------|-----|---------------------|--------------|
| Phase 1 | Current | 10 (beta) | $0 | $190 | N/A |
| Phase 2 | Month 2 | 25 | $7,475 | $485 | 93.5% |
| Phase 3 | Month 4 | 50 | $14,950 | $1,030 | 93.1% |
| Phase 4 | Month 6 | 100 | $29,900 | $1,545 | 94.8% |
| Phase 5 | Month 12 | 200 | $59,800 | $2,900 | 95.1% |

**Break-Even Analysis:**
- Phase 2: 2 customers ($598 MRR) to cover infrastructure
- Phase 3: 4 customers ($1,196 MRR) to cover infrastructure
- Phase 4: 6 customers ($1,794 MRR) to cover infrastructure
- Phase 5: 10 customers ($2,990 MRR) to cover infrastructure

**Unit Economics (Phase 5):**
- Average Revenue Per User (ARPU): $299/month
- Cost Per User (infrastructure): $14.50/month
- Gross Margin: 95.1%
- Customer Lifetime Value (24 months): $7,176
- Customer Acquisition Cost (target): $1,500
- LTV:CAC Ratio: 4.8:1 (healthy)

### Funding Requirements

**Seed Round: $500K**

**Use of Funds:**
1. **Engineering (40% - $200K)**
   - 2 full-time engineers × 12 months
   - AWS infrastructure costs
   - Development tools and services

2. **Sales & Marketing (30% - $150K)**
   - 1 sales/marketing lead × 12 months
   - Marketing campaigns
   - Sales tools (CRM, email, etc.)
   - Conference attendance

3. **Operations (20% - $100K)**
   - 1 customer success manager × 12 months
   - Legal and compliance
   - Accounting and finance
   - Insurance

4. **Reserve (10% - $50K)**
   - Contingency fund
   - Unexpected costs

**Runway:** 18 months to reach $50K MRR and profitability

## Investor Presentation Summary

### The Problem

Small law firms (1-5 attorneys) spend **40% of their time** on document review and organization. Manual review is:
- **Slow:** 15 minutes per document
- **Expensive:** $200-400/hour attorney time
- **Error-prone:** 10-15% miss rate on critical documents
- **Unscalable:** Can't handle large discovery volumes

### Our Solution

CaseIntel is an **AI-powered document intelligence platform** that automatically:
- Classifies documents (95% accuracy)
- Detects privileged content (92% accuracy)
- Identifies hot documents (88% accuracy)
- Extracts timeline events
- Generates case narratives

**Result:** 70% reduction in document review time

### Market Opportunity

- **440,000 law firms** in the US
- **75% are small firms** (1-5 attorneys)
- **$300B legal tech market**
- Growing 10% annually
- **TAM:** $15B (small firm legal tech)
- **SAM:** $3B (document management)
- **SOM:** $150M (AI-powered analysis)

### Traction

**Current State (Phase 1):**
- ✅ Production-ready MVP
- ✅ 10 beta users actively testing
- ✅ 500+ documents processed
- ✅ 95% classification accuracy
- ✅ Positive user feedback

**12-Month Roadmap:**
- Phase 2: Automated workflows (Months 1-2)
- Phase 3: Parallel processing (Months 3-4)
- Phase 4: Advanced AI features (Months 5-6)
- Phase 5: Enterprise scale (Months 7-12)

### Competitive Advantage

1. **Purpose-built for small firms**
   - Affordable pricing ($299-599/month)
   - Easy to use (no training required)
   - Fast implementation (< 1 day)

2. **Latest AI technology**
   - AWS Bedrock (Claude 4.5)
   - Continuous model updates
   - No model training required

3. **Comprehensive solution**
   - Document analysis
   - Timeline generation
   - Privilege detection
   - Hot doc identification
   - Predictive analytics

4. **Strong unit economics**
   - 95% gross margin
   - LTV:CAC ratio of 4.8:1
   - Payback period < 5 months

### Financial Projections

| Metric | Month 2 | Month 6 | Month 12 | Month 24 |
|--------|---------|---------|----------|----------|
| Customers | 25 | 100 | 200 | 500 |
| MRR | $7.5K | $30K | $60K | $150K |
| ARR | $90K | $360K | $720K | $1.8M |
| Infrastructure | $485 | $1,545 | $2,900 | $5,000 |
| Gross Margin | 93.5% | 94.8% | 95.1% | 96.7% |

### The Ask

**Seeking:** $500K seed round

**Milestones:**
- Month 6: $30K MRR, 100 customers
- Month 12: $60K MRR, 200 customers
- Month 18: Break-even, profitable
- Month 24: $150K MRR, 500 customers

**Exit Strategy:**
- Acquisition by legal tech company (Clio, MyCase, etc.)
- Target valuation: $20-30M (10-15x ARR)
- Timeline: 3-5 years

### Team

**Current Team:**
- Founder/CEO: [Name] - [Background]
- CTO: [Name] - [Background]
- Lead Engineer: [Name] - [Background]

**Hiring Plan (with funding):**
- 2 Full-stack Engineers (Months 1-2)
- 1 Sales/Marketing Lead (Month 3)
- 1 Customer Success Manager (Month 6)

### Why Now?

1. **AI breakthrough:** Claude 4.5 enables accurate legal analysis
2. **Cloud infrastructure:** AWS Bedrock makes AI accessible
3. **Market timing:** Small firms adopting legal tech post-COVID
4. **Competitive gap:** No affordable AI solution for small firms
5. **Proven demand:** Beta users willing to pay

### Next Steps

1. **Close seed round** (Q1 2026)
2. **Launch Phase 2** (Q2 2026) - Automated workflows
3. **Reach 100 customers** (Q3 2026)
4. **Launch Phase 5** (Q4 2026) - Enterprise features
5. **Series A fundraise** (Q1 2027) - $3M at $15M valuation

---

## Appendix: Technical Specifications

### AWS Service Configurations

**ECS Task Definitions (Phase 5):**
```yaml
# Backend task definition
BackendTask:
  Family: caseintel-backend
  NetworkMode: awsvpc
  RequiresCompatibilities:
    - FARGATE
  Cpu: 1024  # 1 vCPU
  Memory: 2048  # 2 GB
  ContainerDefinitions:
    - Name: backend
      Image: !Sub ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/caseintel-backend:latest
      PortMappings:
        - ContainerPort: 3000
      Environment:
        - Name: NODE_ENV
          Value: production
        - Name: DATABASE_URL
          ValueFrom: !Ref DatabaseSecretArn
      LogConfiguration:
        LogDriver: awslogs
        Options:
          awslogs-group: /ecs/caseintel-backend
          awslogs-region: !Ref AWS::Region
          awslogs-stream-prefix: ecs

# Agents task definition
AgentsTask:
  Family: caseintel-agents
  NetworkMode: awsvpc
  RequiresCompatibilities:
    - FARGATE
  Cpu: 2048  # 2 vCPU
  Memory: 4096  # 4 GB
  ContainerDefinitions:
    - Name: agents
      Image: !Sub ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/caseintel-agents:latest
      PortMappings:
        - ContainerPort: 8000
      Environment:
        - Name: AWS_REGION
          Value: !Ref AWS::Region
        - Name: DATABASE_URL
          ValueFrom: !Ref DatabaseSecretArn
      LogConfiguration:
        LogDriver: awslogs
        Options:
          awslogs-group: /ecs/caseintel-agents
          awslogs-region: !Ref AWS::Region
          awslogs-stream-prefix: ecs
```

**Auto-Scaling Configuration:**
```yaml
# Backend auto-scaling
BackendAutoScaling:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    ServiceNamespace: ecs
    ResourceId: !Sub service/${ECSCluster}/${BackendService}
    ScalableDimension: ecs:service:DesiredCount
    MinCapacity: 2
    MaxCapacity: 10

BackendScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: caseintel-backend-scaling
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref BackendAutoScaling
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 70.0
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageCPUUtilization

# Agents auto-scaling (based on SQS queue depth)
AgentsAutoScaling:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    ServiceNamespace: ecs
    ResourceId: !Sub service/${ECSCluster}/${AgentsService}
    ScalableDimension: ecs:service:DesiredCount
    MinCapacity: 4
    MaxCapacity: 15

AgentsScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: caseintel-agents-scaling
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref AgentsAutoScaling
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 50.0
      CustomizedMetricSpecification:
        MetricName: ApproximateNumberOfMessagesVisible
        Namespace: AWS/SQS
        Statistic: Average
        Dimensions:
          - Name: QueueName
            Value: !GetAtt JobQueue.QueueName
```

### Database Migration Scripts

**Phase 2 Migration:**
```sql
-- Add webhook events table
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_webhook_events_processed ON webhook_events(processed, created_at);

-- Add active subscriptions table
CREATE TABLE active_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    subscription_type VARCHAR(50) NOT NULL,
    connection_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_active_subscriptions_user ON active_subscriptions(user_id);
CREATE INDEX idx_active_subscriptions_case ON active_subscriptions(case_id);
```

**Phase 3 Migration:**
```sql
-- Add batch jobs table
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    total_documents INTEGER NOT NULL,
    completed_documents INTEGER DEFAULT 0,
    failed_documents INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion_time TIMESTAMP
);

-- Add job queue table
CREATE TABLE job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batch_jobs(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_job_queue_status_priority ON job_queue(status, priority DESC, created_at);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status, created_at);
CREATE INDEX idx_batch_jobs_user ON batch_jobs(user_id, created_at DESC);
```

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Ready for Implementation

