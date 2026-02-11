# Backend Integration Guide - CaseIntel AI Agents

**Last Updated**: February 11, 2026  
**Agents API**: http://localhost:8000 (local) / https://your-agents-api.com (production)

---

## Quick Start Integration

### 1. When User Uploads Document

In your NestJS backend (`DocumentsService.upload`):

```typescript
// After document is uploaded to S3 and record created in DB
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

async uploadDocument(file, caseId, userId) {
  // 1. Upload to S3
  const s3Key = await this.s3Service.uploadFile(file);
  
  // 2. Create document record
  const document = await this.documentRepository.save({
    caseId,
    userId,
    originalFilename: file.originalname,
    storageKey: s3Key,
    mimeType: file.mimetype,
    sizeBytes: file.size,
    status: 'processing', // Start as processing
  });
  
  // 3. Trigger AI analysis (async - don't wait)
  this.triggerAIAnalysis(document.id, document.caseId).catch(err => {
    this.logger.error(`Failed to trigger AI analysis: ${err.message}`);
  });
  
  return document;
}

private async triggerAIAnalysis(documentId: string, caseId: string) {
  const agentsApiUrl = process.env.AGENTS_API_URL || 'http://localhost:8000';
  const apiKey = process.env.AGENTS_API_KEY;
  
  try {
    const response = await firstValueFrom(
      this.httpService.post(
        `${agentsApiUrl}/api/v1/analyze`,
        {
          document_id: documentId,
          case_id: caseId,
          callback_url: `${process.env.API_URL}/webhooks/agents/complete`,
        },
        {
          headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json',
          },
        }
      )
    );
    
    this.logger.log(`AI analysis queued: ${response.data.job_id}`);
    
    // Optionally store job_id in document record
    await this.documentRepository.update(documentId, {
      agentJobId: response.data.job_id,
    });
    
  } catch (error) {
    this.logger.error(`AI analysis request failed: ${error.message}`);
    // Don't fail the upload - just log the error
  }
}
```

---

## 2. Webhook Handler for Completion

Create a webhook endpoint to receive results:

```typescript
// src/modules/webhooks/webhooks.controller.ts

@Controller('webhooks/agents')
export class AgentsWebhookController {
  constructor(
    private readonly documentsService: DocumentsService,
    private readonly timelineService: TimelineService,
    private readonly notificationsService: NotificationsService,
  ) {}
  
  @Post('complete')
  async handleAnalysisComplete(@Body() payload: any) {
    const { job_id, case_id, status, results_summary } = payload;
    
    this.logger.log(`Received analysis completion for job ${job_id}`);
    
    // Find the document by job_id
    const document = await this.documentRepository.findOne({
      where: { agentJobId: job_id },
    });
    
    if (!document) {
      this.logger.warn(`Document not found for job ${job_id}`);
      return { status: 'ok' };
    }
    
    // Update document status
    await this.documentRepository.update(document.id, {
      status: 'ready',
      aiAnalysisComplete: true,
      aiAnalysisSummary: results_summary,
    });
    
    // If it's a hot doc, send notification
    if (results_summary?.is_hot_doc) {
      await this.notificationsService.sendHotDocAlert({
        caseId: case_id,
        documentId: document.id,
        score: results_summary.hot_doc_score,
        severity: results_summary.hot_doc_severity,
      });
    }
    
    return { status: 'ok', message: 'Webhook processed' };
  }
}
```

---

## 3. Fetching Analysis Results

Get full analysis results when user views document:

```typescript
// src/modules/documents/documents.service.ts

async getDocumentAnalysis(documentId: string, userId: string) {
  const document = await this.findDocumentWithPermissions(documentId, userId);
  
  if (!document.agentJobId) {
    throw new NotFoundException('Document has not been analyzed');
  }
  
  const agentsApiUrl = process.env.AGENTS_API_URL;
  const apiKey = process.env.AGENTS_API_KEY;
  
  try {
    const response = await firstValueFrom(
      this.httpService.get(
        `${agentsApiUrl}/api/v1/results/${document.agentJobId}`,
        {
          headers: { 'X-API-Key': apiKey },
        }
      )
    );
    
    return {
      document,
      analysis: response.data,
    };
    
  } catch (error) {
    if (error.response?.status === 404) {
      throw new NotFoundException('Analysis results not found');
    }
    throw error;
  }
}
```

---

## 4. GraphQL Schema Updates

Add these fields to your GraphQL schema:

