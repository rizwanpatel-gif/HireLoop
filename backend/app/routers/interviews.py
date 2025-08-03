"""
Interview Scheduling API Endpoint
=================================

This module provides the comprehensive interview scheduling endpoint that:
- Takes candidate_id and preferred_time from request
- Uses AI to find best available interviewer
- Creates interview record in database
- Triggers background Google Calendar event creation
- Returns interview details and confirmation

Integrates with:
- Candidate Management API
- Smart Matching Algorithm
- Google Calendar Service
- Background Tasks
- AI Analysis Results
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
import asyncio

# Import existing components
from app.candidate_management_api import (
    CandidateDB, AnalysisTaskDB, Base, get_db, SessionLocal,
    CandidateStatus, AnalysisStatus
)
from app.models.models import Interview as InterviewDB  # Use the main Interview model
from app.services.smart_matching_algorithm import SmartMatchingAlgorithm, create_sample_interviewer_profiles
from app.services.google_calendar_service import GoogleCalendarService
from app.services.background_tasks import analyze_candidate_background, task_manager
from app.services.ai_service import AIService
from app.services.automatic_scheduler import (
    AutomaticInterviewScheduler, schedule_interview_with_automation,
    SchedulingResult, SchedulingStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Interview Status Enum
class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

# Interview Type Enum
class InterviewType(str, Enum):
    TECHNICAL = "technical"
    HR = "hr"
    CULTURAL = "cultural"
    FINAL = "final"
    PHONE_SCREEN = "phone_screen"
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"

# Note: Using InterviewDB imported from app.models.models (imported as alias above)
# No need to redefine the class here since we use the main Interview model

# Add relationship to CandidateDB  
CandidateDB.interviews = relationship("InterviewDB", back_populates="candidate")

# Create tables
from app.core.database import engine
Base.metadata.create_all(bind=engine)

# Pydantic Models for API
class InterviewScheduleRequest(BaseModel):
    candidate_id: str = Field(..., description="Unique candidate identifier")
    preferred_time: datetime = Field(..., description="Preferred interview time")
    duration_minutes: int = Field(60, ge=30, le=180, description="Interview duration in minutes")
    interview_type: InterviewType = Field(InterviewType.TECHNICAL, description="Type of interview")
    interview_round: int = Field(1, ge=1, le=10, description="Interview round number")
    is_remote: bool = Field(True, description="Whether interview is remote")
    location: Optional[str] = Field(None, description="Physical location if not remote")
    additional_attendees: List[str] = Field(default_factory=list, description="Additional attendee emails")
    special_requirements: Optional[Dict[str, Any]] = Field(None, description="Special technical requirements")
    notes: Optional[str] = Field(None, description="Additional notes for the interview")
    
    @validator('preferred_time')
    def validate_future_time(cls, v):
        if v <= datetime.now():
            raise ValueError('Interview time must be in the future')
        return v
    
    @validator('additional_attendees')
    def validate_emails(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for email in v:
            if not re.match(email_pattern, email):
                raise ValueError(f'Invalid email address: {email}')
        return v

class InterviewResponse(BaseModel):
    interview_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    position: str
    
    # Scheduling details
    scheduled_time: datetime
    duration_minutes: int
    interview_type: str
    interview_round: int
    status: str
    
    # Interviewer details
    interviewer_id: str
    interviewer_name: str
    interviewer_email: str
    ai_match_score: float
    ai_match_confidence: float
    
    # Calendar integration
    calendar_event_id: Optional[str]
    calendar_event_link: Optional[str]
    google_meet_link: Optional[str]
    calendar_invites_sent: bool
    
    # AI recommendations
    ai_recommended_focus_areas: List[str]
    preparation_materials: List[Dict[str, str]]
    
    # Metadata
    created_at: datetime
    confirmation_required: bool
    
class InterviewConfirmationResponse(BaseModel):
    success: bool
    message: str
    interview: InterviewResponse
    calendar_details: Dict[str, Any]
    next_steps: List[str]

# Initialize services
calendar_service = GoogleCalendarService()
interviewer_profiles = create_sample_interviewer_profiles()
matching_algorithm = SmartMatchingAlgorithm(interviewer_profiles)

async def schedule_interview_endpoint(
    request: InterviewScheduleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> InterviewConfirmationResponse:
    """
    Enhanced interview scheduling endpoint with automatic scheduling logic
    
    This endpoint now uses the AutomaticInterviewScheduler to:
    1. Check interviewer availability in Google Calendar
    2. Create interview database record with all details  
    3. Generate Google Calendar event with meeting link
    4. Send confirmation notifications to both parties
    5. Update interview record with Google event ID
    
    Returns comprehensive scheduling results with full automation
    """
    
    try:
        logger.info(f"� Starting enhanced automatic interview scheduling")
        logger.info(f"   Candidate ID: {request.candidate_id}")
        logger.info(f"   Preferred Time: {request.preferred_time}")
        logger.info(f"   Interview Type: {request.interview_type}")
        
        # Use the new AutomaticInterviewScheduler for complete automation
        scheduling_result = await schedule_interview_with_automation(request, db)
        
        if not scheduling_result.success:
            logger.error(f"❌ Automatic scheduling failed: {scheduling_result.message}")
            raise HTTPException(
                status_code=400,
                detail=f"Interview scheduling failed: {scheduling_result.message}. Errors: {'; '.join(scheduling_result.errors)}"
            )
        
        # Get the created interview record for response
        interview = db.query(InterviewDB).filter(InterviewDB.id == scheduling_result.interview_id).first()
        if not interview:
            raise HTTPException(status_code=500, detail="Interview record not found after creation")
        
        # Get candidate details for response
        candidate = db.query(CandidateDB).filter(CandidateDB.id == request.candidate_id).first()
        
        # Build comprehensive response
        interview_response = InterviewResponse(
            interview_id=scheduling_result.interview_id,
            candidate_id=request.candidate_id,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            position=candidate.position,
            scheduled_time=request.preferred_time,
            duration_minutes=request.duration_minutes,
            interview_type=request.interview_type.value,
            interview_round=request.interview_round,
            status=interview.status,
            interviewer_id=scheduling_result.interviewer_selected['id'],
            interviewer_name=scheduling_result.interviewer_selected['name'],
            interviewer_email=scheduling_result.interviewer_selected['email'],
            ai_match_score=scheduling_result.interviewer_selected['match_score'],
            ai_match_confidence=scheduling_result.interviewer_selected['confidence'],
            calendar_event_id=scheduling_result.calendar_event_id,
            calendar_event_link=interview.calendar_event_link,
            google_meet_link=scheduling_result.google_meet_link,
            calendar_invites_sent=scheduling_result.notifications_sent,
            ai_recommended_focus_areas=interview.ai_recommended_focus_areas or [],
            preparation_materials=interview.preparation_materials or [],
            created_at=interview.created_at,
            confirmation_required=not scheduling_result.notifications_sent
        )
        
        # Generate enhanced next steps based on automation results
        next_steps = []
        
        if scheduling_result.calendar_event_id:
            next_steps.extend([
                "✅ Calendar event created successfully",
                "🎥 Google Meet link generated and ready"
            ])
        else:
            next_steps.append("⚠️ Manual calendar event creation required")
        
        if scheduling_result.notifications_sent:
            next_steps.extend([
                "✅ Confirmation emails sent to all participants",
                "📧 Interview invitations delivered"
            ])
        else:
            next_steps.append("⚠️ Manual notification sending required")
        
        next_steps.extend([
            f"⏰ Interview scheduled for {request.preferred_time.strftime('%A, %B %d, %Y at %I:%M %p')}",
            f"👨‍💼 Interviewer: {scheduling_result.interviewer_selected['name']} (AI Score: {scheduling_result.interviewer_selected['match_score']:.1f}/100)",
            "🔔 Automatic reminders configured (24h, 30min, 10min before)",
            "📝 Interview preparation materials ready for review"
        ])
        
        # Add AI recommendations if available
        if interview.ai_recommended_focus_areas:
            next_steps.append(f"🎯 AI recommends focusing on: {', '.join(interview.ai_recommended_focus_areas[:2])}")
        
        # Prepare enhanced calendar details
        calendar_details = {
            'event_creation_status': 'completed' if scheduling_result.calendar_event_id else 'failed',
            'event_id': scheduling_result.calendar_event_id,
            'google_meet_link': scheduling_result.google_meet_link,
            'attendees': [
                candidate.email,
                scheduling_result.interviewer_selected['email']
            ] + request.additional_attendees,
            'notifications_sent': scheduling_result.notifications_sent,
            'calendar_reminders': ['24 hours before', '30 minutes before', '10 minutes before'],
            'automation_status': {
                'calendar_checked': True,
                'interviewer_matched': True,
                'record_created': True,
                'emails_sent': scheduling_result.notifications_sent
            }
        }
        
        # Add any errors to calendar details
        if scheduling_result.errors:
            calendar_details['errors'] = scheduling_result.errors
        
        confirmation_response = InterviewConfirmationResponse(
            success=True,
            message=f"Interview automatically scheduled with {scheduling_result.interviewer_selected['name']} for {request.preferred_time.strftime('%A, %B %d, %Y at %I:%M %p')}",
            interview=interview_response,
            calendar_details=calendar_details,
            next_steps=next_steps
        )
        
        logger.info(f"🎉 Enhanced interview scheduling completed successfully!")
        logger.info(f"   Interview ID: {scheduling_result.interview_id}")
        logger.info(f"   Interviewer: {scheduling_result.interviewer_selected['name']} (Score: {scheduling_result.interviewer_selected['match_score']:.1f})")
        logger.info(f"   Calendar Event: {scheduling_result.calendar_event_id or 'Failed'}")
        logger.info(f"   Google Meet: {scheduling_result.google_meet_link or 'Failed'}")
        logger.info(f"   Notifications: {'Sent' if scheduling_result.notifications_sent else 'Failed'}")
        logger.info(f"   Status: {scheduling_result.status}")
        
        return confirmation_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Enhanced interview scheduling failed: {e}")
        logger.exception("Full error details:")
        
        raise HTTPException(
            status_code=500,
            detail=f"Interview scheduling failed: {str(e)}"
        )
        selected_interviewer = best_match['interviewer']
        match_score = best_match['match_score']
        match_confidence = best_match.get('confidence_score', 0.8)
        
        logger.info(f"   ✅ Selected interviewer: {selected_interviewer['name']}")
        logger.info(f"   📊 Match Score: {match_score:.1f}/100")
        logger.info(f"   🎯 Confidence: {match_confidence:.1f}")
        
        # Step 4: Create interview record in database
        logger.info(f"   💾 Creating interview record in database...")
        
        interview_id = str(uuid.uuid4())
        
        # Extract AI recommendations
        ai_focus_areas = []
        preparation_materials = []
        
        if ai_analysis:
            # Extract focus areas from AI analysis
            interview_strategy = ai_analysis.get('interview_strategy', {})
            ai_focus_areas = interview_strategy.get('focus_areas', [])
            
            # Generate preparation materials based on candidate's profile
            strengths = ai_analysis.get('strengths', [])
            areas_for_improvement = ai_analysis.get('areas_for_improvement', [])
            
            preparation_materials = [
                {
                    "type": "technical_review",
                    "title": f"Review {candidate.position} Technical Skills",
                    "description": f"Focus on: {', '.join(strengths[:3])}"
                },
                {
                    "type": "candidate_background",
                    "title": "Candidate Background Review",
                    "description": f"Experience: {candidate.experience_years} years, Previous: {', '.join(candidate.previous_companies or [])}"
                }
            ]
            
            if areas_for_improvement:
                preparation_materials.append({
                    "type": "improvement_areas",
                    "title": "Areas to Explore",
                    "description": f"Assess: {', '.join(areas_for_improvement[:2])}"
                })
        
        # Create interview database record
        interview_db = InterviewDB(
            id=interview_id,
            candidate_id=request.candidate_id,
            interviewer_id=selected_interviewer['id'],
            scheduled_time=request.preferred_time,
            duration_minutes=request.duration_minutes,
            interview_type=request.interview_type.value,
            status=InterviewStatus.SCHEDULED,
            position=candidate.position,
            interview_round=request.interview_round,
            is_remote=request.is_remote,
            location=request.location,
            interviewer_name=selected_interviewer['name'],
            interviewer_email=selected_interviewer['email'],
            additional_attendees=request.additional_attendees,
            ai_match_score=match_score,
            ai_match_confidence=match_confidence,
            ai_recommended_focus_areas=ai_focus_areas,
            preparation_materials=preparation_materials,
            technical_requirements=request.special_requirements or {},
            interview_notes=request.notes
        )
        
        db.add(interview_db)
        db.commit()
        
        logger.info(f"   ✅ Interview record created with ID: {interview_id}")
        
        # Step 5: Trigger background Google Calendar event creation
        logger.info(f"   📅 Triggering Google Calendar event creation...")
        
        # Add background task for calendar event creation
        background_tasks.add_task(
            create_calendar_event_background,
            interview_id=interview_id,
            candidate_data={
                'name': candidate.name,
                'email': candidate.email,
                'position': candidate.position
            },
            interviewer_data={
                'name': selected_interviewer['name'],
                'email': selected_interviewer['email']
            },
            interview_details={
                'scheduled_time': request.preferred_time,
                'duration_minutes': request.duration_minutes,
                'interview_type': request.interview_type.value,
                'interview_round': request.interview_round,
                'additional_attendees': request.additional_attendees,
                'notes': request.notes,
                'focus_areas': ai_focus_areas
            }
        )
        
        # Step 6: Prepare response with interview details and confirmation
        logger.info(f"   📝 Preparing comprehensive response...")
        
        interview_response = InterviewResponse(
            interview_id=interview_id,
            candidate_id=request.candidate_id,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            position=candidate.position,
            scheduled_time=request.preferred_time,
            duration_minutes=request.duration_minutes,
            interview_type=request.interview_type.value,
            interview_round=request.interview_round,
            status=InterviewStatus.SCHEDULED,
            interviewer_id=selected_interviewer['id'],
            interviewer_name=selected_interviewer['name'],
            interviewer_email=selected_interviewer['email'],
            ai_match_score=match_score,
            ai_match_confidence=match_confidence,
            calendar_event_id=None,  # Will be populated by background task
            calendar_event_link=None,  # Will be populated by background task
            google_meet_link=None,  # Will be populated by background task
            calendar_invites_sent=False,  # Will be updated by background task
            ai_recommended_focus_areas=ai_focus_areas,
            preparation_materials=preparation_materials,
            created_at=datetime.utcnow(),
            confirmation_required=True
        )
        
        # Generate next steps
        next_steps = [
            "📧 Calendar invitations will be sent to all participants",
            "🎥 Google Meet link will be generated and shared",
            "📝 Interview preparation materials are ready for review",
            f"⏰ Interview scheduled for {request.preferred_time.strftime('%A, %B %d, %Y at %I:%M %p')}",
            "🔔 Reminders will be sent 24 hours and 30 minutes before the interview"
        ]
        
        if ai_focus_areas:
            next_steps.append(f"🎯 AI recommends focusing on: {', '.join(ai_focus_areas[:2])}")
        
        # Prepare calendar details
        calendar_details = {
            'event_creation_status': 'in_progress',
            'expected_completion_time': '2-3 minutes',
            'attendees': [
                candidate.email,
                selected_interviewer['email']
            ] + request.additional_attendees,
            'google_meet_enabled': True,
            'calendar_reminders': ['24 hours before', '30 minutes before', '10 minutes before']
        }
        
        confirmation_response = InterviewConfirmationResponse(
            success=True,
            message=f"Interview successfully scheduled with {selected_interviewer['name']} for {request.preferred_time.strftime('%A, %B %d, %Y at %I:%M %p')}",
            interview=interview_response,
            calendar_details=calendar_details,
            next_steps=next_steps
        )
        
        logger.info(f"🎉 Interview scheduling completed successfully!")
        logger.info(f"   Interview ID: {interview_id}")
        logger.info(f"   Interviewer: {selected_interviewer['name']} (Score: {match_score:.1f})")
        logger.info(f"   Scheduled: {request.preferred_time}")
        logger.info(f"   Calendar event creation in progress...")
        
        return confirmation_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Interview scheduling failed: {e}")
        logger.exception("Full error details:")
        
        raise HTTPException(
            status_code=500,
            detail=f"Interview scheduling failed: {str(e)}"
        )

async def create_calendar_event_background(
    interview_id: str,
    candidate_data: Dict[str, str],
    interviewer_data: Dict[str, str], 
    interview_details: Dict[str, Any]
):
    """
    Background task to create Google Calendar event for the interview
    
    Args:
        interview_id: Interview record ID
        candidate_data: Candidate information
        interviewer_data: Interviewer information
        interview_details: Interview scheduling details
    """
    
    db = SessionLocal()
    
    try:
        logger.info(f"📅 Creating Google Calendar event for interview {interview_id}")
        
        # Get interview record
        interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
        if not interview:
            raise Exception(f"Interview {interview_id} not found")
        
        # Authenticate calendar service (in production, use service account)
        # For demo, we'll simulate the calendar creation
        authenticated = calendar_service.authenticate(interviewer_data['email'])
        
        if not authenticated:
            logger.warning(f"Calendar authentication failed for {interviewer_data['email']}")
            # In production, you might want to fall back to a system account
            # For now, we'll mark as failed but continue
        
        # Create calendar event
        calendar_result = calendar_service.create_calendar_event_with_details(
            title=f"{interview_details['interview_type'].title()} Interview - Round {interview_details['interview_round']}",
            candidate_name=candidate_data['name'],
            candidate_email=candidate_data['email'],
            position=candidate_data['position'],
            interviewer_name=interviewer_data['name'],
            interviewer_email=interviewer_data['email'],
            start_datetime=interview_details['scheduled_time'],
            duration_minutes=interview_details['duration_minutes'],
            interview_type=interview_details['interview_type'].title(),
            notes=interview_details.get('notes', ''),
            additional_attendees=interview_details.get('additional_attendees', [])
        )
        
        if calendar_result:
            # Update interview record with calendar details
            interview.calendar_event_id = calendar_result['event_id']
            interview.calendar_event_link = calendar_result['event_link']
            interview.google_meet_link = calendar_result.get('meet_link')
            interview.calendar_invites_sent = True
            interview.status = InterviewStatus.CONFIRMED
            interview.confirmed_at = datetime.utcnow()
            interview.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"✅ Calendar event created successfully for interview {interview_id}")
            logger.info(f"   Event ID: {calendar_result['event_id']}")
            logger.info(f"   Meet Link: {calendar_result.get('meet_link', 'Pending')}")
            
        else:
            # Mark calendar creation as failed but keep interview scheduled
            interview.calendar_invites_sent = False
            interview.interview_notes = f"Calendar event creation failed. Manual calendar invite required. {interview.interview_notes or ''}"
            interview.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.error(f"❌ Calendar event creation failed for interview {interview_id}")
            logger.error("   Interview remains scheduled - manual calendar invite required")
        
    except Exception as e:
        logger.error(f"❌ Background calendar creation failed for interview {interview_id}: {e}")
        
        # Update interview with error info
        try:
            if 'interview' in locals():
                interview.calendar_invites_sent = False
                interview.interview_notes = f"Calendar creation error: {str(e)}. {interview.interview_notes or ''}"
                interview.updated_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update interview record with error: {db_error}")
    
    finally:
        db.close()

# Additional helper endpoints

async def get_interview_status(interview_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current status of an interview including calendar event status"""
    
    interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Get candidate details
    candidate = db.query(CandidateDB).filter(CandidateDB.id == interview.candidate_id).first()
    
    return {
        'interview_id': interview_id,
        'status': interview.status,
        'candidate_name': candidate.name if candidate else 'Unknown',
        'interviewer_name': interview.interviewer_name,
        'scheduled_time': interview.scheduled_time,
        'calendar_event_created': bool(interview.calendar_event_id),
        'google_meet_link': interview.google_meet_link,
        'calendar_invites_sent': interview.calendar_invites_sent,
        'created_at': interview.created_at,
        'updated_at': interview.updated_at
    }

