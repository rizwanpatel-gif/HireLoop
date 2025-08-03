"""
Google Calendar Event Creation Functions
Ready-to-use functions for creating calendar events with Google Meet integration
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def create_interview_calendar_event(
    candidate_name: str,
    candidate_email: str,
    position: str,
    interviewer_email: str,
    interview_datetime: datetime,
    duration_minutes: int = 60,
    interview_type: str = "Technical",
    notes: str = "",
    additional_attendees: List[str] = None
) -> Optional[str]:
    """
    Create a Google Calendar event for an interview with comprehensive features
    
    Features:
    - Meeting title with candidate name and position
    - Automatic Google Meet link generation
    - Email invitations to candidate and interviewer
    - Reminders set for 24 hours and 30 minutes before
    - Returns event ID for database storage
    
    Args:
        candidate_name: Full name of the candidate
        candidate_email: Candidate's email address
        position: Position being interviewed for
        interviewer_email: Interviewer's email address
        interview_datetime: Interview start time (should be timezone-aware)
        duration_minutes: Interview duration in minutes (default: 60)
        interview_type: Type of interview (Technical, HR, Cultural, etc.)
        notes: Additional notes or instructions
        additional_attendees: List of additional email addresses to invite
        
    Returns:
        str: Google Calendar event ID if successful, None otherwise
        
    Example:
        event_id = create_interview_calendar_event(
            candidate_name="John Doe",
            candidate_email="john.doe@email.com",
            position="Senior Python Developer",
            interviewer_email="interviewer@company.com",
            interview_datetime=datetime(2025, 8, 15, 14, 0, tzinfo=timezone.utc),
            duration_minutes=90,
            interview_type="Technical",
            notes="Focus on Python, algorithms, and system design"
        )
    """
    try:
        from google_calendar_service import GoogleCalendarService
        
        # Initialize calendar service
        calendar_service = GoogleCalendarService()
        
        # Check authentication
        if not calendar_service.is_authenticated(interviewer_email):
            logger.error(f"Interviewer {interviewer_email} is not authenticated with Google Calendar")
            return None
        
        # Prepare enhanced title
        title = f"{interview_type} Interview - {candidate_name} ({position})"
        
        # Create comprehensive event using the enhanced function
        result = calendar_service.create_calendar_event_with_details(
            title=title,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            position=position,
            interviewer_name=interviewer_email.split('@')[0].title(),
            interviewer_email=interviewer_email,
            start_datetime=interview_datetime,
            duration_minutes=duration_minutes,
            interview_type=interview_type,
            notes=notes,
            additional_attendees=additional_attendees
        )
        
        if result:
            logger.info(f"✅ Calendar event created: {title}")
            logger.info(f"   Event ID: {result['event_id']}")
            logger.info(f"   Google Meet: {result.get('meet_link', 'Generating...')}")
            return result['event_id']
        else:
            logger.error(f"❌ Failed to create calendar event for {candidate_name}")
            return None
            
    except ImportError:
        logger.error("Google Calendar service not available")
        return None
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return None

def create_calendar_event_from_interview_data(interview_data: Dict) -> Optional[str]:
    """
    Create a calendar event from interview database record
    
    This function is designed to work with the Interview model from your database.
    
    Args:
        interview_data: Dictionary containing interview details with keys:
            - candidate_name: str
            - candidate_email: str
            - position: str (optional, will extract from candidate data)
            - interviewer_email: str
            - scheduled_time: datetime
            - duration: int (minutes)
            - type: str or enum
            - notes: str (optional)
            
    Returns:
        str: Google Calendar event ID if successful, None otherwise
        
    Example:
        interview_data = {
            'candidate_name': 'Jane Smith',
            'candidate_email': 'jane.smith@email.com',
            'position': 'Frontend Developer',
            'interviewer_email': 'hiring.manager@company.com',
            'scheduled_time': datetime(2025, 8, 15, 10, 0, tzinfo=timezone.utc),
            'duration': 60,
            'type': 'technical',
            'notes': 'React and JavaScript focus'
        }
        
        event_id = create_calendar_event_from_interview_data(interview_data)
    """
    try:
        # Extract and validate required fields
        required_fields = ['candidate_name', 'candidate_email', 'interviewer_email', 'scheduled_time']
        for field in required_fields:
            if field not in interview_data or not interview_data[field]:
                logger.error(f"Missing required field: {field}")
                return None
        
        # Extract data with defaults
        candidate_name = interview_data['candidate_name']
        candidate_email = interview_data['candidate_email']
        position = interview_data.get('position', 'Position TBD')
        interviewer_email = interview_data['interviewer_email']
        scheduled_time = interview_data['scheduled_time']
        duration = interview_data.get('duration', 60)
        interview_type = str(interview_data.get('type', 'Interview')).title()
        notes = interview_data.get('notes', '')
        
        # Create the calendar event
        return create_interview_calendar_event(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            position=position,
            interviewer_email=interviewer_email,
            interview_datetime=scheduled_time,
            duration_minutes=duration,
            interview_type=interview_type,
            notes=notes
        )
        
    except Exception as e:
        logger.error(f"Error creating calendar event from interview data: {e}")
        return None

def update_interview_with_calendar_event(interview_record, db_session) -> bool:
    """
    Create calendar event and update interview record with event ID
    
    This function works with SQLAlchemy models and automatically updates
    the interview record with the Google Calendar event ID.
    
    Args:
        interview_record: SQLAlchemy Interview model instance
        db_session: Database session
        
    Returns:
        bool: True if calendar event created and record updated successfully
        
    Example:
        # In your FastAPI endpoint or service
        interview = Interview(...)
        db.add(interview)
        db.flush()  # Get ID
        
        if update_interview_with_calendar_event(interview, db):
            print(f"Calendar event created: {interview.google_event_id}")
        else:
            print("Failed to create calendar event")
    """
    try:
        # Prepare interview data from the record
        interview_data = {
            'candidate_name': interview_record.candidate.name,
            'candidate_email': interview_record.candidate.email,
            'position': interview_record.candidate.position,
            'interviewer_email': interview_record.interviewer.email,
            'scheduled_time': interview_record.scheduled_time,
            'duration': interview_record.duration,
            'type': interview_record.type.value if hasattr(interview_record.type, 'value') else str(interview_record.type),
            'notes': interview_record.notes or f"Interview for {interview_record.candidate.position} position"
        }
        
        # Create calendar event
        event_id = create_calendar_event_from_interview_data(interview_data)
        
        if event_id:
            # Update interview record with event ID
            interview_record.google_event_id = event_id
            db_session.commit()
            
            logger.info(f"✅ Interview {interview_record.id} updated with calendar event {event_id}")
            return True
        else:
            logger.error(f"❌ Failed to create calendar event for interview {interview_record.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating interview with calendar event: {e}")
        db_session.rollback()
        return False

def get_calendar_event_details(event_id: str, user_email: str) -> Optional[Dict]:
    """
    Get details of a calendar event by ID
    
    Args:
        event_id: Google Calendar event ID
        user_email: Email of authenticated user
        
    Returns:
        Dict with event details or None if not found
    """
    try:
        from google_calendar_service import GoogleCalendarService
        
        calendar_service = GoogleCalendarService()
        
        if not calendar_service.is_authenticated(user_email):
            logger.error(f"User {user_email} not authenticated")
            return None
        
        # Get event details
        event = calendar_service.service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Extract relevant information
        details = {
            'id': event.get('id'),
            'title': event.get('summary'),
            'description': event.get('description'),
            'start_time': event.get('start', {}).get('dateTime'),
            'end_time': event.get('end', {}).get('dateTime'),
            'attendees': [
                {
                    'email': attendee.get('email'),
                    'response_status': attendee.get('responseStatus'),
                    'display_name': attendee.get('displayName')
                }
                for attendee in event.get('attendees', [])
            ],
            'meet_link': None,
            'event_link': event.get('htmlLink'),
            'status': event.get('status')
        }
        
        # Extract Google Meet link
        conference_data = event.get('conferenceData', {})
        for entry_point in conference_data.get('entryPoints', []):
            if entry_point.get('entryPointType') == 'video':
                details['meet_link'] = entry_point.get('uri')
                break
        
        return details
        
    except Exception as e:
        logger.error(f"Error getting calendar event details: {e}")
        return None

def cancel_calendar_event(event_id: str, user_email: str, send_updates: bool = True) -> bool:
    """
    Cancel a calendar event
    
    Args:
        event_id: Google Calendar event ID
        user_email: Email of authenticated user
        send_updates: Whether to send cancellation emails to attendees
        
    Returns:
        bool: True if cancelled successfully
    """
    try:
        from google_calendar_service import GoogleCalendarService
        
        calendar_service = GoogleCalendarService()
        
        if not calendar_service.is_authenticated(user_email):
            logger.error(f"User {user_email} not authenticated")
            return False
        
        # Cancel the event
        calendar_service.service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates='all' if send_updates else 'none'
        ).execute()
        
        logger.info(f"✅ Calendar event {event_id} cancelled")
        return True
        
    except Exception as e:
        logger.error(f"Error cancelling calendar event: {e}")
        return False

# Example usage functions
def example_usage():
    """
    Example of how to use the calendar event creation functions
    """
    from datetime import datetime, timezone
    
    print("📅 Calendar Event Creation Examples")
    print("=" * 50)
    
    # Example 1: Simple event creation
    print("\n1. Simple Event Creation:")
    print("""
