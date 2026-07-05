"""
Standalone Candidates API - No Dependencies
==========================================

Simple candidate management without complex imports or dependencies.
"""

import os
import logging
import pytz
from fastapi import APIRouter, HTTPException, Depends, Request
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
from app.models.models import Candidate, JobRole
from app.core.limiter import limiter

# Simple Pydantic models for API
from pydantic import BaseModel, EmailStr
from typing import List

MATCH_SCORE_THRESHOLD = float(os.getenv("MATCH_SCORE_THRESHOLD", "60"))

class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    job_role_id: Optional[int] = None  # RAG-matched against this role's JD before insert
    resume_summary: str
    current_title: Optional[str] = None  # Derived from job_role.title when not given
    skills: Optional[List[str]] = None   # Derived from the AI's resume extraction when not given
    experience_years: Optional[float] = None  # Derived from the AI's resume extraction when not given
    preferred_interview_date: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

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
    interview_date: Optional[datetime] = None  # For frontend compatibility
    current_round: Optional[int] = None  # For frontend compatibility

    class Config:
        from_attributes = True

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/")
@limiter.limit("10/minute")
async def create_candidate(request: Request, candidate_data: CandidateCreate, db: Session = Depends(get_db)):
    """
    Score the resume against the applied-for job role's JD (RAG match) BEFORE ever
    inserting a row. Below MATCH_SCORE_THRESHOLD: send a rejection email and return
    without touching the database. At/above threshold: insert the candidate.

    (LangGraph round-1 confirmation is wired in a later phase; for now the candidate
    is simply inserted with status="awaiting_round1_confirmation".)
    """
    try:
        logger.info(f"Creating candidate: {candidate_data.name}")

        # Check if candidate exists
        existing = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Candidate with this email already exists")

        # --- RAG match against the job role's JD, before any insert ---
        # This same call also extracts experience_years/skills from the resume
        # text, since the intake form only collects name/email/role/resume now.
        job_role = None
        match_result = None
        match_score = None
        match_rationale = None
        if candidate_data.job_role_id:
            job_role = db.query(JobRole).filter(JobRole.id == candidate_data.job_role_id).first()
            if not job_role:
                raise HTTPException(status_code=404, detail="Job role not found")

        if job_role:
            from starlette.concurrency import run_in_threadpool
            from app.services.matching_service import score_resume_against_role
            from app.services.ai_service import AIService

            ai_service = AIService()
            match_result = await run_in_threadpool(
                score_resume_against_role, candidate_data.resume_summary, job_role, ai_service
            )
            match_score = match_result.score
            match_rationale = match_result.rationale

            logger.info(f"🎯 Match score for {candidate_data.name} vs '{job_role.title}': {match_score}/100")

            if match_score < MATCH_SCORE_THRESHOLD:
                from app.services.email_service import EmailService
                email_service = EmailService()
                if email_service.enabled:
                    await email_service.send_rejection_email(
                        to_email=candidate_data.email,
                        candidate_name=candidate_data.name,
                        position=job_role.title,
                    )
                logger.info(f"❌ {candidate_data.name} rejected pre-insert (score {match_score} < {MATCH_SCORE_THRESHOLD}) — no row created")
                return {
                    "status": "rejected",
                    "message": f"Thank you, {candidate_data.name} - after review, your profile does not match the {job_role.title} role closely enough to proceed.",
                    "match_score": match_score,
                    "rationale": match_rationale,
                }

        # Parse interview date - frontend sends datetime-local format (YYYY-MM-DDTHH:MM) in IST
        interview_date = None
        if candidate_data.preferred_interview_date:
            try:
                # Frontend sends datetime-local format like "2025-08-07T10:00" (IST timezone)
                INDIA_TZ = pytz.timezone("Asia/Kolkata")

                # Parse the datetime-local string and treat as IST
                if 'T' in candidate_data.preferred_interview_date:
                    # Format: "2025-08-07T10:00"
                    naive_dt = datetime.fromisoformat(candidate_data.preferred_interview_date)
                    interview_date = INDIA_TZ.localize(naive_dt)
                    logger.info(f"📅 Parsed interview date as IST: {interview_date.strftime('%Y-%m-%d %I:%M %p %Z')}")
                else:
                    # Fallback for ISO format
                    interview_date = datetime.fromisoformat(candidate_data.preferred_interview_date.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse interview date: {e}")
                interview_date = None

        # experience_years/skills: use what the client sent, else what the AI
        # extracted from the resume text during scoring, else a plain default.
        experience_years = candidate_data.experience_years
        if experience_years is None:
            experience_years = match_result.estimated_experience_years if match_result else 0

        skills_list = candidate_data.skills
        if not skills_list:
            skills_list = match_result.extracted_skills if match_result else []

        # Create candidate - only set the fields we need, let SQLAlchemy handle ID and timestamps
        new_candidate = Candidate(
            name=candidate_data.name,
            email=candidate_data.email,
            position=job_role.title if job_role else (candidate_data.current_title or "Unspecified"),
            job_role_id=candidate_data.job_role_id,
            phone=candidate_data.phone,
            location=candidate_data.location,
            experience_years=experience_years,
            skills=", ".join(skills_list),
            resume_text=candidate_data.resume_summary,
            interview_datetime=interview_date,
            status="awaiting_round1_confirmation" if job_role else "submitted",
            ai_analysis_status="completed" if job_role else "pending",
            ai_overall_score=match_score,
            interview_scheduled=0
        )

        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        logger.info(f"✅ Created candidate ID: {new_candidate.id}")

        # Start the LangGraph thread so HR sees the round-1 question in chat immediately
        if job_role:
            from starlette.concurrency import run_in_threadpool
            from app.services.hiring_graph import start_round1_thread
            from app.models.models import ChatMessage

            graph_result = await run_in_threadpool(start_round1_thread, new_candidate.id)
            interrupts = graph_result.get("__interrupt__", [])
            if interrupts:
                question = interrupts[0].value.get("question", "Send Round 1 invite?")
                db.add(ChatMessage(role="assistant", content=question, candidate_id=new_candidate.id))
                db.commit()

        return {
            "status": "created",
            "id": new_candidate.id,
            "name": new_candidate.name,
            "email": new_candidate.email,
            "position": new_candidate.position,
            "skills": new_candidate.skills or "",
            "resume_text": new_candidate.resume_text or "",
            "candidate_status": new_candidate.status,
            "phone": new_candidate.phone,
            "location": new_candidate.location,
            "experience_years": new_candidate.experience_years,
            "created_at": new_candidate.created_at,
            "updated_at": new_candidate.updated_at,
            "interview_date": new_candidate.interview_datetime,
            "current_round": new_candidate.current_round or 0,
            "ai_overall_score": new_candidate.ai_overall_score,
            "match_rationale": match_rationale,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating candidate: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create candidate: {str(e)}")

@router.get("/", response_model=List[CandidateResponse])
async def list_candidates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all candidates with interview information"""
    try:
        # Get candidates without loading problematic Interview records for now
        candidates = db.query(Candidate).offset(skip).limit(limit).all()
        
        result = []
        for candidate in candidates:
            # Skip Interview loading for now due to enum issues
            # TODO: Fix enum values in database or Interview model
            latest_interview = None
            
            # Create response object
            candidate_dict = {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "position": candidate.position,
                "skills": candidate.skills or "",
                "resume_text": candidate.resume_text or "",
                "status": candidate.status or "pending",
                "phone": candidate.phone,
                "location": candidate.location,
                "experience_years": candidate.experience_years,
                "created_at": candidate.created_at,
                "updated_at": candidate.updated_at,
                "interview_date": candidate.interview_datetime,  # Use candidate's own interview date
                "current_round": 1 if candidate.interview_datetime else 0  # Default logic
            }
            
            result.append(CandidateResponse(**candidate_dict))
        
        return result
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

@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate and send rejection email"""
    try:
        from app.services.candidate_lifecycle import reject_and_delete_candidate
        deleted = await reject_and_delete_candidate(candidate_id, db)

        return {
            "message": "Candidate deleted successfully",
            "deleted_candidate": {
                "id": deleted["id"],
                "name": deleted["name"],
                "email": deleted["email"]
            },
            "rejection_email_sent": deleted["rejection_email_sent"]
        }

    except ValueError:
        raise HTTPException(status_code=404, detail="Candidate not found")
    except Exception as e:
        logger.error(f"❌ Error deleting candidate: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete candidate: {str(e)}")

@router.get("/{candidate_id}/assigned-interviewer")
async def get_assigned_interviewer(candidate_id: int, db: Session = Depends(get_db)):
    """
    Who would be assigned to this candidate (experience_years > candidate's, closest fit).
    No Google Calendar involved - just the DB-driven assignment rule, shown to HR
    before they type in a date/time directly.
    """
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        from app.services.interviewer_calendar_registry import assign_interviewer
        interviewer = assign_interviewer(db, candidate.experience_years)
        if not interviewer:
            raise HTTPException(status_code=500, detail="No interviewers configured on the roster")

        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "assigned_interviewer": {"id": interviewer.id, "name": interviewer.name, "email": interviewer.email},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting assigned interviewer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get assigned interviewer: {str(e)}")

@router.post("/{candidate_id}/advance-round")
async def advance_candidate_to_next_round(
    candidate_id: int,
    round_number: int,
    scheduled_datetime: str,
    meet_link: str = None,
    db: Session = Depends(get_db)
):
    """
    Advance candidate to the next round using a date/time HR/the interviewer
    picked directly (no Google Calendar availability check or auto-created Meet -
    that integration was dropped as too slow to set up for a demo). meet_link is
    whatever link the interviewer shares (Meet/Zoom/etc.), optional.
    """
    try:
        # Find the candidate
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        logger.info(f"🎯 Advancing {candidate.name} to round {round_number}")

        from app.services.email_service import EmailService
        from app.services.interviewer_calendar_registry import assign_interviewer

        # Assign an interviewer (experience_years > candidate's) - pure DB lookup, no calendar involved
        interviewer = assign_interviewer(db, candidate.experience_years)
        if not interviewer:
            raise HTTPException(status_code=500, detail="No interviewers configured on the roster")

        email_service = EmailService()

        # Parse the HR/interviewer-provided datetime (same IST datetime-local convention as candidate intake)
        INDIA_TZ = pytz.timezone("Asia/Kolkata")
        try:
            if 'T' in scheduled_datetime:
                naive_dt = datetime.fromisoformat(scheduled_datetime)
                interview_dt = INDIA_TZ.localize(naive_dt) if naive_dt.tzinfo is None else naive_dt.astimezone(INDIA_TZ)
            else:
                interview_dt = datetime.fromisoformat(scheduled_datetime.replace('Z', '+00:00')).astimezone(INDIA_TZ)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid scheduled_datetime: {e}")

        # Update candidate's current round and interview details
        candidate.current_round = round_number
        candidate.interview_datetime = interview_dt
        candidate.status = "scheduled"
        db.commit()

        # Prepare email content
        round_names = {1: "First", 2: "Second", 3: "Final"}
        round_name = round_names.get(round_number, f"Round {round_number}")
        display_link = meet_link or "Your interviewer will share the call link with you directly before the interview."

        # Send email to candidate
        logger.info("📧 Sending email notification...")
        email_sent = await email_service.send_round_advancement_email(
            candidate_email=candidate.email,
            candidate_name=candidate.name,
            round_number=round_number,
            round_name=round_name,
            interview_datetime=interview_dt,
            meet_link=display_link,
            position=candidate.position
        )

        response_data = {
            "success": True,
            "message": f"Successfully advanced {candidate.name} to {round_name} round",
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "current_round": round_number,
                "status": candidate.status
            },
            "assigned_interviewer": {"id": interviewer.id, "name": interviewer.name, "email": interviewer.email},
            "interview_details": {
                "datetime": interview_dt.isoformat(),
                "meet_link": meet_link,
            },
            "email_sent": email_sent
        }

        logger.info(f"✅ Successfully advanced {candidate.name} to round {round_number}")
        logger.info(f"   📅 Scheduled: {interview_dt}")
        logger.info(f"   📧 Email Sent: {email_sent}")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error advancing candidate to round {round_number}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to advance candidate to round {round_number}: {str(e)}"
        )