async def list_scheduled_interviews(
    candidate_id: Optional[str] = None,
    interviewer_email: Optional[str] = None,
    status: Optional[InterviewStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List scheduled interviews with optional filters"""
    
    query = db.query(InterviewDB)
    
    if candidate_id:
        query = query.filter(InterviewDB.candidate_id == candidate_id)
    if interviewer_email:
        query = query.filter(InterviewDB.interviewer_email == interviewer_email)
    if status:
        query = query.filter(InterviewDB.status == status)
    if from_date:
        query = query.filter(InterviewDB.scheduled_time >= from_date)
    if to_date:
        query = query.filter(InterviewDB.scheduled_time <= to_date)
    
    interviews = query.order_by(InterviewDB.scheduled_time.desc()).limit(50).all()
    
    result = []
    for interview in interviews:
        candidate = db.query(CandidateDB).filter(CandidateDB.id == interview.candidate_id).first()
        
        result.append({
            'interview_id': interview.id,
            'candidate_name': candidate.name if candidate else 'Unknown',
            'candidate_email': candidate.email if candidate else 'Unknown',
            'interviewer_name': interview.interviewer_name,
            'interviewer_email': interview.interviewer_email,
            'scheduled_time': interview.scheduled_time,
            'duration_minutes': interview.duration_minutes,
            'interview_type': interview.interview_type,
            'status': interview.status,
            'google_meet_link': interview.google_meet_link,
            'ai_match_score': interview.ai_match_score
        })
    
    return result

# Create FastAPI router
router = APIRouter(prefix="/interviews", tags=["interviews"])

# Add endpoints to router
router.add_api_route("/schedule", schedule_interview_endpoint, methods=["POST"])
router.add_api_route("/status/{interview_id}", get_interview_status, methods=["GET"]) 
router.add_api_route("/list", list_scheduled_interviews, methods=["GET"])

# Additional endpoints for frontend compatibility
@router.post("/checkAvailability")
async def check_availability(request: dict, db: Session = Depends(get_db)):
    """
    Check if an interviewer is available at a specific time.
    For demo purposes, always return available=True.
    """
    return {
        "available": True,
        "message": "Time slot is available"
    }

@router.post("/")
async def schedule_interview_simple(request: dict, db: Session = Depends(get_db)):
    """
    Simplified schedule endpoint for frontend compatibility.
    Creates a mock interview record for testing.
    """
    try:
        # Create a mock interview response
        interview_id = str(uuid.uuid4())
        return {
            "id": interview_id,
            "interview_id": interview_id,
            "candidate_id": request.get("candidate_id"),
            "interviewer_id": request.get("interviewer_id"),
            "scheduled_time": request.get("scheduled_time"),
            "duration": request.get("duration", 60),
            "type": request.get("type", "TECHNICAL"),
            "status": "scheduled",
            "meeting_link": request.get("meeting_link"),
            "notes": request.get("notes", ""),
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export the main scheduling function
__all__ = [
    'router',
    'schedule_interview_endpoint',
    'get_interview_status', 
    'list_scheduled_interviews',
    'InterviewScheduleRequest',
    'InterviewResponse',
    'InterviewConfirmationResponse',
    'InterviewDB',
    'InterviewStatus',
    'InterviewType'
]