event_id = create_interview_calendar_event(
    candidate_name="John Doe",
    candidate_email="john.doe@email.com", 
    position="Software Engineer",
    interviewer_email="interviewer@company.com",
    interview_datetime=datetime(2025, 8, 15, 14, 0, tzinfo=timezone.utc),
    duration_minutes=60,
    interview_type="Technical"
)
    """)
    
    # Example 2: Event from interview data
    print("\n2. Event from Interview Data:")
    print("""
interview_data = {
    'candidate_name': 'Jane Smith',
    'candidate_email': 'jane.smith@email.com',
    'position': 'Frontend Developer', 
    'interviewer_email': 'hiring.manager@company.com',
    'scheduled_time': datetime(2025, 8, 15, 10, 0, tzinfo=timezone.utc),
    'duration': 90,
    'type': 'technical',
    'notes': 'React and JavaScript focus'
}

event_id = create_calendar_event_from_interview_data(interview_data)
    """)
    
    # Example 3: Database integration
    print("\n3. Database Integration:")
    print("""
# In your FastAPI endpoint
@app.post("/api/interviews/", response_model=InterviewResponse)
def create_interview_endpoint(interview: InterviewCreate, db: Session = Depends(get_db)):
    # Create interview record
    db_interview = Interview(**interview.dict())
    db.add(db_interview)
    db.flush()
    
    # Create calendar event and update record
    if update_interview_with_calendar_event(db_interview, db):
        logger.info(f"Interview scheduled with calendar event: {db_interview.google_event_id}")
    
    return db_interview
    """)
    
    print("\n✅ Features Provided:")
    print("• Automatic Google Meet link generation")
    print("• Email invitations to all attendees") 
    print("• Reminders: 24 hours, 30 minutes, 10 minutes before")
    print("• Professional event formatting")
    print("• Event ID returned for database storage")
    print("• Error handling and authentication checks")

if __name__ == "__main__":
    example_usage()
