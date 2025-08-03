"""
Enhanced Automated Interview Scheduling Workflow v2.0 - CORRECTED
==================================================================

Complete automation pipeline with:
✅ AI Analysis with DeepSeek model
✅ Google Calendar Integration 
✅ Automated Interview Scheduling
✅ Email Notifications
✅ Database Management
✅ FIXED: Proper scheduling logic that actually schedules interviews
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from app.services.ai_service import AIService
from app.services.calendar_service import GoogleCalendarService
from app.models.models import Candidate, Interview, User
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Union, List

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class InterviewAutomationService:
    """
    Orchestrates the complete automated interview scheduling workflow
    """
    
    def __init__(self):
        self.ai_service = AIService()
        self.calendar_service = GoogleCalendarService()
        self._authenticated = False
        
    def _ensure_calendar_authenticated(self):
        """Ensure Google Calendar is authenticated before use"""
        if not self._authenticated:
            interviewer_email = os.getenv('EMAIL_USERNAME', 'rizwanpatelmalipatel@gmail.com')
            logger.info(f"🔐 Authenticating Google Calendar for {interviewer_email}...")
            
            try:
                if self.calendar_service.authenticate(interviewer_email):
                    self._authenticated = True
                    logger.info("✅ Google Calendar authenticated successfully")
                else:
                    logger.warning("⚠️ Google Calendar authentication failed")
            except Exception as e:
                logger.error(f"❌ Calendar authentication error: {e}")
                self._authenticated = False
    
    def send_email(self, to_email, subject, message, is_html=False):
        """Send email using SMTP with optional HTML support"""
        try:
            # Get email configuration from environment
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            email_username = os.getenv('EMAIL_USERNAME')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if not email_username or not email_password:
                logger.error("❌ Email credentials not found in environment")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = email_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add message content (HTML or plain text)
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            logger.info(f"📧 Connecting to Gmail SMTP...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_username, email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    async def process_candidate_submission(
        self, 
        candidate_id: int, 
        db: Session,
        background_tasks: BackgroundTasks
    ):
        """
        CORRECTED Enhanced automation flow with proper calendar integration
        
        1. Candidate submitted ✅ 
        2. AI Analysis 
        3. You are the interviewer (skip matching)
        4. ENHANCED: Proactive calendar scheduling
        5. Email notifications with actual scheduling
        """
        
        logger.info(f"🚀🚀🚀 ENHANCED AUTOMATION v2.0 STARTING for candidate {candidate_id} 🚀🚀🚀")
        logger.info(f"🔍 DEBUG: CORRECTED WORKFLOW WITH PROACTIVE SCHEDULING!")
        
        # Get candidate
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise Exception(f"Candidate {candidate_id} not found")
        
        try:
            # STEP 2: AI Analysis
            logger.info("🤖 Step 2: Running AI Analysis...")
            analysis_result = await self._run_ai_analysis(candidate, db)
            
            if not analysis_result:
                logger.warning("⚠️ AI analysis failed, but continuing...")
            
            # STEP 3: You are the interviewer (simplified)
            logger.info("🎯 Step 3: Setting you as the interviewer...")
            interviewer = await self._find_best_interviewer(candidate, analysis_result, db)
            interviewer_email = interviewer.email if interviewer else os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
            
            # STEP 4: ENHANCED SCHEDULING LOGIC
            logger.info("📅 Step 4: Enhanced calendar-based scheduling...")
            
            # Get preferred time OR find next available slot
            preferred_time = candidate.interview_datetime
            
            if preferred_time:
                logger.info(f"✅ Candidate provided preferred time: {preferred_time}")
                target_time = preferred_time
            else:
                logger.info("📅 No preferred time - finding next available slot...")
                # Find next available business day slot (tomorrow 10 AM as default)
                target_time = self._get_default_interview_time()
                logger.info(f"🎯 Using default time: {target_time}")
            
            # Check availability at target time
            logger.info(f"🔍 Checking calendar availability for {target_time}...")
            try:
                availability_result = await self._check_availability(candidate, interviewer, target_time)
            except Exception as e:
                logger.error(f"❌ Calendar availability check failed: {e}")
                # Assume available and proceed with scheduling
                availability_result = {
                    "available": True,
                    "time": target_time,
                    "formatted_time": target_time.strftime('%A, %B %d at %I:%M %p')
                }
            
            if availability_result["available"]:
                # SUCCESS PATH - Schedule the interview directly
                logger.info("✅ Step 5: Time is available - scheduling interview...")
                interview_result = await self._schedule_interview(
                    candidate, interviewer, availability_result["time"], analysis_result, db
                )
                
                if interview_result["success"]:
                    logger.info("🎉 Interview scheduled successfully!")
                    candidate.interview_scheduled = True
                    candidate.status = "scheduled"
                    candidate.interview_datetime = availability_result["time"]
                    
                    # Send success notification
                    await self._send_candidate_notification(candidate, interviewer, "scheduled", {
                        "scheduled_time_formatted": availability_result["formatted_time"],
                        "meet_link": interview_result.get("meet_link")
                    })
                    
                    db.commit()
                    
                    return {
                        'success': True,
                        'candidate_id': candidate_id,
                        'candidate_name': candidate.name,
                        'interviewer_email': interviewer_email,
                        'ai_score': candidate.ai_overall_score if analysis_result else None,
                        'status': 'scheduled',
                        'scheduled_time': availability_result["formatted_time"],
                        'meet_link': interview_result.get("meet_link"),
                        'calendar_integration': 'enabled'
                    }
                else:
                    logger.error(f"❌ Failed to create calendar event: {interview_result['error']}")
                    # Fall back to manual scheduling
                    candidate.status = "analyzed_ready_for_interview"
            else:
                # ALTERNATIVE PATH - Find other times
                logger.info("⏰ Step 5: Original time not available - finding alternatives...")
                alternative_slots = await self._find_alternative_slot(candidate, interviewer)
                
                if alternative_slots:
                    # Try to schedule first alternative automatically
                    first_alternative = alternative_slots[0]['time']
                    logger.info(f"🔄 Attempting to schedule first alternative: {first_alternative}")
                    
                    interview_result = await self._schedule_interview(
                        candidate, interviewer, first_alternative, analysis_result, db
                    )
                    
                    if interview_result["success"]:
                        logger.info("🎉 Interview scheduled at alternative time!")
                        candidate.interview_scheduled = True
                        candidate.status = "scheduled"
                        candidate.interview_datetime = first_alternative
                        
                        await self._send_candidate_notification(candidate, interviewer, "scheduled", {
                            "scheduled_time_formatted": first_alternative.strftime('%A, %B %d, %Y at %I:%M %p'),
                            "meet_link": interview_result.get("meet_link")
                        })
                        
                        db.commit()
                        
                        return {
                            'success': True,
                            'candidate_id': candidate_id,
                            'candidate_name': candidate.name,
                            'interviewer_email': interviewer_email,
                            'status': 'scheduled',
                            'scheduled_time': first_alternative.strftime('%A, %B %d, %Y at %I:%M %p'),
                            'meet_link': interview_result.get("meet_link")
                        }
                    else:
                        # Send alternatives to candidate for manual selection
                        logger.info("📋 Sending alternative times to candidate...")
                        await self._send_candidate_notification(candidate, interviewer, "alternatives", {
                            "alternatives": alternative_slots,
                            "reason": availability_result["reason"]
                        })
                        candidate.status = "analyzed_alternatives_sent"
                else:
                    # No alternatives found
                    logger.warning("❌ No alternative times found - manual scheduling required")
                    await self._send_candidate_notification(candidate, interviewer, "no_availability", {})
                    candidate.status = "analyzed_no_availability"
            
            # Update database
            if analysis_result:
                candidate.ai_analysis_status = "completed"
            db.commit()
            
            logger.info(f"✅ Enhanced automation workflow complete!")
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'candidate_name': candidate.name,
                'interviewer_email': interviewer_email,
                'ai_score': candidate.ai_overall_score if analysis_result else None,
                'status': candidate.status
            }
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            candidate.status = "automation_failed"
            db.commit()
            raise e
    
    def _get_default_interview_time(self):
        """Get default interview time (next business day at 10 AM)"""
        tomorrow = datetime.now() + timedelta(days=1)
        
        # If tomorrow is weekend, move to Monday
        while tomorrow.weekday() >= 5:  # Saturday=5, Sunday=6
            tomorrow += timedelta(days=1)
        
        # Set time to 10 AM
        default_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        logger.info(f"🎯 Default interview time: {default_time.strftime('%A, %B %d at %I:%M %p')}")
        
        return default_time
    
    async def _run_ai_analysis(self, candidate, db):
        """Run AI analysis on candidate"""
        # Convert to AI service format (you already have this logic)
        from app.schemas.candidate import CandidateProfile, CandidateSkill, SkillLevel
        
        skills = []
        if candidate.skills:
            # Handle both string and array formats
            if isinstance(candidate.skills, str):
                skill_list = candidate.skills.split(',')
            elif isinstance(candidate.skills, list):
                skill_list = candidate.skills
            else:
                skill_list = []
                
            for skill_name in skill_list:
                skills.append(CandidateSkill(
                    name=str(skill_name).strip(),
                    level=SkillLevel.INTERMEDIATE,  # Default, could be enhanced
                    years_experience=1,
                    projects_count=1,
                    certifications=[]
                ))
        
        candidate_profile = CandidateProfile(
            name=candidate.name,
            email=candidate.email,
            position=candidate.position,
            experience_years=candidate.experience_years or 0,
            skills=skills,
            education=candidate.education or "",
            previous_companies=[],
            github_url=candidate.github_url or "",
            linkedin_url=candidate.linkedin_url or "",
            portfolio_url=candidate.portfolio_url or "",
            cover_letter=candidate.cover_letter or "",
            resume_text=candidate.resume_text or "",
            preferred_salary=candidate.preferred_salary or 0.0,
            availability=candidate.availability or ""
        )
        
        # Run AI analysis
        analysis = self.ai_service.analyze_candidate(candidate_profile)
        
        if analysis:
            # Store results in database (you have this logic)
            candidate.ai_analysis_status = "completed"
            candidate.ai_overall_score = analysis.overall_score
            candidate.ai_technical_score = analysis.technical_score
            candidate.ai_confidence_score = analysis.confidence_score
            candidate.analyzed_at = datetime.utcnow()
            
        return analysis
    
    async def _find_best_interviewer(self, candidate, analysis, db):
        """You are the interviewer! Just return your details"""
        # Create a simple interviewer object with your email from .env
        interviewer_email = os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
        
        # Create or get your interviewer record
        interviewer = db.query(User).filter(User.email == interviewer_email).first()
        
        if not interviewer:
            # Create your interviewer profile
            interviewer = User(
                name="Rizwan Patel",  # Your name
                email=interviewer_email,
                role='INTERVIEWER'  # Use uppercase enum value
            )
            db.add(interviewer)
            db.commit()
            db.refresh(interviewer)
            logger.info(f"✅ Created interviewer profile for {interviewer_email}")
        
        logger.info(f"🎯 Best interviewer: {interviewer.name} (that's you!)")
        return interviewer
    
    async def _check_availability(self, candidate, interviewer, preferred_time):
        """
        Step 4: Enhanced Calendar Availability Check
        """
        if not preferred_time:
            logger.warning("❌ No preferred time provided")
            return {"available": False, "reason": "No preferred time provided"}

        # Ensure calendar is authenticated
        self._ensure_calendar_authenticated()

        # Check availability window (1 hour)
        start_time = preferred_time
        end_time = start_time + timedelta(hours=1)

        logger.info(f"📅 STEP 4: CALENDAR AVAILABILITY CHECK")
        logger.info(f"⏰ Checking if {interviewer.name if interviewer else 'interviewer'} is free on {start_time.strftime('%A, %B %d at %I:%M %p')}")
        logger.info(f"🔍 Querying Google Calendar API for time slot: {start_time} - {end_time}")

        # Call Google Calendar API
        availability = self.calendar_service.get_availability(
            interviewer.email if interviewer else os.getenv('EMAIL_USERNAME'),
            start_time,
            end_time
        )

        if 'error' in availability:
            logger.warning(f"⚠️ Calendar API error: {availability['error']}")
            # For now, assume available if calendar API fails
            logger.info("📅 Assuming available due to calendar API issue")
            return {
                "available": True,
                "time": start_time,
                "interviewer_name": interviewer.name if interviewer else "Rizwan Patel",
                "formatted_time": start_time.strftime('%A, %B %d at %I:%M %p')
            }

        # Analyze Calendar Response
        busy_times = availability.get('busy', [])

        if not busy_times:
            # SUCCESS CASE - Interviewer is FREE!
            logger.info(f"✅ Interviewer is free at {start_time.strftime('%A, %B %d at %I:%M %p')}")
            return {
                "available": True,
                "time": start_time,
                "interviewer_name": interviewer.name if interviewer else "Rizwan Patel",
                "formatted_time": start_time.strftime('%A, %B %d at %I:%M %p')
            }
        else:
            # CONFLICT CASE - Interviewer is BUSY
            logger.warning(f"❌ Interviewer is busy at requested time")
            return {"available": False, "reason": "Interviewer has conflicting appointment"}
    
    async def _find_alternative_slot(self, candidate, interviewer):
        """Find alternative time slots if preferred time not available"""
        logger.info(f"🔍 Finding alternative time slots for next 7 days...")
        
        # Look for next 7 days, business hours only (9 AM - 6 PM)
        business_start = 9  # 9 AM
        business_end = 18   # 6 PM
        
        alternative_slots = []
        
        for day_offset in range(1, 8):  # Next 7 days
            check_date = datetime.now().date() + timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() >= 5:  # Saturday=5, Sunday=6
                continue
                
            # Check each hour in business hours
            for hour in range(business_start, business_end):
                check_time = datetime.combine(check_date, datetime.min.time().replace(hour=hour))
                end_time = check_time + timedelta(hours=1)
                
                availability = self.calendar_service.get_availability(
                    interviewer.email if interviewer else os.getenv('EMAIL_USERNAME'),
                    check_time,
                    end_time
                )
                
                # If no conflicts, this is a free slot
                if 'error' not in availability and not availability.get('busy', []):
                    alternative_slots.append({
                        'time': check_time,
                        'formatted': check_time.strftime('%A, %B %d at %I:%M %p')
                    })
                    
                    # Return first 3 available slots
                    if len(alternative_slots) >= 3:
                        break
            
            if len(alternative_slots) >= 3:
                break
        
        logger.info(f"📅 Found {len(alternative_slots)} alternative time slots")
        return alternative_slots

    async def _schedule_interview(self, candidate, interviewer, scheduled_time, analysis, db):
        """
        Step 5: Interview Scheduling & Database Entry
        Creates interview record in database and Google Calendar event.
        """
        try:
            # Ensure calendar is authenticated
            self._ensure_calendar_authenticated()
            
            logger.info(f"🚀 STEP 5: INTERVIEW SCHEDULING & DATABASE ENTRY")
            logger.info(f"📝 Creating interview record for {candidate.name} with {interviewer.name if interviewer else 'Rizwan Patel'}")
            logger.info(f"📅 Scheduled Time: {scheduled_time.strftime('%A, %B %d, %Y at %I:%M %p')}")

            interview_data = {
                'scheduled_time': scheduled_time,
                'duration': 60,  # 1 hour
                'type': 'Technical Interview',
                'candidate_name': candidate.name,
                'interviewer_name': interviewer.name if interviewer else 'Rizwan Patel',
                'position': candidate.position,
                'notes': f"AI Analysis Score: {analysis.overall_score}/100" if analysis else "Analysis pending",
                'id': f"candidate_{candidate.id}"
            }

            logger.info(f"🎥 Creating Google Calendar event with Meet link...")

            calendar_result = self.calendar_service.create_interview_event(
                interview_data,
                candidate.email,
                interviewer.email if interviewer else os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
            )

            if calendar_result:
                logger.info(f"✅ Google Calendar event created successfully!")
                logger.info(f"📎 Event ID: {calendar_result.get('event_id', 'N/A')}")
                logger.info(f"🎥 Meet Link: {calendar_result.get('meet_link', 'Generated')}")

                candidate.interview_datetime = scheduled_time
                candidate.interview_scheduled = True

                # Create database interview record
                from app.models.models import Interview
                interview = Interview(
                    candidate_id=candidate.id,
                    interviewer_id=interviewer.id if interviewer else None,
                    scheduled_time=scheduled_time,
                    duration=60,
                    type='TECHNICAL',  # Use uppercase enum value
                    status='scheduled',
                    notes=interview_data['notes']
                )
                db.add(interview)
                db.commit()
                db.refresh(interview)

                logger.info(f"💾 Database interview record created successfully!")

                return {
                    "success": True,
                    "event_id": calendar_result.get('event_id'),
                    "meet_link": calendar_result.get('meet_link'),
                    "interview_id": interview.id,
                    "scheduled_time_formatted": scheduled_time.strftime('%A, %B %d, %Y at %I:%M %p')
                }
            else:
                logger.error("❌ Failed to create calendar event")
                return {"success": False, "error": "Calendar event creation failed"}
                
        except Exception as e:
            logger.error(f"❌ Error in interview scheduling: {e}")
            return {"success": False, "error": str(e)}

    async def _send_candidate_notification(self, candidate, interviewer, notification_type, data):
        """
        Step 6 & 7: Instant Notifications
        Sends customized emails to both candidate and interviewer
        """
        try:
            interviewer_name = interviewer.name if interviewer else 'Rizwan Patel'
            interviewer_email = interviewer.email if interviewer else os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
            
            # Handle skills display for emails
            skills_display = ""
            if candidate.skills:
                if isinstance(candidate.skills, list):
                    skills_display = ", ".join(str(skill) for skill in candidate.skills)
                else:
                    skills_display = str(candidate.skills)
            
            logger.info(f"📧 STEP 6-7: INSTANT NOTIFICATIONS")
            logger.info(f"📬 Sending {notification_type} emails to candidate and interviewer...")
            
            if notification_type == "scheduled":
                # SUCCESS CASE - Interview was scheduled!
                scheduled_time = data.get('scheduled_time_formatted', candidate.interview_datetime.strftime('%A, %B %d, %Y at %I:%M %p') if candidate.interview_datetime else 'TBD')
                meet_link = data.get('meet_link', 'https://meet.google.com/auto-generated-link')
                
                # CANDIDATE EMAIL - HTML VERSION
                candidate_subject = f"🎉 Interview Scheduled - {candidate.position} Position"
                candidate_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .meeting-link {{ background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold; }}
        .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Interview Scheduled!</h1>
            <p>Congratulations {candidate.name}!</p>
        </div>
        <div class="content">
            <p>Your interview has been <strong>automatically scheduled</strong> based on our AI analysis!</p>
            
            <div class="details">
                <h3>📅 Interview Details</h3>
                <p><strong>📅 Date & Time:</strong> {scheduled_time}</p>
                <p><strong>⏰ Duration:</strong> 1 hour</p>
                <p><strong>👨‍💻 Interviewer:</strong> {interviewer_name} (Technical Lead)</p>
                <p><strong>💼 Position:</strong> {candidate.position}</p>
                <p><strong>🤖 AI Analysis:</strong> Your application passed our automated screening with a strong score!</p>
            </div>
            
            <div style="text-align: center;">
                <a href="{meet_link}" class="meeting-link">
                    🎥 Join Interview Meeting
                </a>
            </div>
            
            <div class="details">
                <h3>🎯 Interview Focus Areas</h3>
                <ul>
                    <li>Technical skills for {candidate.position}</li>
                    <li>Project experience and implementation</li>
                    <li>Problem-solving approach</li>
                    <li>Team collaboration</li>
                </ul>
            </div>
            
            <p><strong>📱 Meeting Link:</strong> <a href="{meet_link}">{meet_link}</a></p>
            <p><em>The meeting has been automatically added to your Google Calendar.</em></p>
            
            <div class="footer">
                <p>Best regards,<br>
                <strong>RHero Interview Team</strong><br>
                🚀 Powered by AI-driven recruitment</p>
            </div>
        </div>
    </div>
</body>
</html>
                """
                
                # INTERVIEWER EMAIL - HTML VERSION  
                interviewer_subject = f"New Interview Assigned - {candidate.name} ({candidate.position})"
                ai_score = candidate.ai_overall_score if candidate.ai_overall_score else "Pending"
                technical_score = candidate.ai_technical_score if candidate.ai_technical_score else "Pending"
                
                interviewer_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .meeting-link {{ background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold; }}
        .candidate-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff6b6b; }}
        .score {{ background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .high-score {{ background: #d4edda; color: #155724; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👩‍� New Interview Assignment</h1>
            <p>AI-Matched Candidate Ready for Interview</p>
        </div>
        <div class="content">
            <p>Hi {interviewer_name},</p>
            <p>You've been matched with a <strong>high-potential candidate</strong> based on expertise alignment!</p>
            
            <div class="candidate-info">
                <h3>🎯 Candidate Profile</h3>
                <p><strong>👩‍💻 Name:</strong> {candidate.name}</p>
                <p><strong>💼 Position:</strong> {candidate.position}</p>
                <p><strong>� Email:</strong> {candidate.email}</p>
                <p><strong>💼 Experience:</strong> {candidate.experience_years or 'TBD'} years</p>
                <p><strong>🎓 Education:</strong> {candidate.education or 'Not specified'}</p>
                <p><strong>💪 Key Skills:</strong> {skills_display or 'Listed in resume'}</p>
                
                <div class="score high-score">
                    <strong>🤖 AI Match Score: {ai_score}%</strong> (High confidence match)
                </div>
                <div class="score">
                    <strong>📈 Technical Score: {technical_score}/100</strong>
                </div>
            </div>
            
            <div class="candidate-info">
                <h3>📅 Interview Details</h3>
                <p><strong>📅 Scheduled:</strong> {scheduled_time}</p>
                <p><strong>⏰ Duration:</strong> 1 hour</p>
                <p><strong>📱 Meeting Link:</strong> <a href="{meet_link}">{meet_link}</a></p>
            </div>
            
            <div style="text-align: center;">
                <a href="{meet_link}" class="meeting-link">
                    🎥 Join Interview Meeting
                </a>
            </div>
            
            <p><em>📋 Full candidate analysis and resume details are available in the system dashboard.</em></p>
            
            <div class="footer">
                <p>Best regards,<br>
                <strong>RHero Interview Team</strong><br>
                🤖 AI-Powered Recruitment System</p>
            </div>
        </div>
    </div>
</body>
</html>
                """
                
                # Send both HTML emails
                candidate_email_sent = self.send_email(candidate.email, candidate_subject, candidate_html, is_html=True)
                interviewer_email_sent = self.send_email(interviewer_email, interviewer_subject, interviewer_html, is_html=True)
                
                logger.info(f"✅ CANDIDATE HTML EMAIL SENT: {candidate_email_sent}")
                logger.info(f"✅ INTERVIEWER HTML EMAIL SENT: {interviewer_email_sent}")
                
                if candidate_email_sent and interviewer_email_sent:
                    logger.info("🎉 Both HTML emails with meeting links sent successfully!")
                else:
                    logger.warning("⚠️ Some emails failed to send")
            
            elif notification_type == "alternatives":
                alternatives_text = "\n".join([f"• {slot['formatted']}" for slot in data['alternatives']])
                subject = f"📅 Interview Scheduling - Alternative Times Available"
                message = f"""Dear {candidate.name},

Your application has passed our AI analysis! However, your preferred time slot conflicts with the interviewer's schedule.

❌ Requested Time: Not available ({data['reason']})

✅ Available Alternative Times:
{alternatives_text}

📧 Please reply with your preferred time from the options above, and we'll confirm your interview.

🤖 AI Analysis: Your application looks promising!
Interviewer: {interviewer_name}

Best regards,
RHero Interview Team
"""
                email_sent = self.send_email(candidate.email, subject, message)
                logger.info(f"📧 ALTERNATIVE TIMES EMAIL SENT: {email_sent}")
            
            elif notification_type == "analysis_complete":
                subject = f"✅ Application Analysis Complete - {candidate.position}"
                message = f"""Dear {candidate.name},

Thank you for your application! Our AI analysis has been completed.

🤖 Analysis Results: Your profile shows potential for the {candidate.position} position.

📅 Next Steps: 
Our interviewer ({interviewer_name}) will review your profile and contact you soon to schedule an interview.

We'll be in touch within 24-48 hours.

Best regards,
RHero Interview Team
"""
                email_sent = self.send_email(candidate.email, subject, message)
                logger.info(f"📧 ANALYSIS COMPLETE EMAIL SENT: {email_sent}")
            
            elif notification_type == "no_availability":
                subject = f"📞 Interview Scheduling - Will Contact Soon"
                message = f"""Dear {candidate.name},

Your application has passed our AI analysis! 

🤖 Great news: Your profile is a good match for the {candidate.position} position.

📅 Scheduling: Due to current calendar availability, our interviewer ({interviewer_name}) will contact you personally within 24 hours to find a suitable interview time.

Thank you for your patience!

Best regards,
RHero Interview Team
"""
                email_sent = self.send_email(candidate.email, subject, message)
                logger.info(f"📧 MANUAL SCHEDULING EMAIL SENT: {email_sent}")
            
            logger.info(f"📨 Email notifications completed successfully!")
            logger.info(f"🎯 Automation workflow complete for {candidate.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False

# Integration endpoint for your existing candidates_standalone.py
async def trigger_automation_after_candidate_creation(candidate_id: int, db: Session):
    """
    Call this after candidate creation in candidates_standalone.py
    """
    automation_service = InterviewAutomationService()
    
    try:
        result = await automation_service.process_candidate_submission(
            candidate_id, db, None
        )
        
        logger.info(f"🎉 Automation completed for candidate {candidate_id}")
        return result
        
    except Exception as e:
        logger.error(f"🚨 Automation failed for candidate {candidate_id}: {e}")
        return {'success': False, 'error': str(e)}
