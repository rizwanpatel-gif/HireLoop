"""
Candidates API Router - Simplified and Clean
===========================================

This router handles candidate management with proper separation of concerns:
- Uses centralized models from app.models.models
- Uses centralized schemas from app.schemas
- Uses centralized database from app.core.database
- Simple candidate creation: name, email, title, skills, resume_summary, interview_date
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

# Import centralized components
from app.core.database import get_db
from app.models.models import Candidate, Interview, User
from app.schemas import (
    CandidateCreate, 
    CandidateResponse, 
    CandidateDetailResponse,
    CandidateListResponse,
    CandidateUpdate,
    SuccessResponse,
    ErrorResponse
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/", response_model=CandidateResponse)
async def create_candidate(
    candidate_data: CandidateCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new candidate with basic information:
    - Name, Email, Current Title, Skills, Resume Summary, Preferred Interview Date
    """
    try:
        logger.info(f"Creating candidate: {candidate_data.name} ({candidate_data.email})")
        
        # Check if candidate already exists
        existing_candidate = db.query(Candidate).filter(
            Candidate.email == candidate_data.email
        ).first()
        
        if existing_candidate:
            raise HTTPException(
                status_code=400,
                detail=f"Candidate with email {candidate_data.email} already exists"
            )
        
        # Create new candidate with simplified schema mapping
        new_candidate = Candidate(
            name=candidate_data.name,
            email=candidate_data.email,
            position=candidate_data.current_title,  # Map current_title to position
            phone=candidate_data.phone,
            location=candidate_data.location,
            experience_years=candidate_data.experience_years or 0,
            
            # Store skills as text for simplicity
            skills=", ".join(candidate_data.skills) if candidate_data.skills else "",
            resume_text=candidate_data.resume_summary,
            
            # Interview scheduling
            interview_datetime=candidate_data.preferred_interview_date,
            
            # Default values
            status="submitted",
            ai_analysis_status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)
        
        logger.info(f"✅ Candidate created successfully with ID: {new_candidate.id}")
        
        # Schedule background AI analysis (optional)
        # background_tasks.add_task(analyze_candidate_background, new_candidate.id)
        
        # Return response
        return CandidateResponse(
            id=new_candidate.id,
            name=new_candidate.name,
            email=new_candidate.email,
            current_title=new_candidate.position,
            skills=new_candidate.skills.split(", ") if new_candidate.skills else [],
            resume_summary=new_candidate.resume_text or "",
            status=new_candidate.status,
            phone=new_candidate.phone,
            location=new_candidate.location,
            experience_years=new_candidate.experience_years,
            preferred_interview_date=new_candidate.interview_datetime,
            ai_analysis_status=new_candidate.ai_analysis_status,
            ai_overall_score=new_candidate.ai_overall_score,
            ai_technical_score=new_candidate.ai_technical_score,
            created_at=new_candidate.created_at,
            updated_at=new_candidate.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating candidate: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create candidate: {str(e)}"
        )


@router.get("/", response_model=CandidateListResponse)
async def list_candidates(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all candidates with optional filtering"""
    try:
        query = db.query(Candidate)
        
        # Apply filters
        if status:
            query = query.filter(Candidate.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        candidates = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        candidate_responses = []
        for candidate in candidates:
            candidate_responses.append(CandidateResponse(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                current_title=candidate.position,
                skills=candidate.skills.split(", ") if candidate.skills else [],
                resume_summary=candidate.resume_text or "",
                status=candidate.status,
                phone=candidate.phone,
                location=candidate.location,
                experience_years=candidate.experience_years,
                preferred_interview_date=candidate.interview_datetime,
                ai_analysis_status=candidate.ai_analysis_status,
                ai_overall_score=candidate.ai_overall_score,
                ai_technical_score=candidate.ai_technical_score,
                created_at=candidate.created_at,
                updated_at=candidate.updated_at
            ))
        
        return CandidateListResponse(
            candidates=candidate_responses,
            total=total,
            page=skip // limit + 1,
            size=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
        
    except Exception as e:
        logger.error(f"❌ Error listing candidates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list candidates: {str(e)}"
        )


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific candidate"""
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        
        return CandidateDetailResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            current_title=candidate.position,
            skills=candidate.skills.split(", ") if candidate.skills else [],
            resume_summary=candidate.resume_text or "",
            status=candidate.status,
            phone=candidate.phone,
            location=candidate.location,
            experience_years=candidate.experience_years,
            preferred_interview_date=candidate.interview_datetime,
            
            # Analysis results
            ai_analysis_status=candidate.ai_analysis_status,
            ai_overall_score=candidate.ai_overall_score,
            ai_technical_score=candidate.ai_technical_score,
            ai_experience_score=candidate.ai_experience_score,
            ai_cultural_fit_score=candidate.ai_cultural_fit_score,
            ai_confidence_score=candidate.ai_confidence_score,
            
            # Scheduling info
            interview_scheduled=bool(candidate.interview_scheduled),
            interview_type=candidate.interview_type,
            
            # Notes and metadata
            recruiter_notes=candidate.recruiter_notes,
            analyzed_at=candidate.analyzed_at,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting candidate {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get candidate: {str(e)}"
        )


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """Update candidate information"""
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        
        # Update fields that are provided
        update_data = candidate_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "current_title":
                setattr(candidate, "position", value)
            elif field == "skills" and isinstance(value, list):
                setattr(candidate, "skills", ", ".join(value))
            elif field == "resume_summary":
                setattr(candidate, "resume_text", value)
            elif field == "preferred_interview_date":
                setattr(candidate, "interview_datetime", value)
            else:
                setattr(candidate, field, value)
        
        candidate.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(candidate)
        
        logger.info(f"✅ Candidate {candidate_id} updated successfully")
        
        return CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            current_title=candidate.position,
            skills=candidate.skills.split(", ") if candidate.skills else [],
            resume_summary=candidate.resume_text or "",
            status=candidate.status,
            phone=candidate.phone,
            location=candidate.location,
            experience_years=candidate.experience_years,
            preferred_interview_date=candidate.interview_datetime,
            ai_analysis_status=candidate.ai_analysis_status,
            ai_overall_score=candidate.ai_overall_score,
            ai_technical_score=candidate.ai_technical_score,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating candidate {candidate_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update candidate: {str(e)}"
        )


@router.delete("/{candidate_id}", response_model=SuccessResponse)
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate and all related interviews"""
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        
        # Delete the candidate (interviews will be deleted due to cascade)
        db.delete(candidate)
        db.commit()
        
        logger.info(f"✅ Candidate {candidate_id} deleted successfully")
        
        return SuccessResponse(
            success=True,
            message=f"Candidate {candidate.name} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting candidate {candidate_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete candidate: {str(e)}"
        )


# Health check for candidates router
@router.get("/health/check")
async def candidates_health_check():
    """Health check endpoint for candidates router"""
    return {
        "status": "healthy",
        "service": "candidates_api",
        "timestamp": datetime.utcnow().isoformat()
    }


# Background task function (optional)
async def analyze_candidate_background(candidate_id: int):
    """
    Background task to analyze candidate with AI
    This would integrate with your AI service
    """
    logger.info(f"🤖 Starting AI analysis for candidate {candidate_id}")
    # Implementation would go here
    pass
