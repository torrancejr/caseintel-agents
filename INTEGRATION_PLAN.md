# CaseIntel Agents Integration Plan

## Current State ✅

The Python agents system is now fully functional locally with:
- 6 AI agents working in pipeline (classifier, metadata, privilege, hotdoc, content, cross-reference)
- API endpoints for document analysis, status checking, and results retrieval
- Case-level aggregation (timeline, witnesses)
- Database integration with existing CaseIntel schema
- Local testing verified and working

## Integration Phases

### Phase 1: Backend Integration (NestJS → Python Agents)

**Goal**: Connect existing NestJS backend to Python agents API

#### 1.1 Document Upload Flow
**Current**: Documents uploaded → stored in S3 → classification service
**New**: Documents uploaded → stored in S3 → **trigger Python agents** → store results

**Changes Needed**:
```typescript
// backend/caseintel-backend/src/documents/documents.service.ts

async processDocument(documentId: string) {
  const document = await this.findOne(documentId);
  
  // Call Python agents API
  const response = await axios.post(
    `${PYTHON_AGENTS_URL}/api/v1/analyze`,
    {
      document_url: document.s3Url,
      case_id: document.caseId,
      document_id: documentId,
      callback_url: `${BACKEND_URL}/webhooks/analysis-complete`
    },
    {
      headers: { 'X-API-Key': AGENTS_API_KEY }
    }
  );
  
  // Store job_id for tracking
  await this.updateAnalysisJob(documentId, response.data.job_id);
}
```

#### 1.2 Webhook Handler
**New endpoint** to receive completion notifications from Python agents:

```typescript
// backend/caseintel-backend/src/webhooks/webhooks.controller.ts

@Post('analysis-complete')
async handleAnalysisComplete(@Body() payload: AnalysisWebhook) {
  const { job_id, case_id, status } = payload;
  
  if (status === 'completed') {
    // Fetch full results from Python API
    const results = await this.agentsService.getResults(job_id);
    
    // Update document with classification
    await this.documentsService.updateClassification(results);
    
    // Store hot doc flags
    if (results.hot_doc.is_hot_doc) {
      await this.notificationsService.sendHotDocAlert(results);
    }
    
    // Update case timeline
    await this.timelineService.addEvents(results.timeline_events);
    
    // Update witness map
    await this.witnessesService.addMentions(results.witness_mentions);
  }
}
```

#### 1.3 Environment Variables
```bash
# backend/caseintel-backend/.env
PYTHON_AGENTS_URL=http://localhost:8000  # Local dev
# PYTHON_AGENTS_URL=https://agents.caseintel.io  # Production
AGENTS_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
```

---

### Phase 2: Frontend Integration (React → Display Results)

**Goal**: Show agent analysis results in the UI

#### 2.1 Document Detail Page Enhancements

**Add new sections**:

1. **AI Analysis Status**
   - Show progress bar while agents are running
   - Display which agent is currently processing
   - Show completion status

2. **Classification Results**
   - Document type badge (correspondence, contract, etc.)
   - Confidence score
   - Sub-type information

3. **Privilege Analysis**
   - Privilege flags (attorney-client, work product, confidential)
   - Recommendation badge (clearly_privileged, needs_review, not_privileged)
   - Confidence score
   - Reasoning explanation

4. **Hot Document Alert**
   - 🔥 Hot doc badge if flagged
   - Severity indicator (critical, high, medium, low)
   - Score display
   - Key excerpts that triggered the flag
   - Impact assessment

5. **Metadata Extraction**
   - Timeline of dates extracted
   - People mentioned (with roles)
   - Entities identified
   - Locations

6. **Content Analysis**
   - AI-generated summary
   - Key facts list
   - Legal issues identified
   - Draft narrative
   - Evidence gaps

7. **Cross-References**
   - Related documents
   - Witness appearances across documents
   - Consistency flags

#### 2.2 Case Dashboard Enhancements

**New widgets**:

1. **Hot Documents Feed**
   - List of all hot docs in the case
   - Sorted by severity/score
   - Quick preview of why flagged

2. **Case Timeline** (Enhanced)
   - Auto-populated from agent extractions
   - Events from all documents
   - Filterable by significance

3. **Witness Map**
   - All witnesses mentioned across documents
   - Shows which documents they appear in
   - Highlights inconsistencies

4. **Privilege Dashboard**
   - Count of privileged vs non-privileged docs
   - Documents needing review
   - Confidence distribution

#### 2.3 API Integration

```typescript
// frontend/src/services/agentsApi.ts

export const agentsApi = {
  // Get analysis status
  async getStatus(jobId: string) {
    return axios.get(`/api/agents/status/${jobId}`);
  },
  
  // Get full results
  async getResults(jobId: string) {
    return axios.get(`/api/agents/results/${jobId}`);
  },
  
  // Get case timeline
  async getCaseTimeline(caseId: string) {
    return axios.get(`/api/agents/case/${caseId}/timeline`);
  },
  
  // Get case witnesses
  async getCaseWitnesses(caseId: string) {
    return axios.get(`/api/agents/case/${caseId}/witnesses`);
  },
  
  // Ask AI a question
  async askQuestion(caseId: string, question: string) {
    return axios.post(`/api/agents/ask`, { case_id: caseId, question });
  }
};
```

---

### Phase 3: Narrative Workflow Integration

**Goal**: Use agent analysis to enhance narrative generation

#### 3.1 Current Narrative Flow
```
User selects documents → Manual review → Write narrative
```

#### 3.2 Enhanced Narrative Flow
```
User selects documents → **AI pre-analysis** → Draft narrative → User edits → Final narrative
```

**Changes**:

