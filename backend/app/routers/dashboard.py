"""
Interview Dashboard API
======================

Comprehensive dashboard endpoints for viewing and managing scheduled interviews.
Provides detailed interview information with proper JOIN queries and formatted responses.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta, date
from enum import Enum
import logging

# Import existing components
from app.models.models import Candidate, Interview, User, InterviewStatus, InterviewType
from app.core.database import get_db, SessionLocal
InterviewDB = Interview
CandidateDB = Candidate
from app.models.models import InterviewResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    """Available sort fields"""
    SCHEDULED_TIME = "scheduled_time"
    CREATED_AT = "created_at"
    CANDIDATE_NAME = "candidate_name"
    INTERVIEWER_NAME = "interviewer_name"
    STATUS = "status"
    AI_MATCH_SCORE = "ai_match_score"

class InterviewDashboardItem(BaseModel):
    """Comprehensive interview item for dashboard display"""
    # Basic interview information
    interview_id: str
    status: str
    interview_type: str
    interview_round: int
    
    # Timing information
    scheduled_time: datetime
    duration_minutes: int
    time_until_interview: Optional[str] = None
    is_upcoming: bool
    is_overdue: bool
    
    # Candidate information
    candidate_id: str
    candidate_name: str
    candidate_email: str
    candidate_position: str
    candidate_experience_years: float
    candidate_ai_score: Optional[float] = None
    candidate_status: str
    
    # Interviewer information
    interviewer_id: str
    interviewer_name: str
    interviewer_email: str
    interviewer_department: Optional[str] = None
    
    # AI and matching information
    ai_match_score: Optional[float] = None
    ai_match_confidence: Optional[float] = None
    ai_recommended_focus_areas: List[str] = []
    
    # Calendar and meeting information
    calendar_event_id: Optional[str] = None
    calendar_event_link: Optional[str] = None
    google_meet_link: Optional[str] = None
    calendar_invites_sent: bool = False
    
    # Interview logistics
    is_remote: bool = True
    location: Optional[str] = None
    additional_attendees: List[str] = []
    
    # Preparation and notes
    preparation_materials: List[Dict[str, str]] = []
    interview_notes: Optional[str] = None
    technical_requirements: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    
    # Status indicators
    automation_score: int = 0  # 0-4 based on automation features
    status_color: str = "gray"  # For UI status indication
    priority_level: str = "normal"  # high, normal, low

class InterviewDashboardResponse(BaseModel):
    """Dashboard response with interviews and metadata"""
    interviews: List[InterviewDashboardItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    # Summary statistics
    summary: Dict[str, Any]
    
    # Filter and sort information
    applied_filters: Dict[str, Any]
    sort_field: str
    sort_order: str

class InterviewDashboardFilters(BaseModel):
    """Available filters for interview dashboard"""
    # Time-based filters
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    time_range: Optional[str] = None  # "today", "this_week", "next_week", "this_month"
    
    # Status filters
    status: Optional[List[InterviewStatus]] = None
    interview_type: Optional[List[InterviewType]] = None
    
    # Participant filters
    candidate_id: Optional[str] = None
    interviewer_email: Optional[str] = None
    interviewer_department: Optional[str] = None
    
    # Automation filters
    has_calendar_event: Optional[bool] = None
    has_google_meet: Optional[bool] = None
    notifications_sent: Optional[bool] = None
    
    # AI and matching filters
    min_ai_score: Optional[float] = None
    max_ai_score: Optional[float] = None
    min_match_score: Optional[float] = None
    
    # Logistics filters
    is_remote: Optional[bool] = None
    is_upcoming: Optional[bool] = None
    is_overdue: Optional[bool] = None

async def get_interviews_dashboard(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    
    # Sorting
    sort_field: SortField = Query(SortField.SCHEDULED_TIME, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    
    # Time filters
    from_date: Optional[date] = Query(None, description="Filter interviews from this date"),
    to_date: Optional[date] = Query(None, description="Filter interviews until this date"),
    time_range: Optional[str] = Query(None, description="Predefined time range: today, this_week, next_week, this_month"),
    
    # Status filters
    status: Optional[List[str]] = Query(None, description="Filter by interview status"),
    interview_type: Optional[List[str]] = Query(None, description="Filter by interview type"),
    
    # Participant filters
    candidate_id: Optional[str] = Query(None, description="Filter by candidate ID"),
    interviewer_email: Optional[str] = Query(None, description="Filter by interviewer email"),
    
    # Automation filters
    has_calendar_event: Optional[bool] = Query(None, description="Filter by calendar event presence"),
    has_google_meet: Optional[bool] = Query(None, description="Filter by Google Meet link presence"),
    notifications_sent: Optional[bool] = Query(None, description="Filter by notification status"),
    
    # AI filters
    min_ai_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum candidate AI score"),
    min_match_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum AI match score"),
    
    # Logistics filters
    is_remote: Optional[bool] = Query(None, description="Filter by remote/in-person"),
    is_upcoming: Optional[bool] = Query(None, description="Filter upcoming interviews"),
    
    db: Session = Depends(get_db)
) -> InterviewDashboardResponse:
    """
    Comprehensive interview dashboard endpoint with JOIN queries and detailed formatting
    
    Returns all scheduled interviews with:
    - Complete candidate and interviewer details
    - Interview status, timing, and meeting links
    - AI matching scores and recommendations
    - Calendar integration status
    - Proper pagination and filtering
    - Summary statistics
    """
    
    try:
        logger.info(f"📊 Getting interview dashboard - Page {page}, Size {page_size}")
        
        # Build base query with JOINs
        base_query = db.query(InterviewDB).join(
            CandidateDB, InterviewDB.candidate_id == CandidateDB.id
        ).options(
            joinedload(InterviewDB.candidate)
        )
        
        # Apply time range filters
        current_time = datetime.utcnow()
        
        if time_range:
            if time_range == "today":
                start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                base_query = base_query.filter(
                    and_(
                        InterviewDB.scheduled_time >= start_of_day,
                        InterviewDB.scheduled_time < end_of_day
                    )
                )
            elif time_range == "this_week":
                days_since_monday = current_time.weekday()
                start_of_week = current_time - timedelta(days=days_since_monday)
                start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_week = start_of_week + timedelta(days=7)
                base_query = base_query.filter(
                    and_(
                        InterviewDB.scheduled_time >= start_of_week,
                        InterviewDB.scheduled_time < end_of_week
                    )
                )
            elif time_range == "next_week":
                days_since_monday = current_time.weekday()
                next_monday = current_time + timedelta(days=(7 - days_since_monday))
                next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_next_week = next_monday + timedelta(days=7)
                base_query = base_query.filter(
                    and_(
                        InterviewDB.scheduled_time >= next_monday,
                        InterviewDB.scheduled_time < end_of_next_week
                    )
                )
            elif time_range == "this_month":
                start_of_month = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if current_time.month == 12:
                    end_of_month = start_of_month.replace(year=current_time.year + 1, month=1)
                else:
                    end_of_month = start_of_month.replace(month=current_time.month + 1)
                base_query = base_query.filter(
                    and_(
                        InterviewDB.scheduled_time >= start_of_month,
                        InterviewDB.scheduled_time < end_of_month
                    )
                )
        
        # Apply date range filters
        if from_date:
            from_datetime = datetime.combine(from_date, datetime.min.time())
            base_query = base_query.filter(InterviewDB.scheduled_time >= from_datetime)
        
        if to_date:
            to_datetime = datetime.combine(to_date, datetime.max.time())
            base_query = base_query.filter(InterviewDB.scheduled_time <= to_datetime)
        
        # Apply status filters
        if status:
            base_query = base_query.filter(InterviewDB.status.in_(status))
        
        if interview_type:
            base_query = base_query.filter(InterviewDB.interview_type.in_(interview_type))
        
        # Apply participant filters
        if candidate_id:
            base_query = base_query.filter(InterviewDB.candidate_id == candidate_id)
        
        if interviewer_email:
            base_query = base_query.filter(InterviewDB.interviewer_email == interviewer_email)
        
        # Apply automation filters
        if has_calendar_event is not None:
            if has_calendar_event:
                base_query = base_query.filter(InterviewDB.calendar_event_id.isnot(None))
            else:
                base_query = base_query.filter(InterviewDB.calendar_event_id.is_(None))
        
        if has_google_meet is not None:
            if has_google_meet:
                base_query = base_query.filter(InterviewDB.google_meet_link.isnot(None))
            else:
                base_query = base_query.filter(InterviewDB.google_meet_link.is_(None))
        
        if notifications_sent is not None:
            base_query = base_query.filter(InterviewDB.calendar_invites_sent == notifications_sent)
        
        # Apply AI filters
        if min_ai_score is not None:
            base_query = base_query.filter(CandidateDB.ai_overall_score >= min_ai_score)
        
        if min_match_score is not None:
            base_query = base_query.filter(InterviewDB.ai_match_score >= min_match_score)
        
        # Apply logistics filters
        if is_remote is not None:
            base_query = base_query.filter(InterviewDB.is_remote == is_remote)
        
        if is_upcoming is not None:
            if is_upcoming:
                base_query = base_query.filter(InterviewDB.scheduled_time > current_time)
            else:
                base_query = base_query.filter(InterviewDB.scheduled_time <= current_time)
        
        # Get total count before pagination
        total_count = base_query.count()
        
        # Apply sorting
        if sort_field == SortField.SCHEDULED_TIME:
            sort_column = InterviewDB.scheduled_time
        elif sort_field == SortField.CREATED_AT:
            sort_column = InterviewDB.created_at
        elif sort_field == SortField.CANDIDATE_NAME:
            sort_column = CandidateDB.name
        elif sort_field == SortField.INTERVIEWER_NAME:
            sort_column = InterviewDB.interviewer_name
        elif sort_field == SortField.STATUS:
            sort_column = InterviewDB.status
        elif sort_field == SortField.AI_MATCH_SCORE:
            sort_column = InterviewDB.ai_match_score
        else:
            sort_column = InterviewDB.scheduled_time
        
        if sort_order == SortOrder.DESC:
            base_query = base_query.order_by(desc(sort_column))
        else:
            base_query = base_query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * page_size
        interviews = base_query.offset(offset).limit(page_size).all()
        
        # Format interviews for dashboard
        dashboard_items = []
        for interview in interviews:
            candidate = interview.candidate
            
            # Calculate time until interview
            time_diff = interview.scheduled_time - current_time
            time_until_interview = None
            is_upcoming = time_diff.total_seconds() > 0
            is_overdue = not is_upcoming and interview.status not in [InterviewStatus.COMPLETED, InterviewStatus.CANCELLED]
            
            if is_upcoming:
                if time_diff.days > 0:
                    time_until_interview = f"in {time_diff.days} days"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_until_interview = f"in {hours} hours"
                else:
                    minutes = time_diff.seconds // 60
                    time_until_interview = f"in {minutes} minutes"
            elif is_overdue:
                abs_time_diff = abs(time_diff)
                if abs_time_diff.days > 0:
                    time_until_interview = f"{abs_time_diff.days} days overdue"
                elif abs_time_diff.seconds > 3600:
                    hours = abs_time_diff.seconds // 3600
                    time_until_interview = f"{hours} hours overdue"
                else:
                    minutes = abs_time_diff.seconds // 60
                    time_until_interview = f"{minutes} minutes overdue"
            
            # Calculate automation score (0-4)
            automation_score = 0
            if interview.calendar_event_id:
                automation_score += 1
            if interview.google_meet_link:
                automation_score += 1
            if interview.calendar_invites_sent:
                automation_score += 1
            if interview.ai_match_score and interview.ai_match_score > 0:
                automation_score += 1
            
            # Determine status color for UI
            status_colors = {
                InterviewStatus.SCHEDULED: "blue",
                InterviewStatus.CONFIRMED: "green",
                InterviewStatus.IN_PROGRESS: "yellow",
                InterviewStatus.COMPLETED: "gray",
                InterviewStatus.CANCELLED: "red",
                InterviewStatus.RESCHEDULED: "orange",
                InterviewStatus.NO_SHOW: "red"
            }
            status_color = status_colors.get(interview.status, "gray")
            
            # Determine priority level
            priority_level = "normal"
            if is_overdue:
                priority_level = "high"
            elif is_upcoming and time_diff.total_seconds() < 3600:  # Less than 1 hour
                priority_level = "high"
            elif automation_score < 2:  # Low automation
                priority_level = "high"
            
            dashboard_item = InterviewDashboardItem(
                # Basic interview information
                interview_id=interview.id,
                status=interview.status,
                interview_type=interview.interview_type,
                interview_round=interview.interview_round,
                
                # Timing information
                scheduled_time=interview.scheduled_time,
                duration_minutes=interview.duration_minutes,
                time_until_interview=time_until_interview,
                is_upcoming=is_upcoming,
                is_overdue=is_overdue,
                
                # Candidate information
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                candidate_position=candidate.position,
                candidate_experience_years=candidate.experience_years,
                candidate_ai_score=candidate.ai_overall_score,
                candidate_status=candidate.status,
                
                # Interviewer information
                interviewer_id=interview.interviewer_id,
                interviewer_name=interview.interviewer_name,
                interviewer_email=interview.interviewer_email,
                interviewer_department=None,  # Would need interviewer table for this
                
                # AI and matching information
                ai_match_score=interview.ai_match_score,
                ai_match_confidence=interview.ai_match_confidence,
                ai_recommended_focus_areas=interview.ai_recommended_focus_areas or [],
                
                # Calendar and meeting information
                calendar_event_id=interview.calendar_event_id,
                calendar_event_link=interview.calendar_event_link,
                google_meet_link=interview.google_meet_link,
                calendar_invites_sent=interview.calendar_invites_sent,
                
                # Interview logistics
                is_remote=interview.is_remote,
                location=interview.location,
                additional_attendees=interview.additional_attendees or [],
                
                # Preparation and notes
                preparation_materials=interview.preparation_materials or [],
                interview_notes=interview.interview_notes,
                technical_requirements=interview.technical_requirements or {},
                
                # Timestamps
                created_at=interview.created_at,
                updated_at=interview.updated_at,
                confirmed_at=interview.confirmed_at,
                
                # Status indicators
                automation_score=automation_score,
                status_color=status_color,
                priority_level=priority_level
            )
            
            dashboard_items.append(dashboard_item)
        
        # Calculate summary statistics
        summary = await _calculate_dashboard_summary(db, base_query, current_time)
        
        # Prepare applied filters summary
        applied_filters = {
            "time_range": time_range,
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
            "status": status,
            "interview_type": interview_type,
            "candidate_id": candidate_id,
            "interviewer_email": interviewer_email,
            "has_calendar_event": has_calendar_event,
            "has_google_meet": has_google_meet,
            "notifications_sent": notifications_sent,
            "min_ai_score": min_ai_score,
            "min_match_score": min_match_score,
            "is_remote": is_remote,
            "is_upcoming": is_upcoming
        }
        
        # Remove None values from applied filters
        applied_filters = {k: v for k, v in applied_filters.items() if v is not None}
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        
        response = InterviewDashboardResponse(
            interviews=dashboard_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            summary=summary,
            applied_filters=applied_filters,
            sort_field=sort_field.value,
            sort_order=sort_order.value
        )
        
        logger.info(f"📊 Dashboard query completed - {len(dashboard_items)} interviews returned")
        logger.info(f"   Total: {total_count}, Page: {page}/{total_pages}")
        logger.info(f"   Filters: {len(applied_filters)} active")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Dashboard query failed: {e}")
        logger.exception("Dashboard error details:")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )

async def _calculate_dashboard_summary(
    db: Session,
    base_query,
    current_time: datetime
) -> Dict[str, Any]:
    """Calculate summary statistics for the dashboard"""
    
    try:
        # Get all interviews matching the filters (without pagination)
        all_interviews = base_query.all()
        
        # Basic counts
        total_interviews = len(all_interviews)
        
        # Status breakdown
        status_counts = {}
        for status in InterviewStatus:
            status_counts[status.value] = sum(1 for i in all_interviews if i.status == status.value)
        
        # Interview type breakdown
        type_counts = {}
        for interview_type in InterviewType:
            type_counts[interview_type.value] = sum(1 for i in all_interviews if i.interview_type == interview_type.value)
        
        # Time-based statistics
        upcoming_interviews = [i for i in all_interviews if i.scheduled_time > current_time]
        past_interviews = [i for i in all_interviews if i.scheduled_time <= current_time]
        overdue_interviews = [
            i for i in past_interviews 
            if i.status not in [InterviewStatus.COMPLETED, InterviewStatus.CANCELLED]
        ]
        
        # Today's interviews
        start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        today_interviews = [
            i for i in all_interviews 
            if start_of_day <= i.scheduled_time < end_of_day
        ]
        
        # Automation statistics
        calendar_events_created = sum(1 for i in all_interviews if i.calendar_event_id)
        google_meet_links = sum(1 for i in all_interviews if i.google_meet_link)
        notifications_sent = sum(1 for i in all_interviews if i.calendar_invites_sent)
        ai_matched = sum(1 for i in all_interviews if i.ai_match_score and i.ai_match_score > 0)
        
        # AI and scoring statistics
        ai_scores = [i.ai_match_score for i in all_interviews if i.ai_match_score]
        candidate_scores = [i.candidate.ai_overall_score for i in all_interviews if i.candidate and i.candidate.ai_overall_score]
        
        summary = {
            "total_interviews": total_interviews,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "time_statistics": {
                "upcoming_count": len(upcoming_interviews),
                "past_count": len(past_interviews),
                "overdue_count": len(overdue_interviews),
                "today_count": len(today_interviews)
            },
            "automation_statistics": {
                "calendar_events_created": calendar_events_created,
                "google_meet_links_generated": google_meet_links,
                "notifications_sent": notifications_sent,
                "ai_matched_interviews": ai_matched,
                "automation_rate": round((calendar_events_created / total_interviews * 100) if total_interviews > 0 else 0, 1)
            },
            "ai_statistics": {
                "average_match_score": round(sum(ai_scores) / len(ai_scores), 1) if ai_scores else 0,
                "average_candidate_score": round(sum(candidate_scores) / len(candidate_scores), 1) if candidate_scores else 0,
                "max_match_score": max(ai_scores) if ai_scores else 0,
                "min_match_score": min(ai_scores) if ai_scores else 0
            },
            "remote_vs_onsite": {
                "remote_count": sum(1 for i in all_interviews if i.is_remote),
                "onsite_count": sum(1 for i in all_interviews if not i.is_remote)
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error calculating dashboard summary: {e}")
        return {
            "total_interviews": 0,
            "error": "Failed to calculate summary statistics"
        }

# Export dashboard components
__all__ = [
    'get_interviews_dashboard',
    'InterviewDashboardItem',
    'InterviewDashboardResponse',
    'InterviewDashboardFilters',
    'SortField',
    'SortOrder'
]
