"""
LangGraph workflow orchestration for the document analysis pipeline.
Coordinates all 6 agents in sequence.
"""
from langgraph.graph import StateGraph, END
from src.workflows.state import PipelineState
from src.agents.classifier import DocumentClassifier
from src.agents.metadata_extractor import MetadataExtractor
from src.agents.privilege_checker import PrivilegeChecker
from src.agents.hot_doc_detector import HotDocDetector
from src.agents.content_analyzer import ContentAnalyzer
from src.agents.cross_reference import CrossReferenceEngine
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# Agent instances (singleton pattern)
_classifier = None
_metadata_extractor = None
_privilege_checker = None
_hot_doc_detector = None
_content_analyzer = None
_cross_reference_engine = None


def get_agents(rag_retriever=None):
    """
    Get or create agent instances.
    
    Args:
        rag_retriever: Optional RAG retriever for cross-reference engine
        
    Returns:
        tuple: All agent instances
    """
    global _classifier, _metadata_extractor, _privilege_checker
    global _hot_doc_detector, _content_analyzer, _cross_reference_engine
    
    if _classifier is None:
        _classifier = DocumentClassifier()
    if _metadata_extractor is None:
        _metadata_extractor = MetadataExtractor()
    if _privilege_checker is None:
        _privilege_checker = PrivilegeChecker()
    if _hot_doc_detector is None:
        _hot_doc_detector = HotDocDetector()
    if _content_analyzer is None:
        _content_analyzer = ContentAnalyzer()
    if _cross_reference_engine is None:
        _cross_reference_engine = CrossReferenceEngine(rag_retriever=rag_retriever)
    
    return (
        _classifier,
        _metadata_extractor,
        _privilege_checker,
        _hot_doc_detector,
        _content_analyzer,
        _cross_reference_engine
    )