1. **Auto-populate narrative sections** from agent analysis:
   - Use `draft_narrative` from content analyzer
   - Use `key_facts` for facts section
   - Use `legal_issues` for issues section
   - Use `timeline_events` for chronology

2. **Evidence gaps** → Suggestions for additional discovery

3. **Cross-references** → Automatic citation of supporting documents

#### 3.3 Implementation

```typescript
// backend/src/narratives/narratives.service.ts

async generateNarrativeDraft(documentIds: string[]) {
  // Get agent analysis for all documents
  const analyses = await Promise.all(
    documentIds.map(id => this.agentsService.getAnalysisForDocument(id))
  );
  
  // Combine into narrative structure
  return {
    summary: this.combineSum maries(analyses),
    chronology: this.buildChronology(analyses),
    keyFacts: this.extractKeyFacts(analyses),
    legalIssues: this.identifyLegalIssues(analyses),
    evidenceGaps: this.identifyGaps(analyses),
    citations: this.buildCitations(analyses)
  };
}
```

---

### Phase 4: Opposition Analysis Integration

**Goal**: Use agent analysis to identify weaknesses and counter-arguments

#### 4.1 Enhanced Opposition Analysis

**New features**:

1. **Automatic weakness detection**
   - Use `consistency_flags` to find contradictions
   - Use `evidence_gaps` to identify missing support
   - Use `hot_doc` analysis to find damaging evidence

2. **Counter-argument generation**
   - Use RAG to find supporting documents
   - Use `legal_issues` to identify defenses
   - Use `cross_references` to find contradictory evidence

3. **Witness credibility analysis**
   - Track witness statements across documents
   - Flag inconsistencies automatically
   - Suggest deposition questions

#### 4.2 Implementation

```typescript
// backend/src/opposition/opposition.service.ts

async analyzeOpposition(caseId: string) {
  // Get all agent analyses for the case
  const timeline = await this.agentsService.getCaseTimeline(caseId);
  const witnesses = await this.agentsService.getCaseWitnesses(caseId);
  const hotDocs = await this.agentsService.getHotDocuments(caseId);
  
  return {
    weaknesses: this.identifyWeaknesses(timeline, witnesses),
    contradictions: this.findContradictions(witnesses),
    missingEvidence: this.identifyGaps(timeline),
    counterArguments: await this.generateCounterArguments(hotDocs),
    depositionQuestions: this.suggestQuestions(witnesses)
  };
}
```

---

### Phase 5: Contract Analysis Integration

**Goal**: Extend agents to handle contract-specific analysis

#### 5.1 New Contract-Specific Agents

**Add specialized agents**:

1. **Clause Extractor**
   - Identify standard clauses (indemnification, limitation of liability, etc.)
   - Extract key terms (dates, amounts, parties)
   - Flag unusual or risky clauses

2. **Obligation Tracker**
   - Extract all obligations for each party
   - Identify deadlines and conditions
   - Flag potential breaches

3. **Risk Analyzer**
   - Identify high-risk clauses
   - Compare against standard terms
   - Suggest modifications

4. **Contract Comparer**
   - Compare multiple versions
   - Highlight changes
   - Identify material modifications

#### 5.2 Implementation

```python
# agents/src/agents/contract_analyzer.py

class ContractAnalyzer(BaseAgent):
    async def analyze(self, state: dict) -> dict:
        contract_text = state["raw_text"]
        
        # Extract clauses
        clauses = await self.extract_clauses(contract_text)
        
        # Identify obligations
        obligations = await self.extract_obligations(contract_text)
        
        # Analyze risks
        risks = await self.analyze_risks(clauses)
        
        return {
            **state,
            "clauses": clauses,
            "obligations": obligations,
            "risks": risks,
            "contract_type": self.classify_contract(contract_text)
        }
```

---

## Deployment Strategy

### Local Development (Current)
- Python agents: `localhost:8000`
- NestJS backend: `localhost:3000`
- React frontend: `localhost:5173`

### Staging
- Python agents: Railway (separate service)
- NestJS backend: Railway (existing)
- React frontend: Vercel (existing)

### Production
- Python agents: AWS Lambda + API Gateway (future)
- NestJS backend: Railway (existing)
- React frontend: Vercel (existing)

---

## Migration Path

### Week 1: Backend Integration
- [ ] Add Python agents API client to NestJS
- [ ] Implement webhook handler
- [ ] Update document upload flow
- [ ] Test with existing documents

### Week 2: Frontend Integration
- [ ] Add agent status display
- [ ] Show classification results
- [ ] Display hot doc alerts
- [ ] Add case timeline widget

### Week 3: Narrative Integration
- [ ] Auto-populate narrative drafts
- [ ] Add evidence gap suggestions
- [ ] Implement citation system

### Week 4: Opposition & Contract
- [ ] Add opposition analysis features
- [ ] Implement contract-specific agents
- [ ] Test end-to-end workflows

---

## API Compatibility

### Existing Backend APIs (Keep)
- Document upload/download
- Case management
- User authentication
- Billing/subscriptions

### New Agent APIs (Add)
- `/api/agents/analyze` - Trigger analysis
- `/api/agents/status/:jobId` - Check progress
- `/api/agents/results/:jobId` - Get results
- `/api/agents/case/:caseId/timeline` - Case timeline
- `/api/agents/case/:caseId/witnesses` - Witness map
- `/api/agents/ask` - RAG Q&A

### Proxy Pattern (Recommended)
NestJS backend proxies all agent requests:
```
Frontend → NestJS → Python Agents
```

Benefits:
- Single authentication point
- Consistent error handling
- Request logging
- Rate limiting
- Easier to swap agent backend later

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Prioritize features** - What to build first?
3. **Set timeline** - When to ship each phase?
4. **Assign tasks** - Who builds what?

Ready to start Phase 1 (Backend Integration)?