@router.post("/{candidate_id}/send-rejection-email")
async def send_rejection_email(candidate_id: int, rejection_data: dict, db: Session = Depends(get_db)):
    """Send rejection email to candidate"""
    try:
        # Find the candidate
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        logger.info(f"📧 Sending rejection email to {candidate.name}")
        
        # Import email service
        from app.services.email_service import EmailService
        
        # Initialize email service
        email_service = EmailService()
        
        # Get rejection reason from request data
        rejection_reason = rejection_data.get('rejection_reason')

        # Send the rejection email
        if email_service.enabled:
            email_sent = await email_service.send_rejection_email(
                to_email=candidate.email,
                candidate_name=candidate.name,
                position=candidate.position,
                reason=rejection_reason,
            )

            if email_sent:
                # Update candidate status
                candidate.status = "rejected"
                db.commit()
                
                logger.info(f"✅ Rejection email sent successfully to {candidate.name}")
                
                return {
                    "success": True,
                    "message": f"Rejection email sent to {candidate.name}",
                    "candidate_email": candidate.email,
                    "email_sent": True
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to send rejection email")
        else:
            raise HTTPException(status_code=500, detail="Email service is not configured")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error sending rejection email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send rejection email: {str(e)}")

@router.get("/health/check")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "candidates_standalone"}


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Get dashboard data - temporarily using only candidate data due to enum issues"""
    try:
        candidates = db.query(Candidate).filter(
            Candidate.interview_datetime.isnot(None)
        ).order_by(Candidate.interview_datetime.asc()).all()
        
        dashboard = []
        for candidate in candidates:
            dashboard.append({
                "candidate_id": candidate.id,
                "name": candidate.name,
                "role": candidate.position,
                "interview_time": candidate.interview_datetime,
                "round": 1,  # Default for now
                "status": candidate.status or "scheduled",
            })
        return {"dashboard": dashboard}
    except Exception as e:
        logger.error(f"❌ Error getting dashboard: {e}")
        return {"dashboard": [], "error": str(e)}