def classify_document(state: PipelineState) -> PipelineState:
    """
    Agent 1: Classify the document type.
    """
    try:
        logger.info(f"[{state['job_id']}] Starting Agent 1: Document Classifier")
        state["current_agent"] = "DocumentClassifier"
        state["progress_percent"] = 5
        
        classifier, *_ = get_agents()
        result = classifier.run(state)
        
        # Update state with results
        state.update(result)
        state["progress_percent"] = 15
        
        logger.info(
            f"[{state['job_id']}] Agent 1 complete: "
            f"{state.get('document_type')} (confidence: {state.get('classification_confidence', 0):.2f})"
        )
        return state
        
    except Exception as e:
        logger.error(f"[{state['job_id']}] Agent 1 failed: {str(e)}")
        state["errors"].append({
            "agent": "DocumentClassifier",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        return state


def extract_metadata(state: PipelineState) -> PipelineState:
    """
    Agent 2: Extract metadata (dates, people, entities, locations).
    """
    try:
        logger.info(f"[{state['job_id']}] Starting Agent 2: Metadata Extractor")
        state["current_agent"] = "MetadataExtractor"
        state["progress_percent"] = 20
        
        _, metadata_extractor, *_ = get_agents()
        result = metadata_extractor.run(state)
        
        state.update(result)
        state["progress_percent"] = 35
        
        logger.info(
            f"[{state['job_id']}] Agent 2 complete: "
            f"{len(state.get('dates', []))} dates, {len(state.get('people', []))} people"
        )
        return state
        
    except Exception as e:
        logger.error(f"[{state['job_id']}] Agent 2 failed: {str(e)}")
        state["errors"].append({
            "agent": "MetadataExtractor",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        return state


def check_privilege(state: PipelineState) -> PipelineState:
    """
    Agent 3: Check for privilege and confidentiality issues.
    """
    try:
        logger.info(f"[{state['job_id']}] Starting Agent 3: Privilege Checker")
        state["current_agent"] = "PrivilegeChecker"
        state["progress_percent"] = 40
        
        _, _, privilege_checker, *_ = get_agents()
        result = privilege_checker.run(state)
        
        state.update(result)
        state["progress_percent"] = 50
        
        logger.info(
            f"[{state['job_id']}] Agent 3 complete: "
            f"flags={state.get('privilege_flags', [])}"
        )
        return state
        
    except Exception as e:
        logger.error(f"[{state['job_id']}] Agent 3 failed: {str(e)}")
        state["errors"].append({
            "agent": "PrivilegeChecker",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        return state


def detect_hot_docs(state: PipelineState) -> PipelineState:
    """
    Agent 4: Detect hot documents.
    """
    try:
        logger.info(f"[{state['job_id']}] Starting Agent 4: Hot Doc Detector")
        state["current_agent"] = "HotDocDetector"
        state["progress_percent"] = 55
        
        _, _, _, hot_doc_detector, *_ = get_agents()
        result = hot_doc_detector.run(state)
        
        state.update(result)
        state["progress_percent"] = 65
        
        logger.info(
            f"[{state['job_id']}] Agent 4 complete: "
            f"is_hot={state.get('is_hot_doc', False)}, score={state.get('hot_doc_score', 0):.2f}"
        )
        return state
        
    except Exception as e:
        logger.error(f"[{state['job_id']}] Agent 4 failed: {str(e)}")
        state["errors"].append({
            "agent": "HotDocDetector",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        return state


def analyze_content(state: PipelineState) -> PipelineState:
    """
    Agent 5: Analyze content and generate narratives.
    """
    try:
        logger.info(f"[{state['job_id']}] Starting Agent 5: Content Analyzer")
        state["current_agent"] = "ContentAnalyzer"
        state["progress_percent"] = 70
        
        _, _, _, _, content_analyzer, _ = get_agents()
        result = content_analyzer.run(state)
        
        state.update(result)
        state["progress_percent"] = 80
        
        logger.info(
            f"[{state['job_id']}] Agent 5 complete: "
            f"{len(state.get('key_facts', []))} key facts, "
            f"{len(state.get('legal_issues', []))} legal issues"
        )
        return state
        
    except Exception as e:
        logger.error(f"[{state['job_id']}] Agent 5 failed: {str(e)}")
        state["errors"].append({
            "agent": "ContentAnalyzer",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        return state


def cross_reference(state: PipelineState) -> PipelineState:
    """
    Agent 6: Cross-reference with other documents.
    """
    try:
        logger.info(f"[{state['job_id']}] Starting Agent 6: Cross-Reference Engine")
        state["current_agent"] = "CrossReferenceEngine"
        state["progress_percent"] = 85
        
        *_, cross_reference_engine = get_agents()
        result = cross_reference_engine.run(state)
        
        state.update(result)
        state["progress_percent"] = 100
        state["status"] = "completed"
        state["current_agent"] = None
        
        logger.info(
            f"[{state['job_id']}] Agent 6 complete: "
            f"{len(state.get('timeline_events', []))} timeline events, "
            f"{len(state.get('witness_mentions', []))} witnesses"
        )
        logger.info(f"[{state['job_id']}] Pipeline completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{state['job_id']}] Agent 6 failed: {str(e)}")
        state["errors"].append({
            "agent": "CrossReferenceEngine",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        state["status"] = "completed"  # Complete even with errors
        state["progress_percent"] = 100
        return state


def build_pipeline(rag_retriever=None):
    """
    Build and compile the LangGraph workflow.
    
    Args:
        rag_retriever: Optional RAG retriever for Agent 6
        
    Returns:
        Compiled LangGraph workflow
    """
    # Initialize agents with RAG retriever
    get_agents(rag_retriever=rag_retriever)
    
    # Create workflow graph
    workflow = StateGraph(PipelineState)
    
    # Add agent nodes
    workflow.add_node("classify", classify_document)
    workflow.add_node("extract_metadata", extract_metadata)
    workflow.add_node("check_privilege", check_privilege)
    workflow.add_node("detect_hot_docs", detect_hot_docs)
    workflow.add_node("analyze_content", analyze_content)
    workflow.add_node("cross_reference", cross_reference)
    
    # Define edges — sequential pipeline
    # Phase 1: Sequential execution for simplicity and debuggability
    # Phase 2 can parallelize agents 2, 3, 4 since they're independent
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract_metadata")
    workflow.add_edge("extract_metadata", "check_privilege")
    workflow.add_edge("check_privilege", "detect_hot_docs")
    workflow.add_edge("detect_hot_docs", "analyze_content")
    workflow.add_edge("analyze_content", "cross_reference")
    workflow.add_edge("cross_reference", END)
    
    logger.info("Pipeline workflow built successfully")
    return workflow.compile()


async def run_pipeline(
    document_url: str,
    case_id: str,
    job_id: str,
    raw_text: str,
    rag_retriever=None
) -> PipelineState:
    """
    Run the complete document analysis pipeline.
    
    Args:
        document_url: URL of the document
        case_id: Case identifier
        job_id: Job identifier
        raw_text: Extracted document text
        rag_retriever: Optional RAG retriever
        
    Returns:
        Final pipeline state with all agent outputs
    """
    logger.info(f"Starting pipeline for job {job_id}")
    
    # Initialize state
    initial_state: PipelineState = {
        "document_url": document_url,
        "case_id": case_id,
        "job_id": job_id,
        "raw_text": raw_text,
        "status": "processing",
        "current_agent": None,
        "progress_percent": 0,
        "errors": [],
        # All other fields will be populated by agents
        "document_type": None,
        "classification_confidence": None,
        "classification_reasoning": None,
        "document_sub_type": None,
        "dates": None,
        "people": None,
        "entities": None,
        "locations": None,
        "privilege_flags": None,
        "privilege_reasoning": None,
        "privilege_confidence": None,
        "privileged_excerpts": None,
        "privilege_recommendation": None,
        "is_hot_doc": None,
        "hot_doc_reasons": None,
        "hot_doc_score": None,
        "hot_doc_severity": None,
        "summary": None,
        "key_facts": None,
        "legal_issues": None,
        "draft_narrative": None,
        "evidence_gaps": None,
        "related_documents": None,
        "timeline_events": None,
        "witness_mentions": None,
        "consistency_flags": None
    }
    
    # Build and run pipeline
    pipeline = build_pipeline(rag_retriever=rag_retriever)
    
    try:
        final_state = pipeline.invoke(initial_state)
        logger.info(f"Pipeline completed for job {job_id}")
        return final_state
    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
        initial_state["status"] = "failed"
        initial_state["errors"].append({
            "agent": "Pipeline",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        return initial_state
