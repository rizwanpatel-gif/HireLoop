"""
HireLoop Interview Automation System - Main Application
===================================================

Organized FastAPI application with automated interview scheduling,
Google Calendar integration, and AI-powered candidate analysis.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import uvicorn
import logging
import os

from app.core.limiter import limiter

# Import routers
from app.routers.candidates_standalone import router as candidates_router
from app.routers.dashboard_simple import router as dashboard_router
from app.routers.agent_chat import router as agent_chat_router
from app.routers.job_roles import router as job_roles_router
# Note: interviews router has import issues, will fix separately
# from app.routers.interviews import router as interviews_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HireLoop - Interview Automation System",
    description="Automated interview scheduling with AI analysis and Google Calendar integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Per-IP rate limiting — candidate creation and chat both trigger real LLM calls,
# so both need basic abuse protection. Shared `limiter` (app/core/limiter.py) is
# imported by the routers that need a per-route limit (candidates_standalone.py, agent_chat.py).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for frontend integration
FRONTEND_ORIGINS = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if uploads directory exists
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(
    candidates_router, 
    prefix="/api/candidates", 
    tags=["Candidates"]
)

app.include_router(
    dashboard_router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    agent_chat_router,
    prefix="/api/agent-chat",
    tags=["Agent Chat"]
)

app.include_router(
    job_roles_router,
    prefix="/api/job-roles",
    tags=["Job Roles"]
)

# TODO: Fix interviews router imports
# app.include_router(
#     interviews_router, 
#     prefix="/api/interviews", 
#     tags=["Interviews"]
# )

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "🚀 HireLoop Interview Automation System",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "candidates": "/api/candidates",
            "dashboard": "/api/dashboard", 
            "interviews": "/api/interviews"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hireloop_automation",
        "version": "2.0.0"
    }

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "api_version": "2.0.0",
        "endpoints": [
            "/api/candidates - Candidate management",
            "/api/dashboard - Interviewer dashboard",
            "/api/interviews - Interview scheduling"
        ],
        "features": [
            "Automated interview scheduling",
            "Google Calendar integration", 
            "AI-powered candidate analysis",
            "Email notifications",
            "Dashboard analytics"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting HireLoop Interview Automation System...")
    print("📋 API Docs: http://localhost:8000/docs")
    print("🎯 API Endpoints: http://localhost:8000/api")
    print("📊 Dashboard: http://localhost:8000/api/dashboard")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
