"""
Health check endpoint.
"""
from fastapi import APIRouter
from src.models.schemas import HealthResponse
from src.services.db import check_db_connection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns service status and version information.
    """
    # Check database connection
    db_healthy = check_db_connection()
    
    status = "healthy" if db_healthy else "degraded"
    
    if not db_healthy:
        logger.warning("Health check: Database connection failed")
    
    return HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )
