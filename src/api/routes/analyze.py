"""
Document analysis endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.models.schemas import AnalyzeRequest, AnalyzeResponse, AskAIRequest, AskAIResponse
from src.models.database import AnalysisJob, AnalysisResult, AgentTimelineEvent, WitnessMention
from src.api.dependencies import verify_api_key, get_db_session
from src.workflows.discovery_pipeline import run_pipeline
from src.services.s3 import s3_service
from src.services.notifications import notification_service
from src.rag.chunking import document_chunker
from src.rag.embeddings import vector_store
from src.rag.retrieval import rag_retriever
import uuid
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"], dependencies=[Depends(verify_api_key)])


async def process_document_pipeline(
    job_id: str,
    document_id: str,
    document_url: str,
    case_id: str,
    callback_url: str = None,
    document_text: str = None
):
    """
    Background task to process document through the pipeline.
    
    Args:
        job_id: Job identifier
        document_id: Document ID from database
        document_url: Document URL (optional if document_text provided)
        case_id: Case identifier
        callback_url: Optional webhook URL
        document_text: Raw document text (optional, for local testing)
    """
    from src.services.db import get_db_context
    
    try:
        logger.info(f"Starting pipeline processing for job {job_id}")
        
        # Create database session for background task
        with get_db_context() as db:
            # Update job status
            job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
            if job:
                job.status = "processing"
                job.started_at = datetime.utcnow()
                db.commit()
        
        # Get document text
        if document_text:
            # Use provided text directly (local testing)
            logger.info(f"Using provided document text ({len(document_text)} characters)")
            raw_text = document_text
        else:
            # Download document from URL
            logger.info(f"Downloading document from {document_url}")
            document_content = s3_service.download_from_url(document_url)
            
            # Extract text (placeholder - in production, use proper PDF/DOCX extraction)
            # TODO: Implement proper document text extraction
            raw_text = document_content.decode("utf-8", errors="ignore")
        
        # Run pipeline
        final_state = await run_pipeline(
            document_url=document_url,
            case_id=case_id,
            job_id=job_id,
            raw_text=raw_text,
            rag_retriever=rag_retriever
        )
        
        # Store results in database
        with get_db_context() as db:
            # Extract document type value (handle enum)
            doc_type = final_state.get("document_type")
            if hasattr(doc_type, 'value'):
                doc_type_str = doc_type.value
            else:
                doc_type_str = str(doc_type).replace("DocumentType.", "").lower()
            
            result = AnalysisResult(
                job_id=job_id,
                document_id=document_id,
                case_id=case_id,
                document_type=doc_type_str,
                classification_confidence=final_state.get("classification_confidence"),
                classification_reasoning=final_state.get("classification_reasoning"),
                document_sub_type=final_state.get("document_sub_type"),
                document_metadata={
                    "dates": final_state.get("dates", []),
                    "people": final_state.get("people", []),
                    "entities": final_state.get("entities", []),
                    "locations": final_state.get("locations", [])
                },
                privilege_flags=final_state.get("privilege_flags"),
                privilege_reasoning=final_state.get("privilege_reasoning"),
                privilege_confidence=final_state.get("privilege_confidence"),
                privilege_recommendation=final_state.get("privilege_recommendation"),
                is_hot_doc=final_state.get("is_hot_doc", False),
                hot_doc_score=final_state.get("hot_doc_score"),
                hot_doc_severity=final_state.get("hot_doc_severity"),
                hot_doc_data={
                    "flags": final_state.get("hot_doc_reasons", [])
                },
                summary=final_state.get("summary"),
                key_facts=final_state.get("key_facts"),
                legal_issues=final_state.get("legal_issues"),
                draft_narrative=final_state.get("draft_narrative"),
                evidence_gaps=final_state.get("evidence_gaps"),
                cross_references={
                    "related_docs": final_state.get("related_documents", []),
                    "timeline": final_state.get("timeline_events", []),
                    "witnesses": final_state.get("witness_mentions", []),
                    "consistency_flags": final_state.get("consistency_flags", [])
                }
            )
            db.add(result)
            
            # Store timeline events
            for event in final_state.get("timeline_events", []):
                timeline_event = AgentTimelineEvent(
                    case_id=case_id,
                    document_id=document_id,
                    event_date=event.get("date"),
                    event_description=event.get("event"),
                    source_page=event.get("source_page"),
                    significance=event.get("significance"),
                    created_by="agent"
                )
                db.add(timeline_event)
            
            # Store witness mentions
            for witness in final_state.get("witness_mentions", []):
                for appearance in witness.get("appearances", []):
                    mention = WitnessMention(
                        case_id=case_id,
                        document_id=document_id,
                        witness_name=witness.get("name"),
                        role=witness.get("role"),
                        context=appearance.get("context"),
                        page_number=appearance.get("page")
                    )
                    db.add(mention)
            
            # Update job status
            job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
            if job:
                job.status = "completed"
                job.completed_at = datetime.utcnow()
                job.progress_percent = 100
                job.current_agent = None
            
            db.commit()
        
        # Add to vector store for RAG
        if raw_text and final_state.get("document_type"):
            chunks = document_chunker.chunk_document(
                text=raw_text,
                document_type=str(final_state.get("document_type")),
                document_id=job_id,
                case_id=case_id
            )
            vector_store.add_document_chunks(case_id=case_id, chunks=chunks)
        
        # Send completion notification
        if callback_url:
            await notification_service.send_completion_notification(
                callback_url=callback_url,
                job_id=job_id,
                case_id=case_id,
                status="completed",
                results_summary={
                    "document_type": str(final_state.get("document_type")),
                    "is_hot_doc": final_state.get("is_hot_doc", False),
                    "hot_doc_score": final_state.get("hot_doc_score", 0.0)
                }
            )
        
        # Send hot doc alert if applicable
        if final_state.get("is_hot_doc") and callback_url:
            await notification_service.send_hot_doc_alert(
                callback_url=callback_url,
                job_id=job_id,
                case_id=case_id,
                hot_doc_score=final_state.get("hot_doc_score", 0.0),
                severity=final_state.get("hot_doc_severity", "medium"),
                summary=final_state.get("summary", "")[:200]
            )
        
        logger.info(f"Pipeline processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Pipeline processing failed for job {job_id}: {str(e)}")
        
        # Update job with error
        from src.services.db import get_db_context
        with get_db_context() as db:
            job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        
        # Send failure notification
        if callback_url:
            await notification_service.send_completion_notification(
                callback_url=callback_url,
                job_id=job_id,
                case_id=case_id,
                status="failed"
            )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """
    Submit a document for analysis.
    Returns immediately with a job ID. Processing happens in the background.
    """
    try:
        # Validate request
        if not request.document_url and not request.document_text:
            raise HTTPException(
                status_code=400,
                detail="Either document_url or document_text must be provided"
            )
        
        # Use provided document_id or generate a placeholder
        document_id = request.document_id or str(uuid.uuid4())
        
        # For local testing with document_text, we may not have a document record
        # The foreign key constraint will be handled by the database
        # In production, the backend creates the document record first
        
        # Create job record
        job_id = str(uuid.uuid4())
        job = AnalysisJob(
            id=job_id,
            document_id=document_id,
            case_id=request.case_id,
            status="queued",
            progress_percent=0
        )
        db.add(job)
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            # If foreign key constraint fails, it means document doesn't exist
            # For local testing, we'll create a minimal document record
            if "foreign key constraint" in str(e).lower() or "violates foreign key" in str(e).lower():
                logger.warning(f"Document {document_id} not found, this is expected for local testing")
                # Re-raise with helpful message
                raise HTTPException(
                    status_code=400,
                    detail=f"Document {document_id} does not exist. For local testing, ensure the case exists in the database."
                )
            raise
        
        logger.info(f"Created analysis job {job_id} for case {request.case_id}")
        
        # Add background task
        background_tasks.add_task(
            process_document_pipeline,
            job_id=job_id,
            document_id=document_id,
            document_url=request.document_url,
            case_id=request.case_id,
            callback_url=request.callback_url,
            document_text=request.document_text
        )
        
        return AnalyzeResponse(
            job_id=job_id,
            status="queued",
            message="Document analysis queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue analysis: {str(e)}")


@router.post("/ask", response_model=AskAIResponse)
async def ask_ai_question(
    request: AskAIRequest,
    _: str = Depends(verify_api_key)
):
    """
    Ask AI a question about case documents.
    Uses RAG to retrieve relevant context and generate an answer.
    """
    try:
        logger.info(f"Processing AI question for case {request.case_id}")
        
        # Use RAG retriever to answer question
        result = rag_retriever.ask_question(
            case_id=request.case_id,
            question=request.question,
            top_k=10
        )
        
        return AskAIResponse(
            question=request.question,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
        
    except Exception as e:
        logger.error(f"Failed to process AI question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")
