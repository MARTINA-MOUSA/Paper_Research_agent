from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import papers, classify, trends
import os
from dotenv import load_dotenv
from database.db import engine
from database import models
from config import settings
from loguru import logger
import sys


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level=settings.LOG_LEVEL
)

# Load .env before reading settings elsewhere
load_dotenv()

app = FastAPI(
    title="Paper2Video API",
    description="Upload research papers and generate summarized videos using Gemini API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
# When using "*" for origins, we cannot use allow_credentials=True
# So we explicitly allow common localhost origins for Streamlit
cors_origins = settings.cors_origins_list
if "*" in cors_origins or len(cors_origins) == 1 and cors_origins[0] == "*":
    # Allow all origins but disable credentials (or use specific origins)
    cors_origins = [
        "http://localhost:8501",  # Streamlit default
        "http://localhost:8502",  # Streamlit alternative
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8502",
        "http://localhost:8000",  # Direct API access
        "http://127.0.0.1:8000",
    ]
    allow_creds = False
else:
    allow_creds = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured with origins: {cors_origins}")
logger.info(f"GEMINI_API_KEY configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")

# Include routers
app.include_router(papers.router, prefix="/papers", tags=["Papers"])
app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(trends.router, prefix="/trends", tags=["Trends"])

@app.get("/")
def root():
    return {
        "message": "Welcome to Paper2Video API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "gemini_configured": bool(settings.GEMINI_API_KEY)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else "An error occurred"}
    )

@app.on_event("startup")
def on_startup():
    """Initialize database and create directories"""
    logger.info("Starting Paper2Video API...")
    models.Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logger.info("Application started successfully")

@app.on_event("shutdown")
def on_shutdown():
    logger.info("Shutting down Paper2Video API...")

