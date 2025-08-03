"""
Integration layer for Google Calendar with Interview Scheduling System
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

from google_calendar_service import GoogleCalendarService, create_calendar_service
from google_calendar_config import get_google_credentials_path, get_calendar_timezone
from models import Interview, User, Candidate

logger = logging.getLogger(__name__)

class InterviewCalendarIntegration:
    """
    Integration class for managing interviews with Google Calendar
    """
    
    def __init__(self, credentials_file: str = None):
        """
        Initialize the calendar integration
        
        Args:
            credentials_file: Path to Google credentials file
        """
        self.credentials_file = credentials_file or get_google_credentials_path()
        self.calendar_service = None
        self._initialize_service()
    
    def _initialize_service(self) -> bool:
        """
        Initialize the Google Calendar service
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.calendar_service = create_calendar_service(self.credentials_file)
            logger.info("✅ Google Calendar service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            return False
    
    def create_interview_event(
        self,
        interview: Interview,
        candidate: Candidate,
        interviewer: User,
        db_session
    ) -> Optional[str]:
        """
        Create a calendar event for an interview and update the database
        
        Args:
            interview: Interview model instance
            candidate: Candidate model instance
            interviewer: User model instance
            db_session: Database session
            
        Returns:
            str: Google Calendar event ID if successful
        """
        try:
            if not self.calendar_service:
                logger.error("Calendar service not initialized")
                return None
            
            # Prepare interview data for calendar
            interview_data = {
                'id': interview.id,
                'scheduled_time': interview.scheduled_time,
                'duration': interview.duration,
                'type': interview.type.value,
                'candidate_name': candidate.name,
                'interviewer_name': interviewer.name,
                'notes': interview.notes or ''
            }
            
            # Create calendar event
            event_id = self.calendar_service.create_interview_event(
                interview_data=interview_data,
                candidate_email=candidate.email,
                interviewer_email=interviewer.email
            )
            
            if event_id:
                # Update interview with calendar event ID
                interview.google_event_id = event_id
                db_session.commit()
                logger.info(f"Interview {interview.id} linked to calendar event {event_id}")
                return event_id
            else:
                logger.error(f"Failed to create calendar event for interview {interview.id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating calendar event for interview {interview.id}: {e}")
            db_session.rollback()
            return None
    
    def update_interview_event(
        self,
        interview: Interview,
        db_session,
        send_updates: str = 'all'
    ) -> bool:
        """
        Update an existing calendar event for an interview
        
        Args:
            interview: Updated interview model instance
            db_session: Database session
            send_updates: Email notification setting
            
        Returns:
            bool: True if update successful
        """
        try:
            if not self.calendar_service or not interview.google_event_id:
                logger.warning(f"Cannot update calendar event for interview {interview.id}")
                return False
            
            # Prepare updated interview data
            interview_data = {
                'scheduled_time': interview.scheduled_time,
                'duration': interview.duration,
                'notes': interview.notes or ''
            }
            
            # Update calendar event
            success = self.calendar_service.update_interview_event(
                event_id=interview.google_event_id,
                interview_data=interview_data,
                send_updates=send_updates
            )
            
            if success:
                logger.info(f"Calendar event updated for interview {interview.id}")
            else:
                logger.error(f"Failed to update calendar event for interview {interview.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating calendar event for interview {interview.id}: {e}")
            return False
    
    def cancel_interview_event(
        self,
        interview: Interview,
        db_session,
        send_updates: str = 'all'
    ) -> bool:
        """
        Cancel/delete a calendar event for an interview
        
        Args:
            interview: Interview model instance
            db_session: Database session
            send_updates: Email notification setting
            
        Returns:
            bool: True if cancellation successful
        """
        try:
            if not self.calendar_service or not interview.google_event_id:
                logger.warning(f"Cannot cancel calendar event for interview {interview.id}")
                return False
            
            # Delete calendar event
            success = self.calendar_service.delete_interview_event(
                event_id=interview.google_event_id,
                send_updates=send_updates
            )
            
            if success:
                # Clear the Google event ID from interview
                interview.google_event_id = None
                db_session.commit()
                logger.info(f"Calendar event cancelled for interview {interview.id}")
            else:
                logger.error(f"Failed to cancel calendar event for interview {interview.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling calendar event for interview {interview.id}: {e}")
            db_session.rollback()
            return False
    
    def check_interviewer_availability(
        self,
        interviewer_email: str,
        proposed_time: datetime,
        duration_minutes: int = 60
    ) -> Dict:
        """
        Check if an interviewer is available at a proposed time
        
        Args:
            interviewer_email: Interviewer's email address
            proposed_time: Proposed interview start time
            duration_minutes: Interview duration in minutes
            
        Returns:
            Dict with availability information
        """
        try:
            if not self.calendar_service:
                return {'available': False, 'error': 'Calendar service not initialized'}
            
            # Check availability for the proposed time slot
            end_time = proposed_time + timedelta(minutes=duration_minutes)
            
            availability = self.calendar_service.get_availability(
                email=interviewer_email,
                start_date=proposed_time - timedelta(minutes=30),  # Buffer before
                end_date=end_time + timedelta(minutes=30),         # Buffer after
                timezone=get_calendar_timezone()
            )
            
            if 'error' in availability:
                return {'available': False, 'error': availability['error']}
            
            # Check if the proposed time slot is free
            is_available = True
            conflict_details = []
            
            for busy_period in availability['busy']:
                busy_start = datetime.fromisoformat(busy_period['start'])
                busy_end = datetime.fromisoformat(busy_period['end'])
                
                # Check for overlap
                if not (end_time <= busy_start or proposed_time >= busy_end):
                    is_available = False
                    conflict_details.append({
                        'start': busy_period['start'],
                        'end': busy_period['end']
                    })
            
            return {
                'available': is_available,
                'email': interviewer_email,
                'proposed_time': proposed_time.isoformat(),
                'duration_minutes': duration_minutes,
                'conflicts': conflict_details,
                'timezone': get_calendar_timezone()
            }
            
        except Exception as e:
            logger.error(f"Error checking availability for {interviewer_email}: {e}")
            return {'available': False, 'error': str(e)}
    
    def find_available_slots(
        self,
        interviewer_email: str,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60
    ) -> List[Dict]:
        """
        Find available time slots for an interviewer
        
        Args:
            interviewer_email: Interviewer's email address
            start_date: Start of search period
            end_date: End of search period
            duration_minutes: Required slot duration
            
        Returns:
            List of available time slots
        """
        try:
            if not self.calendar_service:
                logger.error("Calendar service not initialized")
                return []
            
            availability = self.calendar_service.get_availability(
                email=interviewer_email,
                start_date=start_date,
                end_date=end_date,
                timezone=get_calendar_timezone()
            )
            
            if 'error' in availability:
                logger.error(f"Error getting availability: {availability['error']}")
                return []
            
            # Filter slots by minimum duration
            suitable_slots = []
            for slot in availability['free']:
                slot_start = datetime.fromisoformat(slot['start'])
                slot_end = datetime.fromisoformat(slot['end'])
                slot_duration = (slot_end - slot_start).total_seconds() / 60
                
                if slot_duration >= duration_minutes:
                    suitable_slots.append({
                        'start': slot['start'],
                        'end': slot['end'],
                        'duration_minutes': int(slot_duration),
                        'suitable_for': duration_minutes
                    })
            
            logger.info(f"Found {len(suitable_slots)} available slots for {interviewer_email}")
            return suitable_slots
            
        except Exception as e:
            logger.error(f"Error finding available slots: {e}")
            return []
    
    def suggest_interview_times(
        self,
        interviewer_emails: List[str],
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        max_suggestions: int = 5
    ) -> List[Dict]:
        """
        Suggest optimal interview times based on multiple interviewers' availability
        
        Args:
            interviewer_emails: List of interviewer email addresses
            start_date: Start of search period
            end_date: End of search period
            duration_minutes: Required interview duration
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of suggested time slots
        """
        try:
            if not self.calendar_service:
                logger.error("Calendar service not initialized")
                return []
            
            if len(interviewer_emails) == 1:
                # Single interviewer - return their available slots
                return self.find_available_slots(
                    interviewer_emails[0], start_date, end_date, duration_minutes
                )[:max_suggestions]
            
            # Multiple interviewers - find mutual availability
            mutual_slots = self.calendar_service.find_mutual_availability(
                email_list=interviewer_emails,
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration_minutes,
                timezone=get_calendar_timezone()
            )
            
            # Sort by earliest time and limit results
            mutual_slots.sort(key=lambda x: x['start'])
            
            logger.info(f"Found {len(mutual_slots)} mutual availability slots")
            return mutual_slots[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error suggesting interview times: {e}")
            return []

# Global calendar integration instance
_calendar_integration = None

def get_calendar_integration() -> InterviewCalendarIntegration:
    """
    Get the global calendar integration instance
    
    Returns:
        InterviewCalendarIntegration: Global instance
    """
    global _calendar_integration
    if _calendar_integration is None:
        _calendar_integration = InterviewCalendarIntegration()
    return _calendar_integration

def schedule_interview_with_calendar(
    interview: Interview,
    candidate: Candidate,
    interviewer: User,
    db_session
) -> Optional[str]:
    """
    Convenience function to schedule an interview with calendar integration
    
    Args:
        interview: Interview model instance
        candidate: Candidate model instance
        interviewer: User model instance
        db_session: Database session
        
    Returns:
        str: Calendar event ID if successful
    """
    calendar_integration = get_calendar_integration()
    return calendar_integration.create_interview_event(
        interview, candidate, interviewer, db_session
    )

def check_availability_before_scheduling(
    interviewer_email: str,
    proposed_time: datetime,
    duration_minutes: int = 60
) -> Dict:
    """
    Check availability before scheduling an interview
    
    Args:
        interviewer_email: Interviewer's email address
        proposed_time: Proposed interview time
        duration_minutes: Interview duration
        
    Returns:
        Dict with availability information
    """
    calendar_integration = get_calendar_integration()
    return calendar_integration.check_interviewer_availability(
        interviewer_email, proposed_time, duration_minutes
    )
