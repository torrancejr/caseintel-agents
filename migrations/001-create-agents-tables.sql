-- ============================================================================
-- CaseIntel AI Agents - Database Migration
-- ============================================================================
-- This migration creates tables for the AI agents system that integrate
-- with the existing CaseIntel backend schema.
--
-- IMPORTANT: This assumes the backend tables already exist:
-- - cases
-- - documents
-- - classifications
-- - users
-- - firms
--
-- Run this migration AFTER the backend database is set up.
-- ============================================================================

-- ============================================================================
-- 1. ANALYSIS JOBS TABLE
-- ============================================================================
-- Tracks AI agent pipeline execution for each document
-- Links to backend 'documents' table via document_id

CREATE TABLE IF NOT EXISTS analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys to backend tables
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Job status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    -- Status values: queued, processing, completed, failed, cancelled
    
    current_agent VARCHAR(100),
    -- Current agent: classifier, metadata, privilege, hotdoc, content, crossref
    
    progress_percent INTEGER NOT NULL DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Error handling
    error_message TEXT,
    error_stack TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_analysis_jobs_document ON analysis_jobs(document_id);
CREATE INDEX idx_analysis_jobs_case ON analysis_jobs(case_id);
CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_analysis_jobs_created ON analysis_jobs(created_at DESC);

-- ============================================================================
-- 2. ANALYSIS RESULTS TABLE
-- ============================================================================
-- Stores complete AI agent analysis results
-- Complements the backend 'classifications' table with additional agent data

CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    job_id UUID NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Agent 1: Document Classifier
    document_type VARCHAR(100),
    -- Types: email, contract, memo, pleading, deposition, correspondence, etc.
    
    document_sub_type VARCHAR(100),
    classification_confidence FLOAT,
    classification_reasoning TEXT,
    
    -- Agent 2: Metadata Extractor (JSONB for flexibility)
    metadata JSONB,
    -- Structure: {
    --   dates: [{date, type, context}],
    --   people: [{name, role, organization}],
    --   entities: [{name, type, mentions}],
    --   locations: [{name, type, context}],
    --   subjects: [string],
    --   authors: [string]
    -- }
    
    -- Agent 3: Privilege Checker
    privilege_flags JSONB,
    -- Array: ["attorney_client", "work_product", "settlement_negotiation", etc.]
    
    privilege_reasoning TEXT,
    privilege_confidence FLOAT,
    privilege_recommendation VARCHAR(50),
    -- Recommendations: privileged, not_privileged, needs_review, redact_portions
    
    -- Agent 4: Hot Doc Detector
    is_hot_doc BOOLEAN NOT NULL DEFAULT FALSE,
    hot_doc_score FLOAT,
    hot_doc_severity VARCHAR(20),
    -- Severity: critical, high, medium, low
    
    hot_doc_data JSONB,
    -- Structure: {
    --   flags: ["smoking_gun", "contradicts_testimony", "damages_evidence"],
    --   reasons: [string],
    --   key_passages: [{text, page, significance}]
    -- }
    
    -- Agent 5: Content Analyzer
    summary TEXT,
    key_facts JSONB,
    -- Array of strings: ["fact1", "fact2", ...]
    
    legal_issues JSONB,
    -- Array: [{issue, description, relevant_facts, importance}]
    
    draft_narrative TEXT,
    evidence_gaps JSONB,
    -- Array: [{gap, importance, suggested_action}]
    
    -- Agent 6: Cross-Reference Engine
    cross_references JSONB,
    -- Structure: {
    --   related_docs: [{doc_id, relationship, relevance}],
    --   timeline_events: [{date, event, significance}],
    --   witnesses: [{name, role, mentions}],
    --   contradictions: [{doc_id, issue, severity}]
    -- }
    
    -- Model tracking
    models_used JSONB,
    -- Structure: {
    --   classifier: "model_id",
    --   metadata: "model_id",
    --   privilege: "model_id",
    --   hotdoc: "model_id",
    --   content: "model_id",
    --   crossref: "model_id"
    -- }
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_analysis_results_job ON analysis_results(job_id);
CREATE INDEX idx_analysis_results_document ON analysis_results(document_id);
CREATE INDEX idx_analysis_results_case ON analysis_results(case_id);
CREATE INDEX idx_analysis_results_hot_doc ON analysis_results(is_hot_doc) WHERE is_hot_doc = TRUE;
CREATE INDEX idx_analysis_results_doc_type ON analysis_results(document_type);
CREATE INDEX idx_analysis_results_created ON analysis_results(created_at DESC);

