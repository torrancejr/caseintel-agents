"""
Progress update and notification service.
Sends updates to frontend via webhooks or other mechanisms.
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending progress updates and notifications."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def send_progress_update(
        self,
        callback_url: str,
        job_id: str,
        status: str,
        progress_percent: int,
        current_agent: Optional[str] = None,
        message: Optional[str] = None
    ) -> bool:
        """
        Send a progress update to the callback URL.
        
        Args:
            callback_url: Webhook URL to send update to
            job_id: Job identifier
            status: Current status
            progress_percent: Progress percentage (0-100)
            current_agent: Currently executing agent
            message: Optional status message
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            payload = {
                "job_id": job_id,
                "status": status,
                "progress_percent": progress_percent,
                "current_agent": current_agent,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self.client.post(callback_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Sent progress update for job {job_id} to {callback_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send progress update: {str(e)}")
            return False
    
    async def send_completion_notification(
        self,
        callback_url: str,
        job_id: str,
        case_id: str,
        status: str,
        results_summary: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a completion notification.
        
        Args:
            callback_url: Webhook URL
            job_id: Job identifier
            case_id: Case identifier
            status: Final status (completed/failed)
            results_summary: Optional summary of results
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            payload = {
                "job_id": job_id,
                "case_id": case_id,
                "status": status,
                "completed_at": datetime.utcnow().isoformat(),
                "results_summary": results_summary or {}
            }
            
            response = await self.client.post(callback_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Sent completion notification for job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send completion notification: {str(e)}")
            return False
    
    async def send_hot_doc_alert(
        self,
        callback_url: str,
        job_id: str,
        case_id: str,
        hot_doc_score: float,
        severity: str,
        summary: str
    ) -> bool:
        """
        Send an alert for a hot document detection.
        
        Args:
            callback_url: Webhook URL
            job_id: Job identifier
            case_id: Case identifier
            hot_doc_score: Hot doc score
            severity: Severity level
            summary: Brief summary of why it's hot
            
        Returns:
            bool: True if alert sent successfully
        """
        try:
            payload = {
                "type": "hot_doc_alert",
                "job_id": job_id,
                "case_id": case_id,
                "hot_doc_score": hot_doc_score,
                "severity": severity,
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self.client.post(callback_url, json=payload)
            response.raise_for_status()
            
            logger.warning(f"Sent hot doc alert for job {job_id} (severity: {severity})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send hot doc alert: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
notification_service = NotificationService()
