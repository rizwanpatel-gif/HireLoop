"""
Google Calendar Service for Interview Scheduling System
Handles OAuth2 authentication, event creation, and availability checking with enhanced token management
"""
import os
import json
import pytz
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
from pathlib import Path

# Google Calendar API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenManager:
    """
    Enhanced token management for OAuth2 credentials with user-specific storage
    """
    
    def __init__(self, base_token_dir: str = "tokens"):
        """
        Initialize token manager
        
        Args:
            base_token_dir: Base directory to store token files
        """
        self.base_token_dir = Path(base_token_dir)
        self.base_token_dir.mkdir(exist_ok=True)
    
    def _get_user_token_path(self, user_email: str) -> Path:
        """
        Get user-specific token file path
        
        Args:
            user_email: User's email address
            
        Returns:
            Path to user's token file
        """
        # Create a safe filename from email
        safe_email = hashlib.sha256(user_email.encode()).hexdigest()[:16]
        return self.base_token_dir / f"token_{safe_email}.json"
    
    def save_credentials(self, credentials: Credentials, user_email: str) -> bool:
        """
        Save user credentials to file
        
        Args:
            credentials: Google OAuth2 credentials
            user_email: User's email address
            
        Returns:
            bool: True if saved successfully
        """
        try:
            token_path = self._get_user_token_path(user_email)
            
            # Create credential data with metadata
            credential_data = {
                'credentials': json.loads(credentials.to_json()),
                'user_email': user_email,
                'created_at': datetime.now().isoformat(),
                'last_refreshed': datetime.now().isoformat()
            }
            
            with open(token_path, 'w') as token_file:
                json.dump(credential_data, token_file, indent=2)
            
            logger.info(f"Saved credentials for user: {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials for {user_email}: {e}")
            return False
    
    def load_credentials(self, user_email: str, scopes: List[str]) -> Optional[Credentials]:
        """
        Load user credentials from file
        
        Args:
            user_email: User's email address
            scopes: Required OAuth2 scopes
            
        Returns:
            Credentials object or None if not found/invalid
        """
        try:
            token_path = self._get_user_token_path(user_email)
            
            if not token_path.exists():
                logger.info(f"No token file found for user: {user_email}")
                return None
            
            with open(token_path, 'r') as token_file:
                token_data = json.load(token_file)
            
            # Validate token data
            if token_data.get('user_email') != user_email:
                logger.warning(f"Token file email mismatch for {user_email}")
                return None
            
            # Load credentials
            credentials = Credentials.from_authorized_user_info(
                token_data['credentials'], scopes
            )
            
            logger.info(f"Loaded credentials for user: {user_email}")
            return credentials
            
        except Exception as e:
            logger.error(f"Error loading credentials for {user_email}: {e}")
            return None
    
    def refresh_credentials(
        self, 
        credentials: Credentials, 
        user_email: str
    ) -> Tuple[bool, Optional[Credentials]]:
        """
        Refresh expired credentials
        
        Args:
            credentials: Existing credentials
            user_email: User's email address
            
        Returns:
            Tuple of (success, refreshed_credentials)
        """
        try:
            if not credentials.refresh_token:
                logger.error(f"No refresh token available for {user_email}")
                return False, None
            
            logger.info(f"Refreshing credentials for user: {user_email}")
            credentials.refresh(Request())
            
            # Save refreshed credentials
            if self.save_credentials(credentials, user_email):
                logger.info(f"✅ Credentials refreshed and saved for {user_email}")
                return True, credentials
            else:
                logger.error(f"Failed to save refreshed credentials for {user_email}")
                return False, None
                
        except RefreshError as e:
            logger.error(f"Failed to refresh credentials for {user_email}: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error refreshing credentials for {user_email}: {e}")
            return False, None
    
    def delete_credentials(self, user_email: str) -> bool:
        """
        Delete user credentials
        
        Args:
            user_email: User's email address
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            token_path = self._get_user_token_path(user_email)
            
            if token_path.exists():
                token_path.unlink()
                logger.info(f"Deleted credentials for user: {user_email}")
                return True
            else:
                logger.info(f"No credentials found to delete for user: {user_email}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting credentials for {user_email}: {e}")
            return False

class GoogleCalendarService:
    """
    Google Calendar integration service for interview scheduling with enhanced OAuth2 flow
    """
    
    # OAuth2 scopes required for calendar operations
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    # Default timezone for India
    DEFAULT_TIMEZONE = pytz.timezone('Asia/Kolkata')
    
    def __init__(self, credentials_file: str = None, token_dir: str = None):
        """
        Initialize Google Calendar Service with enhanced OAuth2 flow
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_dir: Directory to store user tokens
        """
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.token_manager = TokenManager(token_dir or os.getenv('GOOGLE_TOKEN_DIR', 'tokens'))
        self.service = None
        self.credentials = None
        self.current_user = None
        
    def authenticate(self, user_email: str, force_reauth: bool = False) -> bool:
        """
        Enhanced OAuth2 authentication with user-specific token management
        
        Args:
            user_email: Email for user-specific authentication
            force_reauth: Force re-authentication even if valid credentials exist
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            if not user_email:
                logger.error("User email is required for authentication")
                return False
                
            logger.info(f"Authenticating Google Calendar for user: {user_email}")
            
            # Check for existing valid credentials
            if not force_reauth:
                self.credentials = self.token_manager.load_credentials(user_email, self.SCOPES)
                
                if self.credentials and self.credentials.valid:
                    logger.info("Using existing valid credentials")
                    self.current_user = user_email
                    self.service = build('calendar', 'v3', credentials=self.credentials)
                    return self._test_connection()
                
                # Try to refresh expired credentials
                if (self.credentials and 
                    self.credentials.expired and 
                    self.credentials.refresh_token):
                    
                    logger.info("Attempting to refresh expired credentials")
                    success, refreshed_creds = self.token_manager.refresh_credentials(
                        self.credentials, user_email
                    )
                    
                    if success and refreshed_creds:
                        self.credentials = refreshed_creds
                        self.current_user = user_email
                        self.service = build('calendar', 'v3', credentials=self.credentials)
                        return self._test_connection()
                    else:
                        logger.warning("Failed to refresh credentials, starting new OAuth flow")
            
            # Start new OAuth2 flow
            return self._start_oauth_flow(user_email)
            
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return False
    
    def _start_oauth_flow(self, user_email: str) -> bool:
        """
        Start OAuth2 flow for new credentials
        
        Args:
            user_email: User's email address
            
        Returns:
            bool: True if authentication successful
        """
        try:
            if not os.path.exists(self.credentials_file):
                logger.error(f"Credentials file not found: {self.credentials_file}")
                raise FileNotFoundError(
                    f"Google credentials file not found: {self.credentials_file}\n"
                    "Please follow the setup guide to create credentials.json"
                )
            
            logger.info("Starting OAuth2 flow for new credentials")
            
            # Create flow from credentials file
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES
            )
            
            # Add user hint if available
            flow.oauth2session.params = {'login_hint': user_email}
            
            # Run OAuth flow
            # For development: use run_local_server()
            # For production: use run_console() or implement web flow
            try:
                self.credentials = flow.run_local_server(
                    port=0,
                    prompt='consent',  # Always show consent screen
                    authorization_prompt_message="Please visit this URL to authorize the application: {url}",
                    success_message="Authentication successful! You may close this window."
                )
            except Exception as server_error:
                logger.warning(f"Local server failed: {server_error}, falling back to console flow")
                self.credentials = flow.run_console()
            
            # Validate credentials
            if not self.credentials or not self.credentials.valid:
                logger.error("Failed to obtain valid credentials from OAuth flow")
                return False
            
            # Save credentials for future use
            if not self.token_manager.save_credentials(self.credentials, user_email):
                logger.warning("Failed to save credentials, but authentication succeeded")
            
            # Build service and test connection
            self.current_user = user_email
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
            if self._test_connection():
                logger.info("✅ Google Calendar authentication successful")
                return True
            else:
                logger.error("Authentication succeeded but service test failed")
                return False
                
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in OAuth flow: {e}")
            return False
    
    def _test_connection(self) -> bool:
        """
        Test the Google Calendar service connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            if not self.service:
                return False
                
            # Test by listing calendars
            calendar_list = self.service.calendarList().list(maxResults=1).execute()
            calendars = calendar_list.get('items', [])
            
            logger.info(f"Connected to Google Calendar with access to {len(calendar_list.get('items', []))} calendars")
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API test failed: {e}")
            if e.resp.status == 403:
                logger.error("Permission denied. Check OAuth scopes and API permissions.")
            return False
        except Exception as e:
            logger.error(f"Service test failed: {e}")
            return False
    
    def is_authenticated(self, user_email: str = None) -> bool:
        """
        Check if user is currently authenticated
        
        Args:
            user_email: Optional email to check specific user
            
        Returns:
            bool: True if authenticated
        """
        try:
            if not self.service or not self.credentials:
                return False
            
            if user_email and user_email != self.current_user:
                return False
            
            if self.credentials.expired:
                if self.credentials.refresh_token:
                    # Try to refresh
                    success, _ = self.token_manager.refresh_credentials(
                        self.credentials, self.current_user
                    )
                    return success
                else:
                    return False
            
            return self.credentials.valid
            
        except Exception as e:
            logger.error(f"Error checking authentication status: {e}")
            return False
    
    def revoke_credentials(self, user_email: str) -> bool:
        """
        Revoke and delete user credentials
        
        Args:
            user_email: User's email address
            
        Returns:
            bool: True if revoked successfully
        """
        try:
            logger.info(f"Revoking credentials for user: {user_email}")
            
            # Load credentials to revoke
            credentials = self.token_manager.load_credentials(user_email, self.SCOPES)
            
            if credentials and credentials.token:
                # Revoke the token
                revoke_url = 'https://oauth2.googleapis.com/revoke'
                import requests
                
                response = requests.post(revoke_url, 
                    params={'token': credentials.token},
                    headers={'content-type': 'application/x-www-form-urlencoded'}
                )
                
                if response.status_code == 200:
                    logger.info("Token revoked successfully on Google's servers")
                else:
                    logger.warning(f"Token revocation returned status: {response.status_code}")
            
            # Delete local token file
            self.token_manager.delete_credentials(user_email)
            
            # Clear current session if it's the same user
            if self.current_user == user_email:
                self.service = None
                self.credentials = None
                self.current_user = None
            
            logger.info(f"✅ Credentials revoked for user: {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking credentials for {user_email}: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """
        Get current authenticated user information
        
        Returns:
            Dict with user info or None if not authenticated
        """
        try:
            if not self.service or not self.current_user:
                return None
            
            # Get primary calendar to verify user identity
            calendar = self.service.calendars().get(calendarId='primary').execute()
            
            return {
                'email': self.current_user,
                'calendar_id': calendar.get('id'),
                'calendar_summary': calendar.get('summary'),
                'timezone': calendar.get('timeZone', 'UTC'),
                'authenticated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def create_interview_event(
        self,
        interview_data: Dict,
        candidate_email: str,
        interviewer_email: str,
        additional_attendees: List[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Create a comprehensive calendar event for an interview with Google Meet integration
        
        Args:
            interview_data: Dictionary containing interview details
            candidate_email: Candidate's email address
            interviewer_email: Interviewer's email address
            additional_attendees: List of additional attendee emails
            
        Returns:
            Dict with event_id, event_link, and meet_link if successful, None otherwise
        """
        try:
            if not self.service:
                logger.error("Google Calendar service not authenticated")
                return None
            
            # Extract interview details with defaults
            start_time = interview_data.get('scheduled_time')
            duration = interview_data.get('duration', 60)  # Default 60 minutes
            interview_type = interview_data.get('type', 'Interview')
            candidate_name = interview_data.get('candidate_name', 'Candidate')
            interviewer_name = interview_data.get('interviewer_name', 'Interviewer')
            position = interview_data.get('position', 'Position')
            notes = interview_data.get('notes', '')
            interview_id = interview_data.get('id', 'unknown')
            
            # Convert to datetime if string
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            # Ensure timezone awareness
            if start_time.tzinfo is None:
                start_time = self.DEFAULT_TIMEZONE.localize(start_time)
            else:
                start_time = start_time.astimezone(self.DEFAULT_TIMEZONE)
            
            # Calculate end time
            end_time = start_time + timedelta(minutes=duration)
            
            # Generate comprehensive meeting title
            meeting_title = f"{interview_type.title()} Interview - {candidate_name} ({position})"
            
            # Create detailed description
            description = f"""
🎯 INTERVIEW DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Candidate: {candidate_name}
📧 Email: {candidate_email}
💼 Position: {position}

👨‍💼 Interviewer: {interviewer_name}
📧 Email: {interviewer_email}

🕒 Duration: {duration} minutes
📅 Date & Time: {start_time.strftime('%A, %B %d, %Y at %I:%M %p %Z')}
🔗 Interview Type: {interview_type.title()}

{f'📝 Notes: {notes}' if notes else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 This event was automatically created by the Interview Scheduling System
🎥 Google Meet link will be available below
📧 All attendees will receive email invitations with calendar updates
⏰ Reminders are set for 24 hours and 30 minutes before the interview

Please join the meeting a few minutes early to test your audio and video.
Good luck! 🍀
            """.strip()
            
            # Prepare comprehensive attendees list with proper display names
            attendees = [
                {
                    'email': candidate_email, 
                    'displayName': f"{candidate_name} (Candidate)",
                    'responseStatus': 'needsAction',
                    'comment': f"Interview candidate for {position} position"
                },
                {
                    'email': interviewer_email, 
                    'displayName': f"{interviewer_name} (Interviewer)",
                    'responseStatus': 'accepted',
                    'organizer': True
                }
            ]
            
            # Add additional attendees if provided
            if additional_attendees:
                for email in additional_attendees:
                    attendees.append({
                        'email': email,
                        'responseStatus': 'needsAction',
                        'comment': 'Additional attendee for interview'
                    })
            
            # Generate unique request ID for Google Meet
            meet_request_id = f"interview_{interview_id}_{int(datetime.now().timestamp())}"
            
            # Create comprehensive event data
            event = {
                'summary': meeting_title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': attendees,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {
                            'method': 'email', 
                            'minutes': 24 * 60,  # 24 hours before
                            'description': f'Interview reminder: {meeting_title}'
                        },
                        {
                            'method': 'popup', 
                            'minutes': 30,  # 30 minutes before
                            'description': 'Interview starting in 30 minutes'
                        },
                        {
                            'method': 'email', 
                            'minutes': 10,  # 10 minutes before (additional reminder)
                            'description': 'Interview starting in 10 minutes - please join the Google Meet'
                        }
                    ],
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': meet_request_id,
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                        'status': {
                            'statusCode': 'pending'
                        }
                    }
                },
                'guestsCanModify': False,
                'guestsCanInviteOthers': False,
                'guestsCanSeeOtherGuests': True,
                'transparency': 'opaque',  # Show as busy
                'visibility': 'private',
                'status': 'confirmed',
                'colorId': '11',  # Red color for interviews
                'source': {
                    'title': 'Interview Scheduling System',
                    'url': 'https://your-company.com/interviews'
                },
                # Custom event properties
                'extendedProperties': {
                    'private': {
                        'interview_type': interview_type,
                        'candidate_email': candidate_email,
                        'interviewer_email': interviewer_email,
                        'position': position,
                        'system_generated': 'true',
                        'interview_id': str(interview_id)
                    }
                }
            }
            
            # Create the event with enhanced logging
            logger.info(f"Creating calendar event for interview:")
            logger.info(f"  Title: {meeting_title}")
            logger.info(f"  Candidate: {candidate_name} ({candidate_email})")
            logger.info(f"  Interviewer: {interviewer_name} ({interviewer_email})")
            logger.info(f"  Time: {start_time.strftime('%Y-%m-%d %H:%M %Z')}")
            logger.info(f"  Duration: {duration} minutes")
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,  # Enable Google Meet integration
                sendUpdates='all'  # Send email invitations to all attendees
            ).execute()
            
            # Extract event details
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            # Extract Google Meet link
            meet_link = None
            conference_data = created_event.get('conferenceData', {})
            entry_points = conference_data.get('entryPoints', [])
            
            for entry_point in entry_points:
                if entry_point.get('entryPointType') == 'video':
                    meet_link = entry_point.get('uri')
                    break
            
            # Log success with all details
            logger.info(f"✅ Interview event created successfully!")
            logger.info(f"   Event ID: {event_id}")
            logger.info(f"   Event Link: {event_link}")
            if meet_link:
                logger.info(f"   Google Meet Link: {meet_link}")
            else:
                logger.warning("   Google Meet link not generated - may take a few moments")
            
            # Return comprehensive result
            result = {
                'event_id': event_id,
                'event_link': event_link,
                'meet_link': meet_link,
                'title': meeting_title,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'attendees_count': len(attendees),
                'conference_id': conference_data.get('conferenceId'),
                'status': 'created'
            }
            
            return result
            
        except HttpError as e:
            logger.error(f"Google Calendar API error creating event: {e}")
            error_details = {
                'status_code': e.resp.status,
                'reason': e._get_reason(),
                'details': str(e)
            }
            
            if e.resp.status == 403:
                logger.error("Permission denied. Check OAuth scopes and calendar permissions.")
                error_details['solution'] = "Verify OAuth2 scopes include calendar write permissions"
            elif e.resp.status == 400:
                logger.error("Bad request. Check event data format.")
                error_details['solution'] = "Verify event data structure and required fields"
            elif e.resp.status == 409:
                logger.error("Conflict. Event may already exist.")
                error_details['solution'] = "Check for duplicate events or timing conflicts"
            
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {e}")
            logger.error(f"Interview data: {interview_data}")
            return None
    
    def create_calendar_event_with_details(
        self,
        title: str,
        candidate_name: str,
        candidate_email: str,
        position: str,
        interviewer_name: str,
        interviewer_email: str,
        start_datetime: datetime,
        duration_minutes: int = 60,
        interview_type: str = "Technical",
        notes: str = "",
        additional_attendees: List[str] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict[str, str]]:
        """
        Create a Google Calendar event with comprehensive details and automatic Google Meet link
        
        This is a standalone function that can be used independently of the interview scheduling system.
        
        Args:
            title: Custom event title (will be enhanced with candidate and position info)
            candidate_name: Full name of the candidate
            candidate_email: Candidate's email address
            position: Position being interviewed for
            interviewer_name: Full name of the interviewer
            interviewer_email: Interviewer's email address
            start_datetime: Interview start time (timezone-aware datetime)
            duration_minutes: Interview duration in minutes (default: 60)
            interview_type: Type of interview (Technical, HR, Cultural, etc.)
            notes: Additional notes or instructions
            additional_attendees: List of additional email addresses to invite
            calendar_id: Google Calendar ID to create event in (default: 'primary')
            
        Returns:
            Dict containing event_id, event_link, meet_link, and other details if successful, None otherwise
            
        Example:
            result = calendar_service.create_calendar_event_with_details(
                title="Senior Developer Interview",
                candidate_name="John Doe",
                candidate_email="john.doe@email.com",
                position="Senior Python Developer",
                interviewer_name="Jane Smith",
                interviewer_email="jane.smith@company.com",
                start_datetime=datetime(2025, 8, 15, 14, 0, tzinfo=pytz.timezone('Asia/Kolkata')),
                duration_minutes=90,
                interview_type="Technical",
                notes="Please prepare coding questions on Python and algorithms"
            )
        """
        try:
            if not self.service:
                logger.error("Google Calendar service not authenticated")
                return None
            
            # Validate required parameters
            required_params = {
                'title': title,
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'position': position,
                'interviewer_name': interviewer_name,
                'interviewer_email': interviewer_email,
                'start_datetime': start_datetime
            }
            
            for param_name, param_value in required_params.items():
                if not param_value:
                    raise ValueError(f"Required parameter '{param_name}' is missing or empty")
            
            # Ensure timezone awareness
            if start_datetime.tzinfo is None:
                start_datetime = self.DEFAULT_TIMEZONE.localize(start_datetime)
            else:
                start_datetime = start_datetime.astimezone(self.DEFAULT_TIMEZONE)
            
            # Calculate end time
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Generate enhanced meeting title
            if not title.startswith(interview_type):
                enhanced_title = f"{interview_type} Interview: {title} - {candidate_name} ({position})"
            else:
                enhanced_title = f"{title} - {candidate_name} ({position})"
            
            # Create comprehensive description
            formatted_date = start_datetime.strftime('%A, %B %d, %Y')
            formatted_time = start_datetime.strftime('%I:%M %p %Z')
            
            description = f"""
🎯 INTERVIEW INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Interview Title: {title}
👤 Candidate: {candidate_name}
📧 Candidate Email: {candidate_email}
💼 Position: {position}

👨‍💼 Interviewer: {interviewer_name}
📧 Interviewer Email: {interviewer_email}

📅 Date: {formatted_date}
🕒 Time: {formatted_time}
⏱️ Duration: {duration_minutes} minutes
🔗 Type: {interview_type}

{f'📝 Additional Notes:\\n{notes}\\n' if notes else ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎥 GOOGLE MEET INFORMATION:
• A Google Meet link will be automatically generated for this interview
• All attendees will receive the meeting link via email invitation
• Please join 5 minutes early to test audio/video setup

⏰ REMINDERS:
• 24 hours before: Email reminder sent to all attendees
• 30 minutes before: Pop-up reminder for interviewer
• 10 minutes before: Final email reminder with join link

📧 NEXT STEPS:
• Calendar invitations will be sent automatically
• Attendees can respond to confirm availability
• Google Meet link will be active 15 minutes before start time

🤖 Generated by Interview Scheduling System
            """.strip()
            
            # Prepare attendees list
            attendees = [
                {
                    'email': candidate_email,
                    'displayName': f"{candidate_name} (Candidate)",
                    'responseStatus': 'needsAction',
                    'comment': f"Interview candidate for {position}"
                },
                {
                    'email': interviewer_email,
                    'displayName': f"{interviewer_name} (Interviewer)",
                    'responseStatus': 'accepted',
                    'organizer': True,
                    'comment': f"Conducting {interview_type.lower()} interview"
                }
            ]
            
            # Add additional attendees
            if additional_attendees:
                for email in additional_attendees:
                    attendees.append({
                        'email': email,
                        'displayName': email.split('@')[0].title(),
                        'responseStatus': 'needsAction',
                        'comment': 'Additional interview attendee'
                    })
            
            # Generate unique conference request ID
            timestamp = int(datetime.now().timestamp())
            conference_request_id = f"interview_{candidate_name.replace(' ', '_').lower()}_{timestamp}"
            
            # Create event structure
            event_data = {
                'summary': enhanced_title,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': str(start_datetime.tzinfo) or 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': str(end_datetime.tzinfo) or 'Asia/Kolkata',
                },
                'attendees': attendees,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {
                            'method': 'email',
                            'minutes': 24 * 60,  # 24 hours
                            'description': f'Interview tomorrow: {enhanced_title}'
                        },
                        {
                            'method': 'popup',
                            'minutes': 30,  # 30 minutes
                            'description': 'Interview starting in 30 minutes'
                        },
                        {
                            'method': 'email',
                            'minutes': 10,  # 10 minutes
                            'description': 'Interview starting soon - click to join Google Meet'
                        }
                    ],
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': conference_request_id,
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                        'status': {'statusCode': 'pending'}
                    }
                },
                'guestsCanModify': False,
                'guestsCanInviteOthers': False,
                'guestsCanSeeOtherGuests': True,
                'transparency': 'opaque',  # Block time on calendar
                'visibility': 'private',
                'status': 'confirmed',
                'colorId': '9',  # Blue color for scheduled interviews
                'source': {
                    'title': 'Interview Scheduling System',
                    'url': 'https://your-company.com'
                },
                'extendedProperties': {
                    'private': {
                        'event_type': 'interview',
                        'interview_type': interview_type,
                        'candidate_name': candidate_name,
                        'candidate_email': candidate_email,
                        'position': position,
                        'interviewer_name': interviewer_name,
                        'interviewer_email': interviewer_email,
                        'duration_minutes': str(duration_minutes),
                        'created_by': 'interview_scheduling_system',
                        'created_at': datetime.now().isoformat()
                    }
                }
            }
            
            # Log event creation details
            logger.info(f"Creating Google Calendar event:")
            logger.info(f"  📋 Title: {enhanced_title}")
            logger.info(f"  👤 Candidate: {candidate_name} <{candidate_email}>")
            logger.info(f"  👨‍💼 Interviewer: {interviewer_name} <{interviewer_email}>")
            logger.info(f"  📅 Date/Time: {start_datetime.strftime('%Y-%m-%d %H:%M %Z')}")
            logger.info(f"  ⏱️ Duration: {duration_minutes} minutes")
            logger.info(f"  🎯 Type: {interview_type}")
            logger.info(f"  👥 Total Attendees: {len(attendees)}")
            
            if additional_attendees:
                logger.info(f"  ➕ Additional Attendees: {', '.join(additional_attendees)}")
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                conferenceDataVersion=1,  # Enable Google Meet
                sendUpdates='all'  # Send invitations to all attendees
            ).execute()
            
            # Extract event information
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            # Extract Google Meet information
            meet_link = None
            meet_phone = None
            meet_access_code = None
            conference_data = created_event.get('conferenceData', {})
            
            for entry_point in conference_data.get('entryPoints', []):
                if entry_point.get('entryPointType') == 'video':
                    meet_link = entry_point.get('uri')
                elif entry_point.get('entryPointType') == 'phone':
                    meet_phone = entry_point.get('uri')
                    meet_access_code = entry_point.get('accessCode')
            
            # Prepare comprehensive result
            result = {
                'event_id': event_id,
                'event_link': event_link,
                'meet_link': meet_link,
                'meet_phone': meet_phone,
                'meet_access_code': meet_access_code,
                'title': enhanced_title,
                'start_time': start_datetime.isoformat(),
                'end_time': end_datetime.isoformat(),
                'timezone': str(start_datetime.tzinfo),
                'duration_minutes': duration_minutes,
                'attendees_count': len(attendees),
                'conference_id': conference_data.get('conferenceId'),
                'conference_request_id': conference_request_id,
                'calendar_id': calendar_id,
                'status': 'created',
                'reminders_set': True,
                'google_meet_enabled': bool(meet_link),
                'invitations_sent': True
            }
            
            # Log successful creation
            logger.info(f"✅ Calendar event created successfully!")
            logger.info(f"   🆔 Event ID: {event_id}")
            logger.info(f"   🔗 Calendar Link: {event_link}")
            
            if meet_link:
                logger.info(f"   🎥 Google Meet Link: {meet_link}")
                if meet_phone:
                    logger.info(f"   📞 Meet Phone: {meet_phone}")
                if meet_access_code:
                    logger.info(f"   🔑 Access Code: {meet_access_code}")
            else:
                logger.warning("   ⚠️ Google Meet link not immediately available (may take a few moments)")
            
            logger.info(f"   📧 Email invitations sent to {len(attendees)} attendees")
            logger.info(f"   ⏰ Reminders set for 24h, 30min, and 10min before interview")
            
            return result
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return None
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            
            if e.resp.status == 403:
                logger.error("❌ Permission denied - check OAuth scopes")
            elif e.resp.status == 400:
                logger.error("❌ Bad request - check event data format")
            elif e.resp.status == 409:
                logger.error("❌ Conflict - event may already exist")
            elif e.resp.status == 404:
                logger.error("❌ Calendar not found - check calendar_id")
            
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {e}")
            logger.exception("Full error details:")
            return None
    
    def get_availability(
        self,
        email: str,
        start_date: datetime,
        end_date: datetime,
        timezone: str = 'Asia/Kolkata'
    ) -> Dict[str, List[Dict]]:
        """
        Check availability for a specific user within a date range
        
        Args:
            email: User's email address
            start_date: Start of the time range to check
            end_date: End of the time range to check
            timezone: Timezone for the query
            
        Returns:
            Dict containing free and busy time slots
        """
        try:
            if not self.service:
                logger.error("Google Calendar service not authenticated")
                return {'free': [], 'busy': [], 'error': 'Service not authenticated'}
            
            logger.info(f"Checking availability for {email} from {start_date} to {end_date}")
            
            # Ensure timezone awareness
            tz = pytz.timezone(timezone)
            if start_date.tzinfo is None:
                start_date = tz.localize(start_date)
            if end_date.tzinfo is None:
                end_date = tz.localize(end_date)
            
            # Convert to UTC for API call
            start_utc = start_date.astimezone(pytz.UTC)
            end_utc = end_date.astimezone(pytz.UTC)
            
            # Prepare the request
            request_body = {
                'timeMin': start_utc.isoformat(),
                'timeMax': end_utc.isoformat(),
                'timeZone': timezone,
                'items': [{'id': email}]
            }
            
            # Make the API call
            freebusy_result = self.service.freebusy().query(body=request_body).execute()
            
            # Extract busy times
            calendar_data = freebusy_result.get('calendars', {}).get(email, {})
            busy_times = calendar_data.get('busy', [])
            errors = calendar_data.get('errors', [])
            
            if errors:
                logger.warning(f"Errors in availability check for {email}: {errors}")
            
            # Convert busy times to local timezone
            busy_periods = []
            for busy_period in busy_times:
                start_busy = datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00'))
                end_busy = datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00'))
                
                busy_periods.append({
                    'start': start_busy.astimezone(tz).isoformat(),
                    'end': end_busy.astimezone(tz).isoformat(),
                    'start_datetime': start_busy.astimezone(tz),
                    'end_datetime': end_busy.astimezone(tz)
                })
            
            # Calculate free time slots (example: working hours 9 AM to 6 PM)
            free_periods = self._calculate_free_slots(
                start_date, end_date, busy_periods, tz
            )
            
            result = {
                'email': email,
                'timezone': timezone,
                'query_start': start_date.isoformat(),
                'query_end': end_date.isoformat(),
                'busy': busy_periods,
                'free': free_periods,
                'errors': errors
            }
            
            logger.info(f"✅ Availability check completed for {email}")
            logger.info(f"   Found {len(busy_periods)} busy periods")
            logger.info(f"   Found {len(free_periods)} free slots")
            
            return result
            
        except HttpError as e:
            logger.error(f"Google Calendar API error checking availability: {e}")
            return {'error': f'API error: {e}', 'free': [], 'busy': []}
        except Exception as e:
            logger.error(f"Unexpected error checking availability: {e}")
            return {'error': f'Unexpected error: {e}', 'free': [], 'busy': []}
    
    def _calculate_free_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        busy_periods: List[Dict],
        timezone: pytz.timezone,
        working_hours: Tuple[int, int] = (9, 18),  # 9 AM to 6 PM
        slot_duration: int = 60  # 60 minutes
    ) -> List[Dict]:
        """
        Calculate free time slots based on busy periods and working hours
        
        Args:
            start_date: Start of the period
            end_date: End of the period
            busy_periods: List of busy time periods
            timezone: Timezone for calculations
            working_hours: Tuple of (start_hour, end_hour) for working hours
            slot_duration: Duration of each slot in minutes
            
        Returns:
            List of free time slots
        """
        free_slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Define working hours for the day
            day_start = timezone.localize(
                datetime.combine(current_date, datetime.min.time().replace(hour=working_hours[0]))
            )
            day_end = timezone.localize(
                datetime.combine(current_date, datetime.min.time().replace(hour=working_hours[1]))
            )
            
            # Ensure we don't go beyond the query range
            if day_start < start_date:
                day_start = start_date
            if day_end > end_date:
                day_end = end_date
            
            # Find busy periods for this day
            day_busy_periods = []
            for busy in busy_periods:
                busy_start = busy['start_datetime']
                busy_end = busy['end_datetime']
                
                # Check if busy period overlaps with this day
                if (busy_start.date() <= current_date <= busy_end.date()):
                    # Clip to working hours
                    clipped_start = max(busy_start, day_start)
                    clipped_end = min(busy_end, day_end)
                    
                    if clipped_start < clipped_end:
                        day_busy_periods.append({
                            'start': clipped_start,
                            'end': clipped_end
                        })
            
            # Sort busy periods by start time
            day_busy_periods.sort(key=lambda x: x['start'])
            
            # Find free slots between busy periods
            current_time = day_start
            
            for busy_period in day_busy_periods:
                # Check if there's a free slot before this busy period
                if current_time + timedelta(minutes=slot_duration) <= busy_period['start']:
                    # Add free slots until the busy period starts
                    while current_time + timedelta(minutes=slot_duration) <= busy_period['start']:
                        slot_end = current_time + timedelta(minutes=slot_duration)
                        free_slots.append({
                            'start': current_time.isoformat(),
                            'end': slot_end.isoformat(),
                            'start_datetime': current_time,
                            'end_datetime': slot_end,
                            'duration_minutes': slot_duration
                        })
                        current_time += timedelta(minutes=slot_duration)
                
                # Move current time to end of busy period
                current_time = max(current_time, busy_period['end'])
            
            # Add remaining free slots until end of working day
            while current_time + timedelta(minutes=slot_duration) <= day_end:
                slot_end = current_time + timedelta(minutes=slot_duration)
                free_slots.append({
                    'start': current_time.isoformat(),
                    'end': slot_end.isoformat(),
                    'start_datetime': current_time,
                    'end_datetime': slot_end,
                    'duration_minutes': slot_duration
                })
                current_time += timedelta(minutes=slot_duration)
            
            current_date += timedelta(days=1)
        
        return free_slots
    
    def update_interview_event(
        self,
        event_id: str,
        interview_data: Dict,
        send_updates: str = 'all'
    ) -> bool:
        """
        Update an existing calendar event
        
        Args:
            event_id: Google Calendar event ID
            interview_data: Updated interview data
            send_updates: Whether to send update notifications ('all', 'externalOnly', 'none')
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if not self.service:
                logger.error("Google Calendar service not authenticated")
                return False
            
            logger.info(f"Updating calendar event: {event_id}")
            
            # Get existing event
            existing_event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields based on interview_data
            if 'scheduled_time' in interview_data:
                start_time = interview_data['scheduled_time']
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                
                if start_time.tzinfo is None:
                    start_time = self.DEFAULT_TIMEZONE.localize(start_time)
                
                duration = interview_data.get('duration', 60)
                end_time = start_time + timedelta(minutes=duration)
                
                existing_event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                }
                existing_event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                }
            
            if 'notes' in interview_data:
                # Update description while preserving the structure
                current_desc = existing_event.get('description', '')
                # You can implement more sophisticated description updating here
                existing_event['description'] = current_desc
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=existing_event,
                sendUpdates=send_updates
            ).execute()
            
            logger.info(f"✅ Calendar event updated successfully: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error updating event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating calendar event: {e}")
            return False
    
    def delete_interview_event(self, event_id: str, send_updates: str = 'all') -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: Google Calendar event ID
            send_updates: Whether to send cancellation notifications
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if not self.service:
                logger.error("Google Calendar service not authenticated")
                return False
            
            logger.info(f"Deleting calendar event: {event_id}")
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates=send_updates
            ).execute()
            
            logger.info(f"✅ Calendar event deleted successfully: {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Calendar event not found: {event_id}")
                return True  # Consider not found as successful deletion
            logger.error(f"Google Calendar API error deleting event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting calendar event: {e}")
            return False
    
    def find_mutual_availability(
        self,
        email_list: List[str],
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        timezone: str = 'Asia/Kolkata'
    ) -> List[Dict]:
        """
        Find mutual availability slots for multiple users
        
        Args:
            email_list: List of email addresses to check
            start_date: Start of the time range
            end_date: End of the time range
            duration_minutes: Required duration in minutes
            timezone: Timezone for the query
            
        Returns:
            List of mutual free time slots
        """
        try:
            logger.info(f"Finding mutual availability for {len(email_list)} users")
            
            all_availabilities = []
            
            # Get availability for each user
            for email in email_list:
                availability = self.get_availability(email, start_date, end_date, timezone)
                if 'error' in availability:
                    logger.warning(f"Error getting availability for {email}: {availability['error']}")
                    continue
                all_availabilities.append(availability)
            
            if not all_availabilities:
                logger.error("No valid availabilities found")
                return []
            
            # Find intersecting free slots
            mutual_slots = []
            
            # Get all possible free slots from the first user
            base_free_slots = all_availabilities[0]['free']
            
            for base_slot in base_free_slots:
                base_start = datetime.fromisoformat(base_slot['start'])
                base_end = datetime.fromisoformat(base_slot['end'])
                
                # Check if this slot is free for all other users
                is_mutual = True
                
                for other_availability in all_availabilities[1:]:
                    slot_is_free = False
                    
                    for other_slot in other_availability['free']:
                        other_start = datetime.fromisoformat(other_slot['start'])
                        other_end = datetime.fromisoformat(other_slot['end'])
                        
                        # Check if there's overlap with required duration
                        overlap_start = max(base_start, other_start)
                        overlap_end = min(base_end, other_end)
                        
                        if overlap_end - overlap_start >= timedelta(minutes=duration_minutes):
                            slot_is_free = True
                            break
                    
                    if not slot_is_free:
                        is_mutual = False
                        break
                
                if is_mutual and (base_end - base_start) >= timedelta(minutes=duration_minutes):
                    mutual_slots.append({
                        'start': base_slot['start'],
                        'end': base_slot['end'],
                        'duration_minutes': duration_minutes,
                        'participants': email_list
                    })
            
            logger.info(f"✅ Found {len(mutual_slots)} mutual availability slots")
            return mutual_slots
            
        except Exception as e:
            logger.error(f"Error finding mutual availability: {e}")
            return []

# Utility functions for easier integration
def create_calendar_service(credentials_file: str = None) -> GoogleCalendarService:
    """
    Create and authenticate a Google Calendar service instance
    
    Args:
        credentials_file: Path to credentials file
        
    Returns:
        GoogleCalendarService: Authenticated service instance
    """
    service = GoogleCalendarService(credentials_file)
    if service.authenticate():
        return service
    else:
        raise Exception("Failed to authenticate Google Calendar service")

def schedule_interview_with_calendar(
    calendar_service: GoogleCalendarService,
    interview_data: Dict,
    candidate_email: str,
    interviewer_email: str
) -> Optional[str]:
    """
    Convenience function to schedule an interview with calendar integration
    
    Args:
        calendar_service: Authenticated calendar service
        interview_data: Interview details
        candidate_email: Candidate's email
        interviewer_email: Interviewer's email
        
    Returns:
        str: Calendar event ID if successful
    """
    return calendar_service.create_interview_event(
        interview_data, candidate_email, interviewer_email
    )
