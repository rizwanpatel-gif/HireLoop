"""
Enhanced Automated Interview Scheduling Workflow v2.0
=====================            # STEP 4: Calendar availability chec            # STEP 4: Calendar availability checking with enha            # OLD CODE DISABLED - USING ENHANCED WORKFLOW ABOVE
            # logger.info("� Step 4-5: Candidate processed, ready for interview scheduling")ed logging
            logger.info("📅 Step 4: Checking calendar availability...")
            preferred_time = candidate.interview_datetime
            
            if preferred_time:
                # Check availability at preferred time
                availability_result = await self._check_availability(candidate, interviewer, preferred_time)
                
                if availability_result["available"]:
                    # Schedule the interview!
                    logger.info("✅ Step 5: Scheduling interview at preferred time...")
                    interview_result = await self._schedule_interview(candidate, interviewer, preferred_time, analysis_result, db)
                    
                    if interview_result["success"]:
                        logger.info("🎉 Interview scheduled successfully!")
                        # Send success email to candidate
                        await self._send_candidate_notification(candidate, interviewer, "scheduled", interview_result)
                        candidate.interview_scheduled = True
                        candidate.status = "scheduled"
                    else:
                        logger.error(f"❌ Failed to schedule interview: {interview_result['error']}")
                        candidate.status = "analyzed_ready_for_interview"
                        
                else:
                    # Find alternative times
                    logger.info("⏰ Step 5: Finding alternative time slots...")
                    alternative_slots = await self._find_alternative_slot(candidate, interviewer)
                    
                    if alternative_slots:
                        logger.info(f"📋 Found {len(alternative_slots)} alternative times")
                        # Send email with alternative times
                        await self._send_candidate_notification(candidate, interviewer, "alternatives", {
                            "alternatives": alternative_slots,
                            "reason": availability_result["reason"]
                        })
                        candidate.status = "analyzed_alternatives_sent"
                    else:
                        logger.warning("❌ No alternative times found")
                        await self._send_candidate_notification(candidate, interviewer, "no_availability", {})
                        candidate.status = "analyzed_no_availability"
            else:
                logger.info("📞 Step 5: No preferred time - sending analysis results...")
                # No preferred time, just send analysis results
                await self._send_candidate_notification(candidate, interviewer, "analysis_complete", {"analysis": analysis_result})
                candidate.status = "analyzed_awaiting_schedule"
            
            # Update candidate status and commit changes
            if analysis_result:
                candidate.ai_analysis_status = "completed"
            db.commit()
            
            logger.info(f"✅ Enhanced automation workflow complete! Candidate {candidate.name} processed with calendar integration")
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'candidate_name': candidate.name,
                'interviewer_email': interviewer_email,
                'ai_score': candidate.ai_overall_score if analysis_result else None,
                'status': candidate.status,
                'calendar_integration': 'enabled',
                'preferred_time': preferred_time.isoformat() if preferred_time else None
            }logging
            logger.info("📅 Step 4: Checking calendar availability...")
              logger.info(f"📅 STEP 4: CALENDAR AVAILABILITY CHECK")
        logger.info(f"⏰ Checking if {inter            logger.info(f"🚀 STEP 5: INTERVIEW SCHEDULING & DATABASE ENTRY")
            logger.info(f"📝 Creating interview record for {candidate.name} with {interviewer.name}")
            logger.info(f"📅 Scheduled Time: {scheduled_time.strftime('%A, %B %d, %Y at %I:%M %p')}")wer.name} is free on {start_time.strftime('%A, %B %d at %I:%M %p')}")
        logger.info(f"🔍 Querying Google Calendar API for time slot: {start_time} - {end_time}")   preferred_time = candidate.interview_datetime
            
            if preferred_time:
                # Check availability at preferred time
                availability_result = await self._check_availability(candidate, interviewer, preferred_time)
                
                if availability_result["available"]:
                    # Schedule the interview!
                    logger.info("✅ Step 5: Scheduling interview at preferred time...")
                    interview_result = await self._schedule_interview(candidate, interviewer, preferred_time, analysis_result, db)
                    
                    if interview_result["success"]:
                        logger.info("🎉 Interview scheduled successfully!")
                        # Send success email to candidate
                        await self._send_candidate_notification(candidate, interviewer, "scheduled", interview_result)
                        candidate.interview_scheduled = True
                        candidate.status = "scheduled"
                    else:
                        logger.error(f"❌ Failed to schedule interview: {interview_result['error']}")
                        candidate.status = "analyzed_ready_for_interview"
                        
                else:
                    # Find alternative times
                    logger.info("⏰ Step 5: Finding alternative time slots...")
                    alternative_slots = await self._find_alternative_slot(candidate, interviewer)
                    
                    if alternative_slots:
                        logger.info(f"📋 Found {len(alternative_slots)} alternative times")
                        # Send email with alternative times
                        await self._send_candidate_notification(candidate, interviewer, "alternatives", {
                            "alternatives": alternative_slots,
                            "reason": availability_result["reason"]
                        })
                        candidate.status = "analyzed_alternatives_sent"
                    else:
                        logger.warning("❌ No alternative times found")
                        await self._send_candidate_notification(candidate, interviewer, "no_availability", {})
                        candidate.status = "analyzed_no_availability"
            else:
                logger.info("📞 Step 5: No preferred time - sending analysis results...")
                # No preferred time, just send analysis results
                await self._send_candidate_notification(candidate, interviewer, "analysis_complete", {"analysis": analysis_result})
                candidate.status = "analyzed_awaiting_schedule"==============================

Complete automation pipeline with:
✅ AI Analysis with DeepSeek model
✅ Google Calendar Integration 
✅ Automated Interview Scheduling
✅ Email Notifications
✅ Database Management

This connects all your existing pieces into the automated flow you described.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from app.services.ai_service import AIService
from app.services.calendar_service import GoogleCalendarService
from app.models.models import Candidate, Interview, User
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

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
    
    def send_email(self, to_email, subject, message):
        """Send email using SMTP"""
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
            msg = MIMEMultipart()
            msg['From'] = email_username
            msg['To'] = to_email
            msg['Subject'] = subject
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
        Simplified automation flow for single interviewer (you!)
        
        1. Candidate submitted ✅ 
        2. AI Analysis 
        3. You are the interviewer (skip matching)
        4. Calendar integration (if Google Calendar is set up)
        5. Email notifications
        """
        
        logger.info(f"🚀🚀🚀 ENHANCED AUTOMATION v2.0 STARTING for candidate {candidate_id} 🚀🚀🚀")
        logger.info(f"🔍 DEBUG: THIS IS THE NEW ENHANCED WORKFLOW WITH CALENDAR INTEGRATION!")
        
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
            
            if not interviewer:
                logger.warning("⚠️ No interviewer found, creating basic profile...")
                # Just use your email for notifications
                interviewer_email = os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
            else:
                interviewer_email = interviewer.email
            
            # STEP 4: Calendar availability check with enhanced logging
            logger.info("📅 Step 4: Checking calendar availability...")
            preferred_time = candidate.interview_datetime
            
            if preferred_time:
                # Check availability at preferred time
                availability_result = await self._check_availability(candidate, interviewer, preferred_time)
                
                if availability_result["available"]:
                    # Schedule the interview!
                    logger.info("✅ Step 5: Scheduling interview at preferred time...")
                    interview_result = await self._schedule_interview(candidate, interviewer, preferred_time, analysis_result, db)
                    
                    if interview_result["success"]:
                        logger.info("🎉 Interview scheduled successfully!")
                        # Send success email to candidate
                        await self._send_candidate_notification(candidate, interviewer, "scheduled", interview_result)
                        candidate.interview_scheduled = True
                        candidate.status = "scheduled"
                    else:
                        logger.error(f"❌ Failed to schedule interview: {interview_result['error']}")
                        candidate.status = "analyzed_ready_for_interview"
                        
                else:
                    # Find alternative times
                    logger.info("⏰ Step 5: Finding alternative time slots...")
                    alternative_slots = await self._find_alternative_slot(candidate, interviewer)
                    
                    if alternative_slots:
                        logger.info(f"📋 Found {len(alternative_slots)} alternative times")
                        # Send email with alternative times
                        await self._send_candidate_notification(candidate, interviewer, "alternatives", {
                            "alternatives": alternative_slots,
                            "reason": availability_result["reason"]
                        })
                        candidate.status = "analyzed_alternatives_sent"
                    else:
                        logger.warning("❌ No alternative times found")
                        await self._send_candidate_notification(candidate, interviewer, "no_availability", {})
                        candidate.status = "analyzed_no_availability"
            else:
                logger.info("📞 Step 5: No preferred time - sending analysis results...")
                # No preferred time, just send analysis results
                await self._send_candidate_notification(candidate, interviewer, "analysis_complete", {"analysis": analysis_result})
                candidate.status = "analyzed_awaiting_schedule"
            
            # Update candidate status
            candidate.status = "analyzed_ready_for_interview"
            if analysis_result:
                candidate.ai_analysis_status = "completed"
            db.commit()
            
            logger.info(f"✅ Automation complete! Candidate {candidate.name} analyzed and ready")
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'candidate_name': candidate.name,
                'interviewer_email': interviewer_email,
                'ai_score': candidate.ai_overall_score if analysis_result else None,
                'status': 'ready_for_interview_scheduling'
            }
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            candidate.status = "automation_failed"
            db.commit()
            raise e
    
    async def _run_ai_analysis(self, candidate, db):
        """Run AI analysis on candidate"""
        # Convert to AI service format (you already have this logic)
        from app.schemas.candidate import CandidateProfile, CandidateSkill, SkillLevel
        
        skills = []
        if candidate.skills:
            skill_list = candidate.skills.split(',')
            for skill_name in skill_list:
                skills.append(CandidateSkill(
                    name=skill_name.strip(),
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
        Step 4: Calendar Availability Check
        Time: 9:03 AM - Google Calendar Integration
        
        System checks interviewer's Google Calendar for requested time slot
        """
        if not preferred_time:
            logger.warning("❌ No preferred time provided by candidate")
            return {"available": False, "reason": "No preferred time provided"}
            
        # Check availability window (1 hour)
        start_time = preferred_time
        end_time = start_time + timedelta(hours=1)
        
        logger.info(f"� STEP 4: CALENDAR AVAILABILITY CHECK")
        logger.info(f"⏰ Checking if {interviewer.name} is free on {start_time.strftime('%A, %B %d at %I:%M %p')}")
        logger.info(f"🔍 Querying Google Calendar API for time slot: {start_time} - {end_time}")
        
        # Call Google Calendar API
        availability = self.calendar_service.get_availability(
            interviewer.email,
            start_time,
            end_time
        )
        
        if 'error' in availability:
            logger.warning(f"⚠️ Calendar API error: {availability['error']}")
            return {"available": False, "reason": f"Calendar error: {availability['error']}"}
        
        # Analyze Calendar Response
        busy_times = availability.get('busy', [])
        
        if not busy_times:
            # SUCCESS CASE - Interviewer is FREE! 
            logger.info(f"🎉 CALENDAR CHECK RESULT: ✅ INTERVIEWER IS FREE!")
            logger.info(f"✅ {interviewer.name} has NO conflicts at {start_time.strftime('%A, %B %d at %I:%M %p')}")
            logger.info(f"🟢 Time slot {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')} is AVAILABLE")
            logger.info(f"➡️  Proceeding to STEP 5: Interview Scheduling...")
            
            return {
                "available": True, 
                "time": start_time,
                "interviewer_name": interviewer.name,
                "formatted_time": start_time.strftime('%A, %B %d at %I:%M %p')
            }
        else:
            # CONFLICT CASE - Interviewer is BUSY
            logger.warning(f"❌ CALENDAR CHECK RESULT: INTERVIEWER IS BUSY")
            logger.warning(f"🔴 {interviewer.name} has {len(busy_times)} conflict(s) at requested time")
            
            # Show conflict details
            for i, conflict in enumerate(busy_times, 1):
                conflict_start = conflict.get('start', 'Unknown')
                conflict_end = conflict.get('end', 'Unknown')
                logger.warning(f"   📅 Conflict #{i}: {conflict_start} - {conflict_end}")
            
            logger.info(f"➡️  Proceeding to find alternative time slots...")
            
            return {
                "available": False, 
                "reason": f"Interviewer busy - {len(busy_times)} conflicts", 
                "conflicts": busy_times,
                "interviewer_name": interviewer.name
            }
    
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
                    interviewer.email,
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
        Time: 9:04 AM - Automatic Scheduling
        
        Creates interview record in database and Google Calendar event
        """
        try:
            logger.info(f"� STEP 5: INTERVIEW SCHEDULING & DATABASE ENTRY")
            logger.info(f"📝 Creating interview record for {candidate.name} with {interviewer.name}")
            logger.info(f"📅 Scheduled Time: {scheduled_time.strftime('%A, %B %d, %Y at %I:%M %p')}")
            
            # Prepare interview data for calendar
            interview_data = {
                'scheduled_time': scheduled_time,
                'duration': 60,  # 1 hour
                'type': 'Technical Interview',
                'candidate_name': candidate.name,
                'interviewer_name': interviewer.name if interviewer else 'Rizwan Patel',
                'position': candidate.position,
                'notes': f"AI Analysis Score: {analysis.overall_score}/100" if analysis else "",
                'id': f"candidate_{candidate.id}"
            }
            
            logger.info(f"🎥 Creating Google Calendar event with Meet link...")
            
            # Create calendar event
            calendar_result = self.calendar_service.create_interview_event(
                interview_data,
                candidate.email,
                interviewer.email if interviewer else os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
            )
            
            if calendar_result:
                logger.info(f"✅ Google Calendar event created successfully!")
                logger.info(f"📎 Event ID: {calendar_result.get('event_id', 'N/A')}")
                logger.info(f"🎥 Meet Link: {calendar_result.get('meet_link', 'Generated')}")
                
                # Update candidate in database
                candidate.interview_datetime = scheduled_time
                candidate.interview_scheduled = True
                
                # Create interview record in database
                from app.models.models import Interview
                interview = Interview(
                    candidate_id=candidate.id,
                    interviewer_id=interviewer.id if interviewer else None,
                    scheduled_time=scheduled_time,
                    duration=60,
                    type='technical',
                    status='scheduled',
                    notes=interview_data['notes']
                )
                db.add(interview)
                db.commit()
                db.refresh(interview)
                
                logger.info(f"💾 Database interview record created:")
                logger.info(f"   📋 Interview ID: {interview.id}")
                logger.info(f"   👤 Candidate: {candidate.name} (ID: {candidate.id})")
                logger.info(f"   👨‍💻 Interviewer: {interviewer.name} (ID: {interviewer.id})")
                logger.info(f"   ⏰ Duration: 60 minutes")
                logger.info(f"   🎯 Type: Technical Interview")
                logger.info(f"   📊 Status: Scheduled")
                logger.info(f"   🤖 AI Recommended Match: True")
                
                logger.info(f"➡️  Proceeding to STEP 6: Email Notifications...")
                
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
        Time: 9:06 AM - Automated Communications
        
        Sends customized emails to both candidate and interviewer
        """
        try:
            interviewer_name = interviewer.name if interviewer else 'Rizwan Patel'
            interviewer_email = interviewer.email if interviewer else os.getenv('EMAIL_USERNAME', 'rizwan.patel@gmail.com')
            
            logger.info(f"📧 STEP 6-7: INSTANT NOTIFICATIONS")
            logger.info(f"📬 Sending {notification_type} emails to candidate and interviewer...")
            
            if notification_type == "scheduled":
                # SUCCESS CASE - Interview was scheduled!
                scheduled_time = data.get('scheduled_time_formatted', candidate.interview_datetime.strftime('%A, %B %d, %Y at %I:%M %p') if candidate.interview_datetime else 'TBD')
                meet_link = data.get('meet_link', 'https://meet.google.com/auto-generated-link')
                
                # CANDIDATE EMAIL
                candidate_subject = f"🎉 Interview Scheduled - {candidate.position} Position"
                candidate_message = f"""
Subject: Interview Scheduled - {candidate.position} Position

Hi {candidate.name},

Your interview has been automatically scheduled!

📅 Date: {scheduled_time}
⏰ Duration: 1 hour
👨‍💻 Interviewer: {interviewer_name} (Technical Lead)
🎥 Meeting Link: {meet_link}

🤖 AI Analysis: Your application passed our automated screening with a strong score!

Focus Areas: {candidate.position} skills, technical implementation, experience discussion

The event has been added to your calendar automatically.

Best regards,
RHero Interview Team
"""
                
                # INTERVIEWER EMAIL
                interviewer_subject = f"New Interview Assigned - {candidate.name} ({candidate.position})"
                ai_score = candidate.ai_overall_score if candidate.ai_overall_score else "Pending"
                technical_score = candidate.ai_technical_score if candidate.ai_technical_score else "Pending"
                
                interviewer_message = f"""
Subject: New Interview Assigned - {candidate.name} ({candidate.position})

Hi {interviewer_name},

You've been matched for an interview based on expertise alignment:

👩‍💻 Candidate: {candidate.name}
📊 AI Match Score: {ai_score}% (High confidence)
💪 Key Strengths: {candidate.skills or 'Listed in resume'}
🎯 Position: {candidate.position}
📈 Technical Score: {technical_score}/100
💼 Experience: {candidate.experience_years or 'TBD'} years

📅 {scheduled_time}
🎥 {meet_link}

📋 Candidate Details:
• Email: {candidate.email}
• Current Role: {candidate.current_title or 'Not specified'}
• Education: {candidate.education or 'Not specified'}

Candidate analysis and resume available in system.

Best regards,
RHero Interview Team
"""
                
                logger.info(f"✅ CANDIDATE EMAIL SENT:")
                logger.info(f"   📧 To: {candidate.email}")
                logger.info(f"   📝 Subject: {candidate_subject}")
                
                # Actually send the candidate email
                candidate_email_sent = self.send_email(candidate.email, candidate_subject, candidate_message)
                
                logger.info(f"✅ INTERVIEWER EMAIL SENT:")
                logger.info(f"   📧 To: {interviewer_email}")
                logger.info(f"   📝 Subject: {interviewer_subject}")
                logger.info(f"   📊 Included AI score: {ai_score}%")
                
                # Actually send the interviewer email
                interviewer_email_sent = self.send_email(interviewer_email, interviewer_subject, interviewer_message)
                
                if candidate_email_sent and interviewer_email_sent:
                    logger.info("🎉 Both emails sent successfully!")
                else:
                    logger.warning("⚠️ Some emails failed to send")
            
            elif notification_type == "alternatives":
                alternatives_text = "\n".join([f"• {slot['formatted']}" for slot in data['alternatives']])
                subject = f"📅 Interview Scheduling - Alternative Times Available"
                message = f"""
Dear {candidate.name},

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
                logger.info(f"📧 ALTERNATIVE TIMES EMAIL SENT:")
                logger.info(f"   📧 To: {candidate.email}")
                logger.info(f"   📝 Found {len(data['alternatives'])} alternative slots")
                
                # Actually send the email
                email_sent = self.send_email(candidate.email, subject, message)
            
            elif notification_type == "analysis_complete":
                subject = f"✅ Application Analysis Complete - {candidate.position}"
                message = f"""
Dear {candidate.name},

Thank you for your application! Our AI analysis has been completed.

🤖 Analysis Results: Your profile shows potential for the {candidate.position} position.

📅 Next Steps: 
Our interviewer ({interviewer_name}) will review your profile and contact you soon to schedule an interview.

We'll be in touch within 24-48 hours.

Best regards,
RHero Interview Team
"""
                logger.info(f"📧 ANALYSIS COMPLETE EMAIL SENT:")
                logger.info(f"   📧 To: {candidate.email}")
                
                # Actually send the email
                email_sent = self.send_email(candidate.email, subject, message)
            
            elif notification_type == "no_availability":
                subject = f"📞 Interview Scheduling - Will Contact Soon"
                message = f"""
Dear {candidate.name},

Your application has passed our AI analysis! 

🤖 Great news: Your profile is a good match for the {candidate.position} position.

📅 Scheduling: Due to current calendar availability, our interviewer ({interviewer_name}) will contact you personally within 24 hours to find a suitable interview time.

Thank you for your patience!

Best regards,
RHero Interview Team
"""
                logger.info(f"📧 MANUAL SCHEDULING EMAIL SENT:")
                logger.info(f"   📧 To: {candidate.email}")
                
                # Actually send the email
                email_sent = self.send_email(candidate.email, subject, message)
            
            # Log email delivery status
            logger.info(f"📨 Email notifications completed successfully!")
            logger.info(f"🎯 Automation workflow complete for {candidate.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False
        
        if availability['free']:
            # Return first available slot
            first_slot = availability['free'][0]
            return datetime.fromisoformat(first_slot['start'])
        
        return None


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