```graphql
type Document {
  id: ID!
  # ... existing fields ...
  
  # AI Analysis fields
  aiAnalysisComplete: Boolean
  agentJobId: String
  aiAnalysisSummary: AnalysisSummary
  aiAnalysisResults: AnalysisResults
}

type AnalysisSummary {
  documentType: String
  confidence: Float
  isHotDoc: Boolean
  hotDocScore: Float
  hasPrivilegeIssues: Boolean
  summary: String
}

type AnalysisResults {
  documentType: String
  classificationConfidence: Float
  classificationReasoning: String
  
  # Metadata
  dates: [ExtractedDate!]
  people: [ExtractedPerson!]
  entities: [ExtractedEntity!]
  locations: [String!]
  
  # Privilege
  privilegeFlags: [String!]
  privilegeReasoning: String
  privilegeConfidence: Float
  privilegeRecommendation: String
  
  # Hot Doc
  isHotDoc: Boolean
  hotDocScore: Float
  hotDocSeverity: String
  hotDocFlags: [HotDocFlag!]
  
  # Content
  summary: String
  keyFacts: [String!]
  legalIssues: [String!]
  draftNarrative: String
  evidenceGaps: [String!]
  
  # Cross-Reference
  relatedDocuments: [RelatedDocument!]
  timelineEvents: [TimelineEvent!]
  witnessMentions: [WitnessMention!]
  consistencyFlags: [ConsistencyFlag!]
}

type HotDocFlag {
  type: String!
  excerpt: String!
  reasoning: String!
  impact: String
  page: Int
}

type ExtractedDate {
  date: String!
  context: String
  significance: String
}

type ExtractedPerson {
  name: String!
  role: String
  mentions: Int
}

type ExtractedEntity {
  name: String!
  type: String
}

# Queries
extend type Query {
  documentAnalysis(documentId: ID!): AnalysisResults
  caseHotDocs(caseId: ID!): [Document!]
  casePrivilegedDocs(caseId: ID!): [Document!]
}
```

---

## 5. GraphQL Resolvers

```typescript
// src/modules/documents/documents.resolver.ts

@Query(() => AnalysisResults, { nullable: true })
async documentAnalysis(
  @Args('documentId') documentId: string,
  @CurrentUser() user: User,
) {
  return this.documentsService.getDocumentAnalysis(documentId, user.id);
}

@Query(() => [Document])
async caseHotDocs(
  @Args('caseId') caseId: string,
  @CurrentUser() user: User,
) {
  // Query from analysis_results table where is_hot_doc = true
  return this.documentsService.getCaseHotDocs(caseId, user.id);
}

@Query(() => [Document])
async casePrivilegedDocs(
  @Args('caseId') caseId: string,
  @CurrentUser() user: User,
) {
  // Query from analysis_results where privilege_flags is not empty
  return this.documentsService.getCasePrivilegedDocs(caseId, user.id);
}
```

---

## 6. Environment Variables

Add to your backend `.env`:

```env
# AI Agents Service
AGENTS_API_URL=http://localhost:8000
AGENTS_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6

# Production (update when deployed)
# AGENTS_API_URL=https://agents.caseintel.io
```

---

## 7. Database Schema Migration

The agents service uses these tables (already created in your DB):

```sql
-- Analysis Jobs (tracks processing status)
CREATE TABLE analysis_jobs (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    case_id UUID REFERENCES cases(id),
    status VARCHAR(50),
    current_agent VARCHAR(100),
    progress_percent INT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analysis Results (stores all agent outputs)
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES analysis_jobs(id),
    document_id UUID REFERENCES documents(id),
    case_id UUID REFERENCES cases(id),
    
    -- Classification
    document_type VARCHAR(50),
    classification_confidence FLOAT,
    classification_reasoning TEXT,
    document_sub_type VARCHAR(50),
    
    -- Metadata
    document_metadata JSONB,
    
    -- Privilege
    privilege_flags TEXT[],
    privilege_reasoning TEXT,
    privilege_confidence FLOAT,
    privilege_recommendation VARCHAR(50),
    
    -- Hot Doc
    is_hot_doc BOOLEAN,
    hot_doc_score FLOAT,
    hot_doc_severity VARCHAR(20),
    hot_doc_data JSONB,
    
    -- Content
    summary TEXT,
    key_facts TEXT[],
    legal_issues TEXT[],
    draft_narrative TEXT,
    evidence_gaps TEXT[],
    
    -- Cross-Reference
    cross_references JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Timeline Events (auto-generated from documents)
CREATE TABLE agent_timeline_events (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    document_id UUID REFERENCES documents(id),
    event_date DATE,
    event_description TEXT,
    source_page INT,
    significance TEXT,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Witness Mentions (tracks witness appearances)
CREATE TABLE witness_mentions (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    document_id UUID REFERENCES documents(id),
    witness_name VARCHAR(255),
    role VARCHAR(100),
    context TEXT,
    page_number INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. Frontend Integration

### Display Analysis Results

```typescript
// In your document viewer component
const { data } = useQuery(DOCUMENT_ANALYSIS_QUERY, {
  variables: { documentId }
});

