"""
FastAPI dependencies for authentication and database sessions.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from src.services.db import get_db
import os
import logging

logger = logging.getLogger(__name__)

# API key from environment
API_KEY = os.getenv("CASEINTEL_API_KEY")
if not API_KEY:
    logger.warning("CASEINTEL_API_KEY not set - API authentication will fail")


async def verify_api_key(x_api_key: str = Header(..., description="API key for authentication")) -> str:
    """
    Verify API key from request header.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: API key not configured"
        )
    
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return x_api_key


def get_db_session():
    """
    Get database session dependency.
    
    Yields:
        Session: SQLAlchemy database session
    """
    yield from get_db()
