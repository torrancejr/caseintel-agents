"""
Pipeline state definitions for LangGraph workflow.
Defines the shared state object that flows through each agent node.
"""
from typing import TypedDict, Optional
from enum import Enum


class DocumentType(str, Enum):
    """Legal document type classifications."""
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
    """Privilege and confidentiality classifications."""
    ATTORNEY_CLIENT = "attorney_client"
    WORK_PRODUCT = "work_product"
    CONFIDENTIAL = "confidential"
    NONE = "none"


class PipelineState(TypedDict):
    """
    Shared state object that flows through the agent pipeline.
    Each agent reads from and writes to specific fields.
    """
    # Input fields
    document_url: str
    case_id: str
    job_id: str
    raw_text: str

    # Agent 1 output: Document Classifier
    document_type: Optional[DocumentType]
    classification_confidence: Optional[float]
    classification_reasoning: Optional[str]
    document_sub_type: Optional[str]

    # Agent 2 output: Metadata Extractor
    dates: Optional[list[dict]]           # [{date, context, source_page}]
    people: Optional[list[dict]]          # [{name, role, context, mentions, first_appearance}]
    entities: Optional[list[dict]]        # [{name, type, role}]
    locations: Optional[list[dict]]       # [{name, context}]

    # Agent 3 output: Privilege Checker
    privilege_flags: Optional[list[PrivilegeFlag]]
    privilege_reasoning: Optional[str]
    privilege_confidence: Optional[float]
    privileged_excerpts: Optional[list[dict]]  # [{text, type, page}]
    privilege_recommendation: Optional[str]

    # Agent 4 output: Hot Doc Detector
    is_hot_doc: Optional[bool]
    hot_doc_reasons: Optional[list[dict]]  # [{type, excerpt, reasoning, page}]
    hot_doc_score: Optional[float]         # 0.0 - 1.0
    hot_doc_severity: Optional[str]        # "critical", "high", "medium"

    # Agent 5 output: Content Analyzer
    summary: Optional[str]
    key_facts: Optional[list[str]]
    legal_issues: Optional[list[str]]
    draft_narrative: Optional[str]
    evidence_gaps: Optional[list[str]]

    # Agent 6 output: Cross-Reference Engine
    related_documents: Optional[list[dict]]    # [{doc_id, title, relevance, relationship}]
    timeline_events: Optional[list[dict]]      # [{date, event, source_doc, source_page}]
    witness_mentions: Optional[list[dict]]     # [{name, appearances: [{doc_id, context, page}]}]
    consistency_flags: Optional[list[dict]]    # [{witness, issue}]

    # Pipeline metadata
    status: str                                # "processing", "completed", "failed"
    current_agent: Optional[str]
    progress_percent: int
    errors: list[dict]                         # [{agent, error, timestamp}]