-- GIN indexes for JSONB columns (for efficient querying)
CREATE INDEX idx_analysis_results_metadata ON analysis_results USING GIN (metadata);
CREATE INDEX idx_analysis_results_privilege_flags ON analysis_results USING GIN (privilege_flags);
CREATE INDEX idx_analysis_results_hot_doc_data ON analysis_results USING GIN (hot_doc_data);
CREATE INDEX idx_analysis_results_cross_refs ON analysis_results USING GIN (cross_references);

-- ============================================================================
-- 3. TIMELINE EVENTS TABLE
-- ============================================================================
-- Extracted timeline events from documents
-- Complements backend 'timeline_events' table if it exists

CREATE TABLE IF NOT EXISTS agent_timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    
    -- Event data
    event_date DATE NOT NULL,
    event_description TEXT NOT NULL,
    event_type VARCHAR(100),
    -- Types: filing, communication, transaction, meeting, deadline, etc.
    
    source_page INTEGER,
    source_text TEXT,
    
    -- Significance
    significance VARCHAR(20),
    -- Values: critical, important, notable, minor
    
    confidence FLOAT,
    
    -- Metadata
    created_by VARCHAR(50) NOT NULL DEFAULT 'agent',
    -- Values: agent, user, system
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_agent_timeline_case ON agent_timeline_events(case_id);
CREATE INDEX idx_agent_timeline_document ON agent_timeline_events(document_id);
CREATE INDEX idx_agent_timeline_date ON agent_timeline_events(event_date);
CREATE INDEX idx_agent_timeline_case_date ON agent_timeline_events(case_id, event_date);
CREATE INDEX idx_agent_timeline_significance ON agent_timeline_events(significance);

-- ============================================================================
-- 4. WITNESS MENTIONS TABLE
-- ============================================================================
-- Tracks witness mentions across documents for consistency analysis

CREATE TABLE IF NOT EXISTS witness_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    
    -- Witness data
    witness_name VARCHAR(500) NOT NULL,
    normalized_name VARCHAR(500),
    -- Normalized for matching (lowercase, no punctuation)
    
    role VARCHAR(100),
    -- Roles: plaintiff, defendant, witness, expert, attorney, etc.
    
    organization VARCHAR(500),
    
    -- Context
    context TEXT,
    page_number INTEGER,
    mention_type VARCHAR(50),
    -- Types: direct_quote, paraphrase, reference, signature, etc.
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_witness_mentions_case ON witness_mentions(case_id);
CREATE INDEX idx_witness_mentions_document ON witness_mentions(document_id);
CREATE INDEX idx_witness_mentions_name ON witness_mentions(witness_name);
CREATE INDEX idx_witness_mentions_normalized ON witness_mentions(normalized_name);
CREATE INDEX idx_witness_mentions_case_name ON witness_mentions(case_id, normalized_name);

-- ============================================================================
-- 5. AGENT EXECUTION LOGS TABLE
-- ============================================================================
-- Detailed logs of agent execution for debugging and monitoring

CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    job_id UUID NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
    
    -- Agent info
    agent_name VARCHAR(100) NOT NULL,
    -- Names: classifier, metadata, privilege, hotdoc, content, crossref
    
    -- Execution details
    status VARCHAR(50) NOT NULL,
    -- Status: started, completed, failed, skipped
    
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Model info
    model_id VARCHAR(200),
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    
    -- Input/Output
    input_summary TEXT,
    output_summary TEXT,
    
    -- Error handling
    error_message TEXT,
    error_type VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_agent_logs_job ON agent_execution_logs(job_id);
CREATE INDEX idx_agent_logs_agent ON agent_execution_logs(agent_name);
CREATE INDEX idx_agent_logs_status ON agent_execution_logs(status);
CREATE INDEX idx_agent_logs_created ON agent_execution_logs(created_at DESC);

-- ============================================================================
-- 6. UPDATE TRIGGERS
-- ============================================================================
-- Automatically update updated_at timestamps

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analysis_jobs_updated_at
    BEFORE UPDATE ON analysis_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at
    BEFORE UPDATE ON analysis_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_timeline_events_updated_at
    BEFORE UPDATE ON agent_timeline_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Complete document analysis with backend classification
