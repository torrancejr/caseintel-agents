"""
FastAPI application entry point.
Configures CORS, middleware, and routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.api.routes import health, analyze, status
from src.services.db import init_db, check_db_connection
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CaseIntel AI Agents",
    description="AI-powered document analysis pipeline for legal case management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
ALLOWED_ORIGINS = [
    "https://caseintel.io",
    "https://www.caseintel.io",
]

# Add localhost for development (remove in production)
if os.getenv("ENVIRONMENT", "production") == "development":
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(status.router)


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Initialize database and check connections.
    """
    logger.info("Starting CaseIntel AI Agents service...")
    
    # Initialize database tables (in production, use Alembic migrations)
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    # Check database connection
    if check_db_connection():
        logger.info("Database connection verified")
    else:
        logger.error("Database connection failed")
    
    # Check required environment variables
    required_vars = [
        "ANTHROPIC_API_KEY",
        "DATABASE_URL",
        "CASEINTEL_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    else:
        logger.info("All required environment variables are set")
    
    logger.info("CaseIntel AI Agents service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    Clean up resources.
    """
    logger.info("Shutting down CaseIntel AI Agents service...")
    
    # Close notification service HTTP client
    from src.services.notifications import notification_service
    await notification_service.close()
    
    logger.info("Service shutdown complete")


@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "CaseIntel AI Agents",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )
