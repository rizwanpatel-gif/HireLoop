"""
Simple Dashboard Router - Testing
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import Dict, Any

# Create router
router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_dashboard_simple(db: Session = Depends(get_db)):
    """Simple dashboard endpoint for testing"""
    return {
        "message": "Dashboard is working!",
        "status": "success"
    }

@router.get("/health")
async def dashboard_health():
    """Dashboard health check"""
    return {"status": "healthy", "service": "dashboard"}
