"""
Google Calendar API endpoints for the Interview Scheduling System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
import logging

from database import get_db
from models import Interview, User, Candidate, InterviewStatus
from calendar_integration import (
    get_calendar_integration,
    check_availability_before_scheduling,
    schedule_interview_with_calendar
)
from google_calendar_config import get_calendar_timezone

logger = logging.getLogger(__name__)

# Create router for calendar endpoints
calendar_router = APIRouter(prefix="/api/calendar", tags=["Google Calendar"])

# Pydantic models for calendar API
class AvailabilityRequest(BaseModel):
    email: EmailStr
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 60
    timezone: str = "Asia/Kolkata"
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v < 15 or v > 480:
            raise ValueError('duration_minutes must be between 15 and 480')
        return v

class MutualAvailabilityRequest(BaseModel):
    emails: List[EmailStr]
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 60
    max_suggestions: int = 5
    timezone: str = "Asia/Kolkata"
    
    @validator('emails')
    def validate_emails(cls, v):
        if len(v) < 1:
            raise ValueError('At least one email is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 emails allowed')
        return v

class CalendarEventCreate(BaseModel):
    interview_id: int
    send_invitations: bool = True
    additional_attendees: Optional[List[EmailStr]] = None

class CalendarEventUpdate(BaseModel):
    send_updates: str = "all"  # all, externalOnly, none

class AvailabilityResponse(BaseModel):
    email: str
    timezone: str
    query_start: datetime
    query_end: datetime
    available: bool
    free_slots: List[Dict[str, Any]]
    busy_periods: List[Dict[str, Any]]

class CalendarEventResponse(BaseModel):
    event_id: str
    interview_id: int
    status: str
    event_url: Optional[str] = None
    meet_link: Optional[str] = None

# Calendar endpoints
@calendar_router.get("/health")
def calendar_health_check():
    """Check Google Calendar service health"""
    try:
        calendar_integration = get_calendar_integration()
        if calendar_integration.calendar_service:
            return {
                "status": "healthy",
                "service": "Google Calendar",
                "authenticated": True,
                "timezone": get_calendar_timezone()
            }
        else:
            return {
                "status": "unhealthy",
                "service": "Google Calendar",
                "authenticated": False,
                "error": "Calendar service not initialized"
            }
    except Exception as e:
        logger.error(f"Calendar health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "Google Calendar",
            "authenticated": False,
            "error": str(e)
        }

@calendar_router.post("/availability/check", response_model=Dict[str, Any])
def check_availability(
    request: AvailabilityRequest,
    db: Session = Depends(get_db)
):
    """
    Check availability for a specific user
    """
    try:
        calendar_integration = get_calendar_integration()
        
        if not calendar_integration.calendar_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google Calendar service not available"
            )
        
        # Verify user exists in our system
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.warning(f"Availability check for non-existent user: {request.email}")
        
        # Get availability from Google Calendar
        availability = calendar_integration.calendar_service.get_availability(
            email=request.email,
            start_date=request.start_date,
            end_date=request.end_date,
            timezone=request.timezone
        )
        
        if 'error' in availability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Calendar API error: {availability['error']}"
            )
        
        # Format response
        return {
            "email": request.email,
            "timezone": request.timezone,
            "query_period": {
                "start": request.start_date.isoformat(),
                "end": request.end_date.isoformat()
            },
            "free_slots": availability['free'],
            "busy_periods": availability['busy'],
            "total_free_slots": len(availability['free']),
            "total_busy_periods": len(availability['busy'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check availability"
        )

@calendar_router.post("/availability/mutual", response_model=List[Dict[str, Any]])
def find_mutual_availability(
    request: MutualAvailabilityRequest,
    db: Session = Depends(get_db)
):
    """
    Find mutual availability for multiple users
    """
    try:
        calendar_integration = get_calendar_integration()
        
        if not calendar_integration.calendar_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google Calendar service not available"
            )
        
        # Verify all users exist in our system
        existing_users = db.query(User).filter(User.email.in_(request.emails)).all()
        existing_emails = {user.email for user in existing_users}
        missing_emails = set(request.emails) - existing_emails
        
        if missing_emails:
            logger.warning(f"Mutual availability check includes non-existent users: {missing_emails}")
        
        # Find mutual availability
        mutual_slots = calendar_integration.suggest_interview_times(
            interviewer_emails=request.emails,
            start_date=request.start_date,
            end_date=request.end_date,
            duration_minutes=request.duration_minutes,
            max_suggestions=request.max_suggestions
        )
        
        return mutual_slots
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding mutual availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find mutual availability"
        )

@calendar_router.post("/events/create", response_model=CalendarEventResponse)
def create_calendar_event(
    request: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """
    Create a Google Calendar event for an existing interview
    """
    try:
        # Get interview with related data
        interview = db.query(Interview).filter(Interview.id == request.interview_id).first()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with ID {request.interview_id} not found"
            )
        
        # Check if calendar event already exists
        if interview.google_event_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Calendar event already exists for this interview"
            )
        
        # Get candidate and interviewer
        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        interviewer = db.query(User).filter(User.id == interview.interviewer_id).first()
        
        if not candidate or not interviewer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid candidate or interviewer for interview"
            )
        
        # Create calendar event
        calendar_integration = get_calendar_integration()
        event_id = calendar_integration.create_interview_event(
            interview=interview,
            candidate=candidate,
            interviewer=interviewer,
            db_session=db
        )
        
        if not event_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create calendar event"
            )
        
        return CalendarEventResponse(
            event_id=event_id,
            interview_id=interview.id,
            status="created",
            event_url=f"https://calendar.google.com/calendar/event?eid={event_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create calendar event"
        )

@calendar_router.put("/events/{interview_id}", response_model=CalendarEventResponse)
def update_calendar_event(
    interview_id: int,
    request: CalendarEventUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing Google Calendar event
    """
    try:
        # Get interview
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with ID {interview_id} not found"
            )
        
        if not interview.google_event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No calendar event exists for this interview"
            )
        
        # Update calendar event
        calendar_integration = get_calendar_integration()
        success = calendar_integration.update_interview_event(
            interview=interview,
            db_session=db,
            send_updates=request.send_updates
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update calendar event"
            )
        
        return CalendarEventResponse(
            event_id=interview.google_event_id,
            interview_id=interview.id,
            status="updated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating calendar event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update calendar event"
        )

