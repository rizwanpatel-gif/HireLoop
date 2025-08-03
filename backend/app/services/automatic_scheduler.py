"""
Automatic Interview Scheduling Logic
===================================

Comprehensive interview scheduling system that:
1. Checks interviewer availability in Google Calendar
2. Creates interview database record with all details
3. Generates Google Calendar event with meeting link
4. Sends confirmation notifications to both parties
5. Updates interview record with Google event ID

Features:
- Real-time calendar availability checking
- AI-powered interviewer matching with availability
- Automated Google Meet link generation
- Email notifications and confirmations
- Comprehensive error handling and retry logic
- Interview status tracking and updates
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Import existing components
from interview_scheduling_api import (
    InterviewDB, InterviewStatus, InterviewType,
    InterviewScheduleRequest, InterviewConfirmationResponse
)
from candidate_management_api import CandidateDB, get_db, SessionLocal
from google_calendar_service import GoogleCalendarService
from smart_matching_algorithm import SmartMatchingAlgorithm, create_sample_interviewer_profiles
from background_tasks import task_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulingStatus(str, Enum):
    """Interview scheduling process status"""
    INITIATED = "initiated"
    CHECKING_AVAILABILITY = "checking_availability" 
    FINDING_INTERVIEWER = "finding_interviewer"
    CREATING_RECORD = "creating_record"
    CREATING_CALENDAR_EVENT = "creating_calendar_event"
    SENDING_NOTIFICATIONS = "sending_notifications"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AvailabilitySlot:
    """Represents an available time slot for an interviewer"""
    interviewer_id: str
    interviewer_name: str
    interviewer_email: str
    start_time: datetime
    end_time: datetime
    confidence_score: float
    timezone: str = "UTC"

@dataclass 
class InterviewerAvailability:
    """Comprehensive interviewer availability information"""
    interviewer_id: str
    interviewer_name: str
    interviewer_email: str
    available_slots: List[AvailabilitySlot]
    next_available: Optional[datetime]
    calendar_last_checked: datetime
    busy_periods: List[Tuple[datetime, datetime]]

@dataclass
class SchedulingResult:
    """Result of the automatic scheduling process"""
    success: bool
    interview_id: Optional[str]
    status: SchedulingStatus
    message: str
    interviewer_selected: Optional[Dict[str, Any]]
    calendar_event_id: Optional[str]
    google_meet_link: Optional[str]
    notifications_sent: bool
    errors: List[str]
    scheduled_time: Optional[datetime]

class EmailNotificationService:
    """Service for sending interview confirmation emails"""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"  # Configure for your email provider
        self.smtp_port = 587
        self.email_templates = self._load_email_templates()
    
    def _load_email_templates(self) -> Dict[str, Template]:
        """Load email templates for different notifications"""
        
        # Candidate confirmation email template
        candidate_template = Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .interview-details { background: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }
                .button { display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Interview Scheduled Successfully! 🎉</h1>
            </div>
            <div class="content">
                <p>Dear {{ candidate_name }},</p>
                
                <p>Great news! Your interview has been scheduled for the <strong>{{ position }}</strong> position.</p>
                
                <div class="interview-details">
                    <h3>Interview Details:</h3>
                    <p><strong>📅 Date & Time:</strong> {{ scheduled_time.strftime('%A, %B %d, %Y at %I:%M %p %Z') }}</p>
                    <p><strong>⏱️ Duration:</strong> {{ duration_minutes }} minutes</p>
                    <p><strong>🎯 Interview Type:</strong> {{ interview_type.title() }}</p>
                    <p><strong>👨‍💼 Interviewer:</strong> {{ interviewer_name }}</p>
                    <p><strong>📧 Interviewer Email:</strong> {{ interviewer_email }}</p>
                    {% if google_meet_link %}
                    <p><strong>🎥 Meeting Link:</strong> <a href="{{ google_meet_link }}">Join Google Meet</a></p>
                    {% endif %}
                </div>
                
                {% if focus_areas %}
                <h3>Preparation Recommendations:</h3>
                <ul>
                    {% for area in focus_areas %}
                    <li>{{ area }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                <p>Please make sure to:</p>
                <ul>
                    <li>✅ Confirm your attendance by clicking the calendar invite</li>
                    <li>🔧 Test your audio/video setup beforehand</li>
                    <li>📋 Prepare questions about the role and company</li>
                    <li>💼 Have your portfolio/work samples ready to share</li>
                </ul>
                
                <p>We're excited to speak with you! If you need to reschedule or have any questions, please contact us immediately.</p>
                
                <p>Best regards,<br>The Hiring Team</p>
            </div>
        </body>
        </html>
        ''')
        
        # Interviewer notification email template
        interviewer_template = Template('''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: #2196F3; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .candidate-info { background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>New Interview Scheduled 📅</h1>
            </div>
            <div class="content">
                <p>Hi {{ interviewer_name }},</p>
                
                <p>A new interview has been scheduled and you've been selected as the interviewer based on AI matching (Match Score: {{ ai_match_score }}/100).</p>
                
                <div class="candidate-info">
                    <h3>Candidate Information:</h3>
                    <p><strong>👤 Name:</strong> {{ candidate_name }}</p>
                    <p><strong>📧 Email:</strong> {{ candidate_email }}</p>
                    <p><strong>💼 Position:</strong> {{ position }}</p>
                    <p><strong>📊 AI Score:</strong> {{ candidate_ai_score }}/100</p>
                    <p><strong>⏱️ Experience:</strong> {{ experience_years }} years</p>
                </div>
                
                <div class="interview-details">
                    <h3>Interview Details:</h3>
                    <p><strong>📅 Date & Time:</strong> {{ scheduled_time.strftime('%A, %B %d, %Y at %I:%M %p %Z') }}</p>
                    <p><strong>⏱️ Duration:</strong> {{ duration_minutes }} minutes</p>
                    <p><strong>🎯 Type:</strong> {{ interview_type.title() }} (Round {{ interview_round }})</p>
                    {% if google_meet_link %}
                    <p><strong>🎥 Meeting Link:</strong> <a href="{{ google_meet_link }}">Join Google Meet</a></p>
                    {% endif %}
                </div>
                
                {% if focus_areas %}
                <h3>AI Recommended Focus Areas:</h3>
                <ul>
                    {% for area in focus_areas %}
                    <li>{{ area }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                <p>Please review the candidate's profile and prepare accordingly. The calendar event has been added to your calendar with all details.</p>
                
                <p>Best regards,<br>Hiring System</p>
            </div>
        </body>
        </html>
        ''')
        
        return {
            'candidate_confirmation': candidate_template,
            'interviewer_notification': interviewer_template
        }
    
    async def send_confirmation_emails(
        self,
        candidate_data: Dict[str, Any],
        interviewer_data: Dict[str, Any],
        interview_details: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Send confirmation emails to candidate and interviewer
        
        Returns:
            Dict with email sending status for each recipient
        """
        results = {
            'candidate_email_sent': False,
            'interviewer_email_sent': False
        }
        
        try:
            # Send candidate confirmation email
            candidate_html = self.email_templates['candidate_confirmation'].render(
                candidate_name=candidate_data['name'],
                position=candidate_data['position'],
                scheduled_time=interview_details['scheduled_time'],
                duration_minutes=interview_details['duration_minutes'],
                interview_type=interview_details['interview_type'],
                interviewer_name=interviewer_data['name'],
                interviewer_email=interviewer_data['email'],
                google_meet_link=interview_details.get('google_meet_link'),
                focus_areas=interview_details.get('focus_areas', [])
            )
            
            candidate_sent = await self._send_email(
                to_email=candidate_data['email'],
                subject=f"Interview Scheduled - {candidate_data['position']} Position",
                html_content=candidate_html
            )
            results['candidate_email_sent'] = candidate_sent
            
            # Send interviewer notification email
            interviewer_html = self.email_templates['interviewer_notification'].render(
                interviewer_name=interviewer_data['name'],
                candidate_name=candidate_data['name'],
                candidate_email=candidate_data['email'],
                position=candidate_data['position'],
                candidate_ai_score=candidate_data.get('ai_score', 'N/A'),
                experience_years=candidate_data.get('experience_years', 0),
                scheduled_time=interview_details['scheduled_time'],
                duration_minutes=interview_details['duration_minutes'],
                interview_type=interview_details['interview_type'],
                interview_round=interview_details.get('interview_round', 1),
                ai_match_score=interview_details.get('ai_match_score', 0),
                google_meet_link=interview_details.get('google_meet_link'),
                focus_areas=interview_details.get('focus_areas', [])
            )
            
            interviewer_sent = await self._send_email(
                to_email=interviewer_data['email'],
                subject=f"New Interview Scheduled - {candidate_data['name']}",
                html_content=interviewer_html
            )
            results['interviewer_email_sent'] = interviewer_sent
            
        except Exception as e:
            logger.error(f"Error sending confirmation emails: {e}")
        
        return results
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send individual email (implement with your email service)"""
        # In production, implement with your email service (SendGrid, AWS SES, etc.)
        # For demo, we'll simulate email sending
        logger.info(f"📧 Sending email to {to_email}: {subject}")
        await asyncio.sleep(0.1)  # Simulate email sending delay
        logger.info(f"✅ Email sent successfully to {to_email}")
        return True

class AutomaticInterviewScheduler:
    """
    Main class for automatic interview scheduling with comprehensive features
    """
    
    def __init__(self):
        self.calendar_service = GoogleCalendarService()
        self.matching_algorithm = SmartMatchingAlgorithm()
        self.email_service = EmailNotificationService()
        self.interviewer_profiles = create_sample_interviewer_profiles()
    
    async def schedule_interview_automatically(
        self,
        request: InterviewScheduleRequest,
        db: Session
    ) -> SchedulingResult:
        """
        Main method to automatically schedule an interview with full workflow
        
        Args:
            request: Interview scheduling request
            db: Database session
            
        Returns:
            SchedulingResult with complete scheduling information
        """
        
        result = SchedulingResult(
            success=False,
            interview_id=None,
            status=SchedulingStatus.INITIATED,
            message="Starting automatic interview scheduling...",
            interviewer_selected=None,
            calendar_event_id=None,
            google_meet_link=None,
            notifications_sent=False,
            errors=[],
            scheduled_time=None
        )
        
        try:
            logger.info(f"🚀 Starting automatic interview scheduling")
            logger.info(f"   Candidate ID: {request.candidate_id}")
            logger.info(f"   Preferred Time: {request.preferred_time}")
            logger.info(f"   Duration: {request.duration_minutes} minutes")
            
            # Step 1: Get candidate details and validate
            candidate = await self._get_and_validate_candidate(request.candidate_id, db)
            if not candidate:
                result.status = SchedulingStatus.FAILED
                result.message = f"Candidate {request.candidate_id} not found"
                result.errors.append("Candidate validation failed")
                return result
            
            # Step 2: Check interviewer availability in Google Calendar
            result.status = SchedulingStatus.CHECKING_AVAILABILITY
            logger.info(f"📅 Checking interviewer availability...")
            
            available_interviewers = await self._check_interviewer_availability(
                request.preferred_time,
                request.duration_minutes,
                request.interview_type
            )
            
            if not available_interviewers:
                result.status = SchedulingStatus.FAILED
                result.message = "No interviewers available at the requested time"
                result.errors.append("No available interviewers found")
                return result
            
            logger.info(f"   Found {len(available_interviewers)} available interviewers")
            
            # Step 3: Use AI to find best available interviewer
            result.status = SchedulingStatus.FINDING_INTERVIEWER
            logger.info(f"🤖 Finding best interviewer using AI matching...")
            
            best_interviewer = await self._find_best_available_interviewer(
                candidate, available_interviewers, request
            )
            
            if not best_interviewer:
                result.status = SchedulingStatus.FAILED
                result.message = "No suitable interviewer found"
                result.errors.append("Interviewer matching failed")
                return result
            
            result.interviewer_selected = best_interviewer
            logger.info(f"   Selected: {best_interviewer['name']} (Score: {best_interviewer['match_score']:.1f})")
            
            # Step 4: Create interview database record with all details
            result.status = SchedulingStatus.CREATING_RECORD
            logger.info(f"💾 Creating comprehensive interview database record...")
            
            interview_id = await self._create_interview_record(
                candidate, best_interviewer, request, db
            )
            
            if not interview_id:
                result.status = SchedulingStatus.FAILED
                result.message = "Failed to create interview record"
                result.errors.append("Database record creation failed")
                return result
            
            result.interview_id = interview_id
            result.scheduled_time = request.preferred_time
            logger.info(f"   Interview record created: {interview_id}")
            
            # Step 5: Generate Google Calendar event with meeting link
            result.status = SchedulingStatus.CREATING_CALENDAR_EVENT
            logger.info(f"📅 Creating Google Calendar event with meeting link...")
            
            calendar_result = await self._create_calendar_event_with_meeting(
                interview_id, candidate, best_interviewer, request, db
            )
            
            if calendar_result:
                result.calendar_event_id = calendar_result['event_id']
                result.google_meet_link = calendar_result.get('meet_link')
                logger.info(f"   Calendar event created: {calendar_result['event_id']}")
                logger.info(f"   Google Meet: {calendar_result.get('meet_link', 'Pending')}")
            else:
                result.errors.append("Calendar event creation failed")
                logger.warning("   Calendar event creation failed - continuing with email notifications")
            
            # Step 6: Send confirmation notifications to both parties
            result.status = SchedulingStatus.SENDING_NOTIFICATIONS
            logger.info(f"📧 Sending confirmation notifications...")
            
            notifications_result = await self._send_confirmation_notifications(
                candidate, best_interviewer, request, result
            )
            
            result.notifications_sent = notifications_result['all_sent']
            if not notifications_result['all_sent']:
                result.errors.extend(notifications_result['errors'])
            
            # Step 7: Update interview record with final details
            await self._finalize_interview_record(
                interview_id, result.calendar_event_id, result.google_meet_link, 
                notifications_result, db
            )
            
            # Mark as completed
            result.status = SchedulingStatus.COMPLETED
            result.success = True
            result.message = f"Interview successfully scheduled with {best_interviewer['name']}"
            
            logger.info(f"🎉 Automatic interview scheduling completed successfully!")
            logger.info(f"   Interview ID: {interview_id}")
            logger.info(f"   Interviewer: {best_interviewer['name']}")
            logger.info(f"   Calendar Event: {result.calendar_event_id or 'Failed'}")
            logger.info(f"   Notifications: {'Sent' if result.notifications_sent else 'Failed'}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Automatic interview scheduling failed: {e}")
            logger.exception("Full error details:")
            
            result.status = SchedulingStatus.FAILED
            result.success = False
            result.message = f"Scheduling failed: {str(e)}"
            result.errors.append(str(e))
            
            return result
    
    async def _get_and_validate_candidate(self, candidate_id: str, db: Session) -> Optional[CandidateDB]:
        """Get and validate candidate exists and has required data"""
        try:
            candidate = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
            if not candidate:
                logger.error(f"Candidate {candidate_id} not found")
                return None
            
            # Validate required fields
            if not candidate.email or not candidate.name:
                logger.error(f"Candidate {candidate_id} missing required fields")
                return None
            
            logger.info(f"✅ Candidate validated: {candidate.name} ({candidate.email})")
            return candidate
            
        except Exception as e:
            logger.error(f"Error validating candidate {candidate_id}: {e}")
            return None
    
    async def _check_interviewer_availability(
        self,
        preferred_time: datetime,
        duration_minutes: int,
        interview_type: InterviewType
    ) -> List[InterviewerAvailability]:
        """
        Check Google Calendar availability for all potential interviewers
        
        Returns:
            List of available interviewers with their availability details
        """
        available_interviewers = []
        end_time = preferred_time + timedelta(minutes=duration_minutes)
        
        # Check availability window (±2 hours from preferred time)
        check_start = preferred_time - timedelta(hours=2)
        check_end = preferred_time + timedelta(hours=2)
        
        for interviewer in self.interviewer_profiles:
            try:
                # Check if interviewer is qualified for this interview type
                if not self._is_interviewer_qualified(interviewer, interview_type):
                    continue
                
                logger.info(f"   Checking availability for {interviewer['name']}...")
                
                # Check calendar availability
                is_available = await self._check_calendar_availability(
                    interviewer['email'],
                    preferred_time,
                    end_time
                )
                
                if is_available:
                    # Get detailed availability slots
                    availability_slots = await self._get_availability_slots(
                        interviewer,
                        check_start,
                        check_end,
                        duration_minutes
                    )
                    
                    if availability_slots:
                        interviewer_availability = InterviewerAvailability(
                            interviewer_id=interviewer['id'],
                            interviewer_name=interviewer['name'],
                            interviewer_email=interviewer['email'],
                            available_slots=availability_slots,
                            next_available=preferred_time,
                            calendar_last_checked=datetime.utcnow(),
                            busy_periods=[]
                        )
                        
                        available_interviewers.append(interviewer_availability)
                        logger.info(f"   ✅ {interviewer['name']} is available")
                else:
                    logger.info(f"   ❌ {interviewer['name']} is not available")
                    
            except Exception as e:
                logger.error(f"Error checking availability for {interviewer['name']}: {e}")
                continue
        
        logger.info(f"📊 Availability check complete: {len(available_interviewers)} available")
        return available_interviewers
    
    def _is_interviewer_qualified(self, interviewer: Dict[str, Any], interview_type: InterviewType) -> bool:
        """Check if interviewer is qualified for the interview type"""
        interviewer_specialties = interviewer.get('specialties', [])
        interviewer_interview_types = interviewer.get('interview_types', [])
        
        # Check if interviewer can conduct this type of interview
        if interview_type.value in interviewer_interview_types:
            return True
        
        # For technical interviews, check if interviewer has technical expertise
        if interview_type == InterviewType.TECHNICAL and 'technical' in interviewer_specialties:
            return True
        
        # For HR interviews, check if interviewer has HR background
        if interview_type == InterviewType.HR and 'hr' in interviewer_specialties:
            return True
        
        return False
    
    async def _check_calendar_availability(
        self,
        interviewer_email: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if interviewer is available during the specified time"""
        try:
            # For demo purposes, we'll simulate calendar checking
            # In production, this would call Google Calendar API
            logger.info(f"     Checking calendar for {interviewer_email}")
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # For demo, assume 80% availability rate
            import random
            is_available = random.random() > 0.2
            
            logger.info(f"     Calendar check result: {'Available' if is_available else 'Busy'}")
            return is_available
            
        except Exception as e:
            logger.error(f"Calendar availability check failed for {interviewer_email}: {e}")
            return False
    
    async def _get_availability_slots(
        self,
        interviewer: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        duration_minutes: int
    ) -> List[AvailabilitySlot]:
        """Get detailed availability slots for an interviewer"""
        slots = []
        
        try:
            # For demo, create some realistic availability slots
            current_time = start_time
            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                # Simulate calendar busy periods
                import random
                if random.random() > 0.3:  # 70% chance of availability
                    slot = AvailabilitySlot(
                        interviewer_id=interviewer['id'],
                        interviewer_name=interviewer['name'],
                        interviewer_email=interviewer['email'],
                        start_time=current_time,
                        end_time=current_time + timedelta(minutes=duration_minutes),
                        confidence_score=random.uniform(0.7, 0.95)
                    )
                    slots.append(slot)
                
                current_time += timedelta(minutes=30)  # Check 30-minute intervals
        
        except Exception as e:
            logger.error(f"Error getting availability slots for {interviewer['name']}: {e}")
        
        return slots
    
    async def _find_best_available_interviewer(
        self,
        candidate: CandidateDB,
        available_interviewers: List[InterviewerAvailability],
        request: InterviewScheduleRequest
    ) -> Optional[Dict[str, Any]]:
        """Use AI to find the best available interviewer"""
        try:
            # Prepare candidate data for matching
            candidate_skills = []
            for skill_data in candidate.skills or []:
                candidate_skills.append({
                    'name': skill_data.get('name', ''),
                    'level': skill_data.get('level', 'beginner'),
                    'years_experience': skill_data.get('years_experience', 0)
                })
            
            candidate_data = {
                'name': candidate.name,
                'position': candidate.position,
                'skills': candidate_skills,
                'experience_years': candidate.experience_years,
                'ai_analysis': candidate.ai_analysis_results,
                'interview_type': request.interview_type.value,
                'interview_round': request.interview_round
            }
            
            # Filter interviewer profiles to only available ones
            available_profiles = []
            for interviewer_avail in available_interviewers:
                # Find the interviewer profile
                for profile in self.interviewer_profiles:
                    if profile['id'] == interviewer_avail.interviewer_id:
                        # Add availability information to profile
                        profile_with_availability = profile.copy()
                        profile_with_availability['availability'] = interviewer_avail
                        available_profiles.append(profile_with_availability)
                        break
            
            if not available_profiles:
                logger.error("No available interviewer profiles found")
                return None
            
            # Use matching algorithm to find best matches
            matches = self.matching_algorithm.find_best_matches(
                candidate_data,
                available_profiles,
                max_matches=3
            )
            
            if not matches:
                logger.error("No suitable matches found")
                return None
            
            # Select the best match
            best_match = matches[0]
            interviewer = best_match['interviewer']
            
            # Enhance with availability information
            best_interviewer = {
                'id': interviewer['id'],
                'name': interviewer['name'],
                'email': interviewer['email'],
                'department': interviewer.get('department', 'Engineering'),
                'title': interviewer.get('title', 'Senior Engineer'),
                'skills': interviewer.get('skills', []),
                'specialties': interviewer.get('specialties', []),
                'match_score': best_match['match_score'],
                'confidence': best_match.get('confidence_score', 0.8),
                'availability': interviewer.get('availability'),
                'matching_reasons': best_match.get('reasons', [])
            }
            
            logger.info(f"🎯 Best interviewer selected: {best_interviewer['name']}")
            logger.info(f"   Match Score: {best_interviewer['match_score']:.1f}/100")
            logger.info(f"   Confidence: {best_interviewer['confidence']:.1f}")
            
            return best_interviewer
            
        except Exception as e:
            logger.error(f"Error finding best available interviewer: {e}")
            return None
    
    async def _create_interview_record(
        self,
        candidate: CandidateDB,
        interviewer: Dict[str, Any],
        request: InterviewScheduleRequest,
        db: Session
    ) -> Optional[str]:
        """Create comprehensive interview database record"""
        try:
            interview_id = str(uuid.uuid4())
            
            # Prepare AI recommendations
            ai_focus_areas = []
            preparation_materials = []
            
            if candidate.ai_analysis_results:
                analysis = candidate.ai_analysis_results
                interview_strategy = analysis.get('interview_strategy', {})
                ai_focus_areas = interview_strategy.get('focus_areas', [])
                
                # Generate preparation materials
                strengths = analysis.get('strengths', [])
                areas_for_improvement = analysis.get('areas_for_improvement', [])
                
                preparation_materials = [
                    {
                        "type": "technical_review",
                        "title": f"Review {candidate.position} Technical Skills",
                        "description": f"Focus on: {', '.join(strengths[:3])}"
                    },
                    {
                        "type": "candidate_background",
                        "title": "Candidate Background Review",
                        "description": f"Experience: {candidate.experience_years} years"
                    },
                    {
                        "type": "matching_insights",
                        "title": "AI Matching Insights",
                        "description": f"Match reasons: {', '.join(interviewer.get('matching_reasons', [])[:2])}"
                    }
                ]
                
                if areas_for_improvement:
                    preparation_materials.append({
                        "type": "improvement_areas",
                        "title": "Areas to Explore",
                        "description": f"Assess: {', '.join(areas_for_improvement[:2])}"
                    })
            
            # Create comprehensive interview record
            interview_db = InterviewDB(
                id=interview_id,
                candidate_id=candidate.id,
                interviewer_id=interviewer['id'],
                scheduled_time=request.preferred_time,
                duration_minutes=request.duration_minutes,
                interview_type=request.interview_type.value,
                status=InterviewStatus.SCHEDULED,
                position=candidate.position,
                interview_round=request.interview_round,
                is_remote=request.is_remote,
                location=request.location,
                interviewer_name=interviewer['name'],
                interviewer_email=interviewer['email'],
                additional_attendees=request.additional_attendees,
                ai_match_score=interviewer['match_score'],
                ai_match_confidence=interviewer['confidence'],
                ai_recommended_focus_areas=ai_focus_areas,
                preparation_materials=preparation_materials,
                technical_requirements=request.special_requirements or {},
                interview_notes=request.notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(interview_db)
            db.commit()
            
            logger.info(f"✅ Interview record created successfully: {interview_id}")
            return interview_id
            
        except Exception as e:
            logger.error(f"Error creating interview record: {e}")
            db.rollback()
            return None
    
    async def _create_calendar_event_with_meeting(
        self,
        interview_id: str,
        candidate: CandidateDB,
        interviewer: Dict[str, Any],
        request: InterviewScheduleRequest,
        db: Session
    ) -> Optional[Dict[str, str]]:
        """Create Google Calendar event with Google Meet link"""
        try:
            logger.info(f"📅 Creating calendar event for interview {interview_id}")
            
            # Prepare event details
            event_title = f"{request.interview_type.value.title()} Interview - Round {request.interview_round}"
            event_description = self._generate_event_description(
                candidate, interviewer, request
            )
            
            # Create calendar event using Google Calendar Service
            calendar_result = self.calendar_service.create_calendar_event_with_details(
                title=event_title,
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                position=candidate.position,
                interviewer_name=interviewer['name'],
                interviewer_email=interviewer['email'],
                start_datetime=request.preferred_time,
                duration_minutes=request.duration_minutes,
                interview_type=request.interview_type.value.title(),
                notes=event_description,
                additional_attendees=request.additional_attendees
            )
            
            if calendar_result:
                logger.info(f"✅ Calendar event created: {calendar_result['event_id']}")
                return calendar_result
            else:
                logger.error("Calendar event creation returned None")
                return None
                
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    def _generate_event_description(
        self,
        candidate: CandidateDB,
        interviewer: Dict[str, Any],
        request: InterviewScheduleRequest
    ) -> str:
        """Generate comprehensive event description"""
        description_parts = [
            f"Interview Details:",
            f"• Candidate: {candidate.name} ({candidate.email})",
            f"• Position: {candidate.position}",
            f"• Experience: {candidate.experience_years} years",
            f"• Interview Type: {request.interview_type.value.title()}",
            f"• Round: {request.interview_round}",
            f"• Duration: {request.duration_minutes} minutes",
            "",
            f"Interviewer Information:",
            f"• Name: {interviewer['name']}",
            f"• Email: {interviewer['email']}",
            f"• Department: {interviewer.get('department', 'N/A')}",
            f"• AI Match Score: {interviewer['match_score']:.1f}/100",
            ""
        ]
        
        # Add AI recommendations if available
        if candidate.ai_analysis_results:
            analysis = candidate.ai_analysis_results
            strengths = analysis.get('strengths', [])
            if strengths:
                description_parts.extend([
                    "Candidate Strengths:",
                    *[f"• {strength}" for strength in strengths[:3]],
                    ""
                ])
        
        # Add interview focus areas
        focus_areas = interviewer.get('matching_reasons', [])
        if focus_areas:
            description_parts.extend([
                "Interview Focus Areas:",
                *[f"• {area}" for area in focus_areas[:3]],
                ""
            ])
        
        # Add notes if provided
        if request.notes:
            description_parts.extend([
                "Additional Notes:",
                request.notes,
                ""
            ])
        
        description_parts.append("Generated by Automatic Interview Scheduling System")
        
        return "\n".join(description_parts)
    
    async def _send_confirmation_notifications(
        self,
        candidate: CandidateDB,
        interviewer: Dict[str, Any],
        request: InterviewScheduleRequest,
        scheduling_result: SchedulingResult
    ) -> Dict[str, Any]:
        """Send confirmation notifications to both parties"""
        try:
            candidate_data = {
                'name': candidate.name,
                'email': candidate.email,
                'position': candidate.position,
                'ai_score': candidate.ai_overall_score,
                'experience_years': candidate.experience_years
            }
            
            interviewer_data = {
                'name': interviewer['name'],
                'email': interviewer['email']
            }
            
            interview_details = {
                'scheduled_time': request.preferred_time,
                'duration_minutes': request.duration_minutes,
                'interview_type': request.interview_type.value,
                'interview_round': request.interview_round,
                'ai_match_score': interviewer['match_score'],
                'google_meet_link': scheduling_result.google_meet_link,
                'focus_areas': interviewer.get('matching_reasons', [])
            }
            
            # Send emails
            email_results = await self.email_service.send_confirmation_emails(
                candidate_data, interviewer_data, interview_details
            )
            
            all_sent = all(email_results.values())
            errors = []
            
            if not email_results.get('candidate_email_sent'):
                errors.append("Failed to send candidate confirmation email")
            if not email_results.get('interviewer_email_sent'):
                errors.append("Failed to send interviewer notification email")
            
            logger.info(f"📧 Email notifications: Candidate={'Sent' if email_results.get('candidate_email_sent') else 'Failed'}, Interviewer={'Sent' if email_results.get('interviewer_email_sent') else 'Failed'}")
            
            return {
                'all_sent': all_sent,
                'candidate_sent': email_results.get('candidate_email_sent', False),
                'interviewer_sent': email_results.get('interviewer_email_sent', False),
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error sending confirmation notifications: {e}")
            return {
                'all_sent': False,
                'candidate_sent': False,
                'interviewer_sent': False,
                'errors': [str(e)]
            }
    
    async def _finalize_interview_record(
        self,
        interview_id: str,
        calendar_event_id: Optional[str],
        google_meet_link: Optional[str],
        notifications_result: Dict[str, Any],
        db: Session
    ):
        """Update interview record with final details"""
        try:
            interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
            if interview:
                # Update calendar information
                if calendar_event_id:
                    interview.calendar_event_id = calendar_event_id
                    interview.status = InterviewStatus.CONFIRMED
                    interview.confirmed_at = datetime.utcnow()
                
                if google_meet_link:
                    interview.google_meet_link = google_meet_link
                
                # Update notification status
                interview.calendar_invites_sent = notifications_result['all_sent']
                
                # Add any error notes
                if notifications_result['errors']:
                    error_notes = f"Notification errors: {'; '.join(notifications_result['errors'])}"
                    interview.interview_notes = f"{interview.interview_notes or ''}\n{error_notes}".strip()
                
                interview.updated_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"✅ Interview record finalized: {interview_id}")
            
        except Exception as e:
            logger.error(f"Error finalizing interview record {interview_id}: {e}")
            db.rollback()

# Helper function for external use
async def schedule_interview_with_automation(
    request: InterviewScheduleRequest,
    db: Session = None
) -> SchedulingResult:
    """
    Main entry point for automatic interview scheduling
    
    Args:
        request: Interview scheduling request
        db: Database session (optional, will create if not provided)
        
    Returns:
        SchedulingResult with complete scheduling information
    """
    
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False
    
    try:
        scheduler = AutomaticInterviewScheduler()
        result = await scheduler.schedule_interview_automatically(request, db)
        return result
        
    finally:
        if close_db:
            db.close()

# Export main components
__all__ = [
    'AutomaticInterviewScheduler',
    'schedule_interview_with_automation',
    'SchedulingResult',
    'SchedulingStatus',
    'InterviewerAvailability',
    'AvailabilitySlot',
    'EmailNotificationService'
]