const analysis = data?.documentAnalysis;

return (
  <div>
    {/* Hot Doc Alert */}
    {analysis?.isHotDoc && (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>🔥 Hot Document - {analysis.hotDocSeverity?.toUpperCase()}</AlertTitle>
        <AlertDescription>
          Score: {(analysis.hotDocScore * 100).toFixed(0)}% - 
          This document contains critical evidence requiring immediate attorney review.
        </AlertDescription>
      </Alert>
    )}
    
    {/* Privilege Warning */}
    {analysis?.privilegeFlags?.length > 0 && (
      <Alert variant="warning">
        <Lock className="h-4 w-4" />
        <AlertTitle>🔒 Privilege Issues Detected</AlertTitle>
        <AlertDescription>
          {analysis.privilegeRecommendation === 'likely_privileged' 
            ? 'This document likely contains privileged content. Review required.'
            : 'This document may contain privileged content.'}
        </AlertDescription>
      </Alert>
    )}
    
    {/* Summary */}
    <Card>
      <CardHeader>
        <CardTitle>AI Analysis Summary</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{analysis?.summary}</p>
        
        {/* Key Facts */}
        <h3>Key Facts</h3>
        <ul>
          {analysis?.keyFacts?.map((fact, i) => (
            <li key={i}>{fact}</li>
          ))}
        </ul>
        
        {/* Legal Issues */}
        {analysis?.legalIssues?.length > 0 && (
          <>
            <h3>Legal Issues</h3>
            <ul>
              {analysis.legalIssues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </>
        )}
      </CardContent>
    </Card>
  </div>
);
```

---

## 9. API Endpoints Reference

### Analyze Document

```bash
POST /api/v1/analyze
Headers:
  Content-Type: application/json
  X-API-Key: <your-api-key>

Body:
{
  "document_id": "uuid",        # Required: Your document UUID
  "case_id": "uuid",            # Required: Case UUID
  "document_url": "https://...", # Optional: S3 URL (or use document_text)
  "document_text": "...",       # Optional: Raw text for testing
  "callback_url": "https://..."  # Optional: Webhook URL
}

Response:
{
  "job_id": "uuid",
  "status": "queued",
  "message": "Document analysis queued successfully"
}
```

### Check Status

```bash
GET /api/v1/status/{job_id}
Headers:
  X-API-Key: <your-api-key>

Response:
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress_percent": 75,
  "current_agent": "HotDocDetector",
  "started_at": "2026-02-11T14:52:41Z",
  "completed_at": null
}
```

### Get Results

```bash
GET /api/v1/results/{job_id}
Headers:
  X-API-Key: <your-api-key>

Response:
{
  "job_id": "uuid",
  "document_id": "uuid",
  "case_id": "uuid",
  "status": "completed",
  
  "classification": {
    "document_type": "email",
    "confidence": 0.95,
    "reasoning": "...",
    "sub_type": "internal_communication"
  },
  
  "metadata": {
    "dates": [...],
    "people": [...],
    "entities": [...],
    "locations": [...]
  },
  
  "privilege": {
    "flags": ["confidential"],
    "confidence": 0.70,
    "reasoning": "...",
    "recommendation": "review_required"
  },
  
  "hot_doc": {
    "is_hot": true,
    "score": 0.95,
    "severity": "critical",
    "flags": [
      {
        "type": "smoking_gun",
        "excerpt": "...",
        "reasoning": "...",
        "impact": "..."
      }
    ]
  },
  
  "content": {
    "summary": "...",
    "key_facts": [...],
    "legal_issues": [...],
    "draft_narrative": "...",
    "evidence_gaps": [...]
  },
  
  "cross_references": {
    "related_documents": [...],
    "timeline_events": [...],
    "witness_mentions": [...],
    "consistency_flags": [...]
  }
}
```

---

## 10. Error Handling

```typescript
async getAnalysisResults(jobId: string) {
  try {
    const response = await this.agentsHttpService.get(`/results/${jobId}`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      throw new NotFoundException('Analysis not found or still processing');
    }
    if (error.response?.status === 500) {
      throw new InternalServerErrorException('Analysis failed');
    }
    throw error;
  }
}
```

---

## 11. Auto-Sync Timeline Events

Automatically create timeline events from agent analysis:

```typescript
async syncTimelineFromAgents(caseId: string) {
  // Query agent_timeline_events table
  const agentEvents = await this.db.query(`
    SELECT event_date, event_description, source_page, significance, document_id
    FROM agent_timeline_events
    WHERE case_id = $1
    AND NOT EXISTS (
      SELECT 1 FROM timeline_events te 
      WHERE te.agent_event_id = agent_timeline_events.id
    )
    ORDER BY event_date
  `, [caseId]);
  
  // Create timeline events in main table
  for (const event of agentEvents) {
    await this.timelineRepository.save({
      caseId,
      eventDate: event.event_date,
      title: event.event_description.substring(0, 100),
      description: event.event_description,
      importance: event.significance === 'high' ? 5 : 3,
      aiGenerated: true,
      verified: false,
      sourceDocumentId: event.document_id,
    });
  }
}
```

---

## 12. Dashboard Widgets

### Hot Docs Summary

```graphql
query CaseHotDocs($caseId: ID!) {
  caseHotDocs(caseId: $caseId) {
    id
    originalFilename
    uploadedAt
    aiAnalysisSummary {
      hotDocScore
      hotDocSeverity
      summary
    }
  }
}
```

### Privilege Risk Documents

```graphql
query CasePrivilegedDocs($caseId: ID!) {
  casePrivilegedDocs(caseId: $caseId) {
    id
    originalFilename
    uploadedAt
    aiAnalysisSummary {
      privilegeFlags
      privilegeRecommendation
    }
  }
}
```

---

## 13. Monitoring & Alerts

### Track AI Processing

```typescript
// Add to your DocumentsModule
@Cron('*/5 * * * *') // Every 5 minutes
async checkPendingAnalyses() {
  const pending = await this.documentRepository.find({
    where: { 
      status: 'processing',
      agentJobId: Not(IsNull()),
      createdAt: LessThan(new Date(Date.now() - 10 * 60 * 1000)) // > 10 min
    }
  });
  
  for (const doc of pending) {
    // Check status from agents API
    const status = await this.checkAgentJobStatus(doc.agentJobId);
    
    if (status.status === 'completed') {
      doc.status = 'ready';
      doc.aiAnalysisComplete = true;
    } else if (status.status === 'failed') {
      doc.status = 'ready'; // Still mark as ready even if analysis failed
      doc.aiAnalysisFailed = true;
    }
    
    await this.documentRepository.save(doc);
  }
}
```

---

## 14. Testing Integration

### Local Development

```bash
# 1. Start agents service
cd /Users/ryan/WIXEN/CaseIntel/agents
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Start backend
cd /Users/ryan/WIXEN/CaseIntel/backend/caseintel-backend
npm run start:dev

# 3. Upload a test document
# The backend should automatically trigger AI analysis
```

### Verify Integration

```bash
# Check if job was created
psql -h localhost -p 5433 -U caseintel -d caseintel \
  -c "SELECT id, status, current_agent FROM analysis_jobs ORDER BY created_at DESC LIMIT 5;"

# Check if results were stored
psql -h localhost -p 5433 -U caseintel -d caseintel \
  -c "SELECT job_id, document_type, is_hot_doc FROM analysis_results ORDER BY created_at DESC LIMIT 5;"
```

---

## 15. Production Deployment

### Deploy Agents Service

```bash
# Option 1: Railway
railway up

# Option 2: Docker
docker build -t caseintel-agents .
docker push your-registry/caseintel-agents:latest

# Option 3: AWS ECS
# Use the Dockerfile and deploy to ECS cluster
```

### Update Backend Environment

```env
# Production
AGENTS_API_URL=https://agents-api.caseintel.io
AGENTS_API_KEY=<production-key>
```

---

## Cost Monitoring Query

Add this to your admin dashboard:

```typescript
async getAICostEstimate(startDate: Date, endDate: Date) {
  const jobs = await this.db.query(`
    SELECT 
      DATE(created_at) as date,
      COUNT(*) as documents_analyzed,
      COUNT(*) * 0.16 as estimated_cost
    FROM analysis_jobs
    WHERE status = 'completed'
    AND created_at BETWEEN $1 AND $2
    GROUP BY DATE(created_at)
    ORDER BY date DESC
  `, [startDate, endDate]);
  
  const total = jobs.reduce((sum, row) => sum + row.estimated_cost, 0);
  
  return {
    daily_breakdown: jobs,
    total_cost: total,
    total_documents: jobs.reduce((sum, row) => sum + row.documents_analyzed, 0),
  };
}
```

---

## Quick Integration Checklist

- [ ] Add AGENTS_API_URL and AGENTS_API_KEY to backend `.env`
- [ ] Install `@nestjs/axios` in backend
- [ ] Create webhook endpoint `/webhooks/agents/complete`
- [ ] Add `agentJobId` column to `documents` table
- [ ] Call agents API after document upload
- [ ] Update GraphQL schema with analysis fields
- [ ] Add resolvers for `documentAnalysis` query
- [ ] Create UI components to display hot doc alerts
- [ ] Add privilege warnings in document viewer
- [ ] Test end-to-end with real document upload

---

**Estimated Integration Time**: 2-3 hours for basic integration, 1 day for full UI/UX polish

**Next Step**: Add the webhook endpoint and test document upload flow!
