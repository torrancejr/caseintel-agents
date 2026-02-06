"""
SQLAlchemy database models for storing analysis results.
Integrates with existing CaseIntel backend schema.
"""
from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ForeignKey, Date, Boolean, Numeric, create_engine
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker
import uuid
import os

Base = declarative_base()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://caseintel:caseintel_dev@localhost:5433/caseintel")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AnalysisJob(Base):
    """
    Tracks AI agent pipeline execution for each document.
    Links to backend 'documents' and 'cases' tables.
    """
    __tablename__ = "analysis_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys to backend tables
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Job status tracking
    status = Column(String(50), default="queued", nullable=False)  # queued, processing, completed, failed, cancelled
    current_agent = Column(String(100), nullable=True)  # classifier, metadata, privilege, hotdoc, content, crossref
    progress_percent = Column(Integer, default=0, nullable=False)
    
    # Timing
    started_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_stack = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, document_id={self.document_id}, status={self.status})>"


class AnalysisResult(Base):
    """
    Stores complete AI agent analysis results for a document.
    Complements the backend 'classifications' table with additional agent data.
    """
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent 1: Document Classifier
    document_type = Column(String(100), nullable=True)  # email, contract, memo, pleading, etc.
    document_sub_type = Column(String(100), nullable=True)
    classification_confidence = Column(Float, nullable=True)
    classification_reasoning = Column(Text, nullable=True)
    
    # Agent 2: Metadata Extractor (JSONB for flexibility)
    document_metadata = Column("metadata", JSONB, nullable=True)
    # Structure: {dates: [], people: [], entities: [], locations: [], subjects: [], authors: []}
    
    # Agent 3: Privilege Checker
    privilege_flags = Column(JSONB, nullable=True)  # ["attorney_client", "work_product", etc.]
    privilege_reasoning = Column(Text, nullable=True)
    privilege_confidence = Column(Float, nullable=True)
    privilege_recommendation = Column(String(50), nullable=True)  # privileged, not_privileged, needs_review
    
    # Agent 4: Hot Doc Detector
    is_hot_doc = Column(Boolean, default=False, nullable=False, index=True)
    hot_doc_score = Column(Float, nullable=True)
    hot_doc_severity = Column(String(20), nullable=True)  # critical, high, medium, low
    hot_doc_data = Column(JSONB, nullable=True)  # {flags: [], reasons: [], key_passages: []}
    
    # Agent 5: Content Analyzer
    summary = Column(Text, nullable=True)
    key_facts = Column(JSONB, nullable=True)  # ["fact1", "fact2", ...]
    legal_issues = Column(JSONB, nullable=True)  # [{issue, description, relevant_facts, importance}]
    draft_narrative = Column(Text, nullable=True)
    evidence_gaps = Column(JSONB, nullable=True)  # [{gap, importance, suggested_action}]
    
    # Agent 6: Cross-Reference Engine
    cross_references = Column(JSONB, nullable=True)
    # Structure: {related_docs: [], timeline_events: [], witnesses: [], contradictions: []}
    
    # Model tracking
    models_used = Column(JSONB, nullable=True)
    # Structure: {classifier: "model_id", metadata: "model_id", ...}
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, document_id={self.document_id}, document_type={self.document_type})>"


class AgentTimelineEvent(Base):
    """
    Timeline events extracted by AI agents from documents.
    Named 'agent_timeline_events' to avoid conflicts with backend 'timeline_events' table.
    """
    __tablename__ = "agent_timeline_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Event data
    event_date = Column(Date, nullable=False, index=True)
    event_description = Column(Text, nullable=False)
    event_type = Column(String(100), nullable=True)  # filing, communication, transaction, meeting, etc.
    
    source_page = Column(Integer, nullable=True)
    source_text = Column(Text, nullable=True)
    
    # Significance
    significance = Column(String(20), nullable=True, index=True)  # critical, important, notable, minor
    confidence = Column(Float, nullable=True)
    
    # Metadata
    created_by = Column(String(50), default="agent", nullable=False)  # agent, user, system
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AgentTimelineEvent(id={self.id}, case_id={self.case_id}, event_date={self.event_date})>"


class WitnessMention(Base):
    """
    Tracks witness mentions across all documents in a case.
    Enables witness consistency analysis.
    """
    __tablename__ = "witness_mentions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Witness data
    witness_name = Column(String(500), nullable=False, index=True)
    normalized_name = Column(String(500), nullable=True, index=True)  # For matching
    role = Column(String(100), nullable=True)  # plaintiff, defendant, witness, expert, attorney
    organization = Column(String(500), nullable=True)
    
    # Context
    context = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    mention_type = Column(String(50), nullable=True)  # direct_quote, paraphrase, reference, signature
    
    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<WitnessMention(id={self.id}, witness_name={self.witness_name}, case_id={self.case_id})>"


class AgentExecutionLog(Base):
    """
    Detailed logs of agent execution for debugging and monitoring.
    Tracks individual agent performance, costs, and errors.
    """
    __tablename__ = "agent_execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent info
    agent_name = Column(String(100), nullable=False, index=True)  # classifier, metadata, privilege, etc.
    
    # Execution details
    status = Column(String(50), nullable=False, index=True)  # started, completed, failed, skipped
    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Model info
    model_id = Column(String(200), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(10, 6), nullable=True)
    
    # Input/Output
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AgentExecutionLog(id={self.id}, agent_name={self.agent_name}, status={self.status})>"