@calendar_router.delete("/events/{interview_id}")
def cancel_calendar_event(
    interview_id: int,
    send_updates: str = Query("all", regex="^(all|externalOnly|none)$"),
    db: Session = Depends(get_db)
):
    """
    Cancel/delete a Google Calendar event
    """
    try:
        # Get interview
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with ID {interview_id} not found"
            )
        
        if not interview.google_event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No calendar event exists for this interview"
            )
        
        # Cancel calendar event
        calendar_integration = get_calendar_integration()
        success = calendar_integration.cancel_interview_event(
            interview=interview,
            db_session=db,
            send_updates=send_updates
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel calendar event"
            )
        
        return {"message": "Calendar event cancelled successfully", "interview_id": interview_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling calendar event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel calendar event"
        )

@calendar_router.get("/suggest-times")
def suggest_interview_times(
    interviewer_emails: List[str] = Query(..., description="List of interviewer email addresses"),
    start_date: datetime = Query(..., description="Start of search period"),
    end_date: datetime = Query(..., description="End of search period"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Interview duration in minutes"),
    max_suggestions: int = Query(5, ge=1, le=20, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get suggested interview times based on interviewer availability
    """
    try:
        if len(interviewer_emails) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 interviewers allowed"
            )
        
        # Verify interviewers exist
        existing_users = db.query(User).filter(User.email.in_(interviewer_emails)).all()
        existing_emails = {user.email for user in existing_users}
        missing_emails = set(interviewer_emails) - existing_emails
        
        if missing_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown interviewer emails: {list(missing_emails)}"
            )
        
        # Get suggested times
        calendar_integration = get_calendar_integration()
        suggestions = calendar_integration.suggest_interview_times(
            interviewer_emails=interviewer_emails,
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration_minutes,
            max_suggestions=max_suggestions
        )
        
        return {
            "suggestions": suggestions,
            "criteria": {
                "interviewers": interviewer_emails,
                "duration_minutes": duration_minutes,
                "search_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            },
            "total_suggestions": len(suggestions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting interview times: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suggest interview times"
        )

@calendar_router.post("/interviews/schedule-with-calendar")
def schedule_interview_with_calendar_endpoint(
    interview_id: int,
    check_availability: bool = True,
    db: Session = Depends(get_db)
):
    """
    Schedule an interview and automatically create calendar event
    """
    try:
        # Get interview with related data
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with ID {interview_id} not found"
            )
        
        if interview.status != InterviewStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview must be in scheduled status"
            )
        
        # Get candidate and interviewer
        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
        interviewer = db.query(User).filter(User.id == interview.interviewer_id).first()
        
        # Check availability if requested
        if check_availability:
            availability_result = check_availability_before_scheduling(
                interviewer_email=interviewer.email,
                proposed_time=interview.scheduled_time,
                duration_minutes=interview.duration
            )
            
            if not availability_result.get('available', False):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Interviewer not available at proposed time",
                        "conflicts": availability_result.get('conflicts', []),
                        "availability_check": availability_result
                    }
                )
        
        # Create calendar event
        event_id = schedule_interview_with_calendar(
            interview=interview,
            candidate=candidate,
            interviewer=interviewer,
            db_session=db
        )
        
        if not event_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create calendar event"
            )
        
        return {
            "message": "Interview scheduled with calendar event",
            "interview_id": interview.id,
            "calendar_event_id": event_id,
            "scheduled_time": interview.scheduled_time.isoformat(),
            "interviewer": interviewer.email,
            "candidate": candidate.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling interview with calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule interview with calendar"
        )
