"""
SQLAlchemy database models for storing analysis results.
"""
from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ForeignKey, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class AnalysisJob(Base):
    """
    Tracks pipeline execution for each document analysis.
    """
    __tablename__ = "analysis_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), nullable=False, index=True)
    document_url = Column(Text, nullable=False)
    status = Column(String(50), default="queued", nullable=False)  # queued, processing, completed, failed
    current_agent = Column(String(100), nullable=True)
    progress_percent = Column(Integer, default=0, nullable=False)
    started_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, case_id={self.case_id}, status={self.status})>"


class AnalysisResult(Base):
    """
    Stores the complete output from all agents for a document.
    """
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    case_id = Column(String(255), nullable=False, index=True)
    
    # Agent 1: Classification
    document_type = Column(String(100), nullable=True)
    classification_confidence = Column(Float, nullable=True)
    classification_reasoning = Column(Text, nullable=True)
    document_sub_type = Column(String(100), nullable=True)
    
    # Agent 2: Metadata (stored as JSONB for flexibility)
    metadata = Column(JSONB, nullable=True)  # {dates: [], people: [], entities: [], locations: []}
    
    # Agent 3: Privilege
    privilege_flags = Column(JSONB, nullable=True)  # ["attorney_client", "work_product", etc.]
    privilege_reasoning = Column(Text, nullable=True)
    privilege_confidence = Column(Float, nullable=True)
    privilege_recommendation = Column(String(50), nullable=True)
    
    # Agent 4: Hot Doc
    is_hot_doc = Column(Boolean, default=False, nullable=False)
    hot_doc_score = Column(Float, nullable=True)
    hot_doc_severity = Column(String(20), nullable=True)
    hot_doc_data = Column(JSONB, nullable=True)  # {flags: [], reasons: []}
    
    # Agent 5: Content Analysis
    summary = Column(Text, nullable=True)
    key_facts = Column(JSONB, nullable=True)  # ["fact1", "fact2", ...]
    legal_issues = Column(JSONB, nullable=True)  # [{issue, description, relevant_facts}, ...]
    draft_narrative = Column(Text, nullable=True)
    evidence_gaps = Column(JSONB, nullable=True)  # [{gap, importance, suggested_action}, ...]
    
    # Agent 6: Cross-references
    cross_references = Column(JSONB, nullable=True)  # {related_docs: [], timeline: [], witnesses: []}
    
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, job_id={self.job_id}, document_type={self.document_type})>"


class TimelineEvent(Base):
    """
    Individual timeline events extracted from documents.
    Denormalized for efficient timeline queries.
    """
    __tablename__ = "timeline_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    event_description = Column(Text, nullable=False)
    source_document_id = Column(UUID(as_uuid=True), nullable=True)
    source_page = Column(Integer, nullable=True)
    significance = Column(String(20), nullable=True)  # critical, important, notable
    created_by = Column(String(50), default="agent", nullable=False)  # 'agent' or 'user'
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<TimelineEvent(id={self.id}, case_id={self.case_id}, date={self.date})>"


class WitnessMention(Base):
    """
    Tracks witness mentions across all documents in a case.
    Enables witness consistency analysis.
    """
    __tablename__ = "witness_mentions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), nullable=False, index=True)
    witness_name = Column(String(500), nullable=False, index=True)
    role = Column(String(100), nullable=True)
    document_id = Column(UUID(as_uuid=True), nullable=True)
    context = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<WitnessMention(id={self.id}, witness_name={self.witness_name}, case_id={self.case_id})>"


# Indexes for performance
# These would be created via Alembic migrations in production
"""
CREATE INDEX idx_jobs_case ON analysis_jobs(case_id);
CREATE INDEX idx_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_results_case ON analysis_results(case_id);
CREATE INDEX idx_results_job ON analysis_results(job_id);
CREATE INDEX idx_results_hot_doc ON analysis_results(is_hot_doc) WHERE is_hot_doc = true;
CREATE INDEX idx_timeline_case_date ON timeline_events(case_id, date);
CREATE INDEX idx_witness_case ON witness_mentions(case_id, witness_name);
"""