CREATE OR REPLACE VIEW v_document_analysis AS
SELECT 
    d.id AS document_id,
    d.original_filename,
    d.case_id,
    d.status AS document_status,
    d.uploaded_at,
    
    -- Analysis job info
    aj.id AS job_id,
    aj.status AS analysis_status,
    aj.progress_percent,
    aj.started_at AS analysis_started,
    aj.completed_at AS analysis_completed,
    
    -- Backend classification
    c.privilege AS backend_privilege,
    c.privilege_type AS backend_privilege_type,
    c.privilege_confidence AS backend_privilege_confidence,
    c.relevance_score AS backend_relevance_score,
    
    -- Agent analysis results
    ar.document_type,
    ar.classification_confidence,
    ar.is_hot_doc,
    ar.hot_doc_score,
    ar.hot_doc_severity,
    ar.privilege_recommendation,
    ar.summary,
    ar.metadata,
    ar.cross_references
    
FROM documents d
LEFT JOIN analysis_jobs aj ON d.id = aj.document_id
LEFT JOIN analysis_results ar ON aj.id = ar.job_id
LEFT JOIN classifications c ON d.id = c.document_id
ORDER BY d.uploaded_at DESC;

-- View: Hot documents summary
CREATE OR REPLACE VIEW v_hot_documents AS
SELECT 
    d.id AS document_id,
    d.original_filename,
    d.case_id,
    c.title AS case_title,
    ar.hot_doc_score,
    ar.hot_doc_severity,
    ar.hot_doc_data,
    ar.summary,
    ar.created_at AS analyzed_at
FROM documents d
JOIN cases c ON d.case_id = c.id
JOIN analysis_jobs aj ON d.id = aj.document_id
JOIN analysis_results ar ON aj.id = ar.job_id
WHERE ar.is_hot_doc = TRUE
ORDER BY ar.hot_doc_score DESC, ar.created_at DESC;

-- View: Privilege analysis summary
CREATE OR REPLACE VIEW v_privilege_analysis AS
SELECT 
    d.id AS document_id,
    d.original_filename,
    d.case_id,
    c.title AS case_title,
    
    -- Backend classification
    cl.privilege AS backend_privilege,
    cl.privilege_type AS backend_privilege_type,
    cl.privilege_confidence AS backend_confidence,
    cl.review_status,
    
    -- Agent analysis
    ar.privilege_flags AS agent_privilege_flags,
    ar.privilege_confidence AS agent_confidence,
    ar.privilege_recommendation,
    ar.privilege_reasoning,
    
    ar.created_at AS analyzed_at
FROM documents d
JOIN cases c ON d.case_id = c.id
LEFT JOIN classifications cl ON d.id = cl.document_id
LEFT JOIN analysis_jobs aj ON d.id = aj.document_id
LEFT JOIN analysis_results ar ON aj.id = ar.job_id
WHERE cl.privilege != 'unclassified' OR ar.privilege_flags IS NOT NULL
ORDER BY ar.created_at DESC;

-- ============================================================================
-- 8. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE analysis_jobs IS 'Tracks AI agent pipeline execution for document analysis';
COMMENT ON TABLE analysis_results IS 'Stores complete AI agent analysis results for documents';
COMMENT ON TABLE agent_timeline_events IS 'Timeline events extracted by AI agents from documents';
COMMENT ON TABLE witness_mentions IS 'Witness mentions tracked across documents for consistency analysis';
COMMENT ON TABLE agent_execution_logs IS 'Detailed execution logs for AI agents (debugging and monitoring)';

COMMENT ON COLUMN analysis_jobs.status IS 'Job status: queued, processing, completed, failed, cancelled';
COMMENT ON COLUMN analysis_jobs.current_agent IS 'Currently executing agent: classifier, metadata, privilege, hotdoc, content, crossref';
COMMENT ON COLUMN analysis_results.is_hot_doc IS 'Whether document is flagged as a hot document (case-critical)';
COMMENT ON COLUMN analysis_results.hot_doc_severity IS 'Hot document severity: critical, high, medium, low';
COMMENT ON COLUMN analysis_results.privilege_recommendation IS 'Privilege recommendation: privileged, not_privileged, needs_review, redact_portions';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verify tables were created
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN (
    'analysis_jobs',
    'analysis_results',
    'agent_timeline_events',
    'witness_mentions',
    'agent_execution_logs'
)
ORDER BY table_name;

-- Expected output: 5 tables with their column counts
