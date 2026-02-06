"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type classifications."""
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


class JobStatus(str, Enum):
    """Job status values."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Schemas

class AnalyzeRequest(BaseModel):
    """Request to analyze a document."""
    document_url: str = Field(..., description="S3 presigned URL or direct URL to document")
    case_id: str = Field(..., description="Case identifier")
    callback_url: Optional[str] = Field(None, description="Webhook URL for completion notification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_url": "https://s3.amazonaws.com/caseintel-documents/cases/case123/doc456.pdf",
                "case_id": "case123",
                "callback_url": "https://caseintel.io/api/webhooks/analysis-complete"
            }
        }


class AskAIRequest(BaseModel):
    """Request to ask AI a question about case documents."""
    case_id: str = Field(..., description="Case identifier")
    question: str = Field(..., description="Question to ask about the case documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case123",
                "question": "What evidence do we have of prior knowledge of the defect?"
            }
        }


# Response Schemas

class AnalyzeResponse(BaseModel):
    """Response after submitting a document for analysis."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Human-readable status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "queued",
                "message": "Document analysis queued successfully"
            }
        }


class StatusResponse(BaseModel):
    """Response for job status check."""
    job_id: str
    status: JobStatus
    current_agent: Optional[str] = None
    progress_percent: int = Field(..., ge=0, le=100)
    agents_completed: List[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "current_agent": "MetadataExtractor",
                "progress_percent": 35,
                "agents_completed": ["DocumentClassifier"],
                "started_at": "2024-01-15T10:30:00Z",
                "completed_at": None,
                "errors": []
            }
        }


class ClassificationResult(BaseModel):
    """Document classification results."""
    document_type: DocumentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    sub_type: Optional[str] = None


class MetadataResult(BaseModel):
    """Metadata extraction results."""
    dates: List[Dict[str, Any]]
    people: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    locations: List[Dict[str, Any]]


class PrivilegeResult(BaseModel):
    """Privilege checking results."""
    flags: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    recommendation: str
    excerpts: List[Dict[str, Any]] = Field(default_factory=list)


class HotDocResult(BaseModel):
    """Hot document detection results."""
    is_hot_doc: bool
    score: float = Field(..., ge=0.0, le=1.0)
    severity: str
    flags: List[Dict[str, Any]] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Content analysis results."""
    summary: str
    key_facts: List[str]
    legal_issues: List[Dict[str, Any]]
    draft_narrative: str
    evidence_gaps: List[Dict[str, Any]] = Field(default_factory=list)


class CrossReferenceResult(BaseModel):
    """Cross-reference results."""
    related_documents: List[Dict[str, Any]]
    timeline_events: List[Dict[str, Any]]
    witness_mentions: List[Dict[str, Any]]
    consistency_flags: List[Dict[str, Any]] = Field(default_factory=list)


class ResultsResponse(BaseModel):
    """Complete analysis results."""
    job_id: str
    case_id: str
    status: JobStatus
    
    # Agent outputs
    classification: Optional[ClassificationResult] = None
    metadata: Optional[MetadataResult] = None
    privilege: Optional[PrivilegeResult] = None
    hot_doc: Optional[HotDocResult] = None
    analysis: Optional[AnalysisResult] = None
    cross_references: Optional[CrossReferenceResult] = None
    
    # Metadata
    started_at: datetime
    completed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)


class TimelineResponse(BaseModel):
    """Timeline events for a case."""
    case_id: str
    events: List[Dict[str, Any]]
    total_count: int


class WitnessResponse(BaseModel):
    """Witness map for a case."""
    case_id: str
    witnesses: List[Dict[str, Any]]
    total_count: int


class AskAIResponse(BaseModel):
    """Response to an AI question."""
    question: str
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid API key",
                "detail": "The provided API key is not valid",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
