"""
Standalone Candidates API - No Dependencies
==========================================

Simple candidate management without complex imports or dependencies.
"""

import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from datetime import datetime

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models
from app.models.models import Candidate

# Simple Pydantic models for API
from pydantic import BaseModel, EmailStr
from typing import List

class CandidateCreate(BaseModel):
    name: str
    email: str
    current_title: str
    skills: List[str]
    resume_summary: str
    preferred_interview_date: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[float] = None

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    position: str  # This is current_title in the database
    skills: str    # Stored as comma-separated string
    resume_text: str  # This is resume_summary
    status: str
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/", response_model=CandidateResponse)
async def create_candidate(candidate_data: CandidateCreate, db: Session = Depends(get_db)):
    """Create a new candidate"""
    try:
        logger.info(f"Creating candidate: {candidate_data.name}")
        
        # Check if candidate exists
        existing = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Candidate with this email already exists")
        
        # Parse interview date
        interview_date = None
        if candidate_data.preferred_interview_date:
            try:
                interview_date = datetime.fromisoformat(candidate_data.preferred_interview_date.replace('Z', '+00:00'))
            except:
                interview_date = None
        
        # Create candidate - only set the fields we need, let SQLAlchemy handle ID and timestamps
        new_candidate = Candidate(
            name=candidate_data.name,
            email=candidate_data.email,
            position=candidate_data.current_title,
            phone=candidate_data.phone,
            location=candidate_data.location,
            experience_years=candidate_data.experience_years or 0,
            skills=", ".join(candidate_data.skills),
            resume_text=candidate_data.resume_summary,
            interview_datetime=interview_date,
            status="submitted",
            ai_analysis_status="pending",
            interview_scheduled=0
        )
        
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)
        
        logger.info(f"✅ Created candidate ID: {new_candidate.id}")
        
        # 🚀 TRIGGER AUTOMATION WORKFLOW
        logger.info(f"🤖 Triggering automated interview scheduling for {new_candidate.name}")
        try:
            # Import automation service
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from automation_service import trigger_automation_after_candidate_creation
            
            # Trigger automation in background
            automation_result = await trigger_automation_after_candidate_creation(
                new_candidate.id, db
            )
            
            if automation_result.get('success'):
                logger.info(f"🎉 Automation completed successfully!")
                logger.info(f"   📅 Interviewer: {automation_result.get('interviewer')}")
                logger.info(f"   ⏰ Scheduled: {automation_result.get('scheduled_time')}")
                logger.info(f"   🎥 Meet Link: {automation_result.get('meet_link')}")
            else:
                logger.warning(f"⚠️ Automation had issues: {automation_result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Automation trigger failed: {e}")
            # Don't fail candidate creation if automation fails
        
        return new_candidate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating candidate: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create candidate: {str(e)}")

@router.get("/", response_model=List[CandidateResponse])
async def list_candidates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all candidates"""
    try:
        candidates = db.query(Candidate).offset(skip).limit(limit).all()
        return candidates
    except Exception as e:
        logger.error(f"❌ Error listing candidates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list candidates: {str(e)}")

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate"""
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get candidate: {str(e)}")

@router.get("/health/check")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "candidates_standalone"}
