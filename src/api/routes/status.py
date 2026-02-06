"""
Status and results endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.schemas import (
    StatusResponse, ResultsResponse, TimelineResponse, WitnessResponse,
    ClassificationResult, MetadataResult, PrivilegeResult, HotDocResult,
    AnalysisResult, CrossReferenceResult
)
from src.models.database import AnalysisJob, AnalysisResult as DBAnalysisResult, AgentTimelineEvent, WitnessMention
from src.api.dependencies import verify_api_key, get_db_session
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["status"], dependencies=[Depends(verify_api_key)])


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get the status of an analysis job.
    Used for polling progress updates.
    """
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Determine which agents have completed based on progress
        agents_completed = []
        if job.progress_percent >= 15:
            agents_completed.append("DocumentClassifier")
        if job.progress_percent >= 35:
            agents_completed.append("MetadataExtractor")
        if job.progress_percent >= 50:
            agents_completed.append("PrivilegeChecker")
        if job.progress_percent >= 65:
            agents_completed.append("HotDocDetector")
        if job.progress_percent >= 80:
            agents_completed.append("ContentAnalyzer")
        if job.progress_percent >= 100:
            agents_completed.append("CrossReferenceEngine")
        
        return StatusResponse(
            job_id=str(job.id),
            status=job.status,
            current_agent=job.current_agent,
            progress_percent=job.progress_percent,
            agents_completed=agents_completed,
            started_at=job.started_at,
            completed_at=job.completed_at,
            errors=[]  # TODO: Parse error_message into structured errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve status: {str(e)}")


@router.get("/results/{job_id}", response_model=ResultsResponse)
async def get_job_results(
    job_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get the complete analysis results for a job.
    Only available after job is completed.
    """
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status not in ["completed", "failed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Job is still {job.status}. Results not yet available."
            )
        
        # Get analysis results
        result = db.query(DBAnalysisResult).filter(DBAnalysisResult.job_id == job_id).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Results not found")
        
        # Build response
        response = ResultsResponse(
            job_id=str(job.id),
            case_id=job.case_id,
            status=job.status,
            started_at=job.started_at,
            completed_at=job.completed_at,
            errors=[]
        )
        
        # Add classification results
        if result.document_type:
            response.classification = ClassificationResult(
                document_type=result.document_type,
                confidence=result.classification_confidence or 0.0,
                reasoning=result.classification_reasoning or "",
                sub_type=result.document_sub_type
            )
        
        # Add metadata results
        if result.metadata:
            response.metadata = MetadataResult(
                dates=result.metadata.get("dates", []),
                people=result.metadata.get("people", []),
                entities=result.metadata.get("entities", []),
                locations=result.metadata.get("locations", [])
            )
        
        # Add privilege results
        if result.privilege_flags:
            response.privilege = PrivilegeResult(
                flags=result.privilege_flags,
                confidence=result.privilege_confidence or 0.0,
                reasoning=result.privilege_reasoning or "",
                recommendation=result.privilege_recommendation or "review_required",
                excerpts=[]
            )
        
        # Add hot doc results
        response.hot_doc = HotDocResult(
            is_hot_doc=result.is_hot_doc,
            score=result.hot_doc_score or 0.0,
            severity=result.hot_doc_severity or "low",
            flags=result.hot_doc_data.get("flags", []) if result.hot_doc_data else []
        )
        
        # Add analysis results
        if result.summary:
            response.analysis = AnalysisResult(
                summary=result.summary,
                key_facts=result.key_facts or [],
                legal_issues=result.legal_issues or [],
                draft_narrative=result.draft_narrative or "",
                evidence_gaps=result.evidence_gaps or []
            )
        
        # Add cross-reference results
        if result.cross_references:
            response.cross_references = CrossReferenceResult(
                related_documents=result.cross_references.get("related_docs", []),
                timeline_events=result.cross_references.get("timeline", []),
                witness_mentions=result.cross_references.get("witnesses", []),
                consistency_flags=result.cross_references.get("consistency_flags", [])
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.get("/case/{case_id}/timeline", response_model=TimelineResponse)
async def get_case_timeline(
    case_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get the timeline of events for a case.
    Aggregates timeline events from all analyzed documents.
    """
    try:
        events = db.query(AgentTimelineEvent).filter(
            AgentTimelineEvent.case_id == case_id
        ).order_by(AgentTimelineEvent.event_date).all()
        
        event_list = []
        for event in events:
            event_list.append({
                "id": str(event.id),
                "date": event.date.isoformat(),
                "event": event.event_description,
                "source_document_id": str(event.source_document_id) if event.source_document_id else None,
                "source_page": event.source_page,
                "significance": event.significance,
                "created_by": event.created_by
            })
        
        return TimelineResponse(
            case_id=case_id,
            events=event_list,
            total_count=len(event_list)
        )
        
    except Exception as e:
        logger.error(f"Failed to get case timeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve timeline: {str(e)}")


@router.get("/case/{case_id}/witnesses", response_model=WitnessResponse)
async def get_case_witnesses(
    case_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get the witness map for a case.
    Shows all witnesses and their mentions across documents.
    """
    try:
        mentions = db.query(WitnessMention).filter(
            WitnessMention.case_id == case_id
        ).all()
        
        # Group by witness name
        witness_map = {}
        for mention in mentions:
            name = mention.witness_name
            if name not in witness_map:
                witness_map[name] = {
                    "name": name,
                    "role": mention.role,
                    "mentions": []
                }
            
            witness_map[name]["mentions"].append({
                "document_id": str(mention.document_id) if mention.document_id else None,
                "context": mention.context,
                "page": mention.page_number
            })
        
        witness_list = list(witness_map.values())
        
        return WitnessResponse(
            case_id=case_id,
            witnesses=witness_list,
            total_count=len(witness_list)
        )
        
    except Exception as e:
        logger.error(f"Failed to get case witnesses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve witnesses: {str(e)}")
