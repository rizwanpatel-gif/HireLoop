"""
Email Service for HireLoop Interview Management System
================================================

Handles email notifications for interview scheduling and round advancements.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USERNAME")  # Updated to match .env file
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.from_name = os.getenv("FROM_NAME", "HireLoop Interview Team")
        
        if not self.email_user or not self.email_password:
            logger.warning("⚠️ Email credentials not found. Email functionality will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"📧 Email service initialized with {self.email_user}")
    
    async def send_round_advancement_email(
        self,
        candidate_email: str,
        candidate_name: str,
        round_number: int,
        round_name: str,
        interview_datetime: datetime,
        meet_link: str,
        position: str
    ) -> bool:
        """Send round advancement email to candidate"""
        
        if not self.enabled:
            logger.warning("📧 Email service disabled - no credentials")
            return False
        
        try:
            # Format interview date and time
            formatted_datetime = interview_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
            
            # Email subject
            subject = f"🎉 Congratulations! You've been selected for {round_name} Interview Round"
            
            # Email body (HTML)
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .highlight {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 HireLoop Interview System</h1>
                        <h2>Congratulations, {candidate_name}!</h2>
                    </div>
                    
                    <div class="content">
                        <p>Great news! You have been selected to advance to the <strong>{round_name} interview round</strong> for the <strong>{position}</strong> position.</p>
                        
                        <div class="highlight">
                            <h3>📅 Interview Details:</h3>
                            <p><strong>Round:</strong> {round_name} (Round {round_number})</p>
                            <p><strong>Position:</strong> {position}</p>
                            <p><strong>Date & Time:</strong> {formatted_datetime}</p>
                            <p><strong>Duration:</strong> 60 minutes</p>
                        </div>
                        
                        <h3>🎥 Join the Interview:</h3>
                        <p>Your interview will be conducted via Google Meet. Please join at the scheduled time using the link below:</p>
                        
                        <p style="text-align: center;">
                            <a href="{meet_link}" class="button">Join Google Meet Interview</a>
                        </p>
                        
                        <div class="highlight">
                            <h3>📝 What to Expect:</h3>
                            <ul>
                                <li>Please join the meeting 5 minutes early</li>
                                <li>Ensure you have a stable internet connection</li>
                                <li>Test your camera and microphone beforehand</li>
                                <li>Have your resume and portfolio ready to share</li>
                                <li>Prepare questions about the role and company</li>
                            </ul>
                        </div>
                        
                        <p>If you have any technical issues or need to reschedule, please reply to this email immediately.</p>
                        
                        <p>We're excited to learn more about you and discuss how you can contribute to our team!</p>
                        
                        <p>Best regards,<br>
                        <strong>The HireLoop Interview Team</strong></p>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from HireLoop Interview Management System</p>
                        <p>Please do not reply to this email for general inquiries</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = candidate_email
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            logger.info(f"📧 Sending round advancement email to {candidate_email}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {candidate_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {candidate_email}: {e}")
            return False
    
    async def send_interview_confirmation_email(
        self,
        candidate_email: str,
        candidate_name: str,
        interview_datetime: datetime,
        meet_link: str,
        position: str,
        interviewer_name: str = "Interview Team"
    ) -> bool:
        """Send initial interview confirmation email"""
        
        if not self.enabled:
            logger.warning("📧 Email service disabled - no credentials")
            return False
        
        try:
            formatted_datetime = interview_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
            
            subject = f"📅 Interview Scheduled - {position} Position"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1>🚀 HireLoop Interview System</h1>
                        <h2>Interview Scheduled!</h2>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p>Dear {candidate_name},</p>
                        
                        <p>Thank you for your interest in the <strong>{position}</strong> position. We're excited to meet you!</p>
                        
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3>📅 Interview Details:</h3>
                            <p><strong>Position:</strong> {position}</p>
                            <p><strong>Date & Time:</strong> {formatted_datetime}</p>
                            <p><strong>Interviewer:</strong> {interviewer_name}</p>
                            <p><strong>Duration:</strong> 60 minutes</p>
                        </div>
                        
                        <p style="text-align: center;">
                            <a href="{meet_link}" style="display: inline-block; background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Join Interview</a>
                        </p>
                        
                        <p>Best regards,<br><strong>The HireLoop Team</strong></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = candidate_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Interview confirmation email sent to {candidate_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send confirmation email to {candidate_email}: {e}")
            return False

    def build_rejection_email(self, candidate_name: str, position: str, reason: str = None) -> tuple:
        """
        Build the (subject, message) for a rejection email. Centralizes the copy so
        pre-insert AI auto-rejection, HR-initiated rejection, and reject-and-delete
        all send the exact same wording instead of three drifting copies.
        """
        subject = f"Update on Your Application - {position}"
        reason = reason or "After careful consideration of all applications, we have decided to move forward with other candidates whose profiles more closely align with our current requirements."
        message = f"""Dear {candidate_name},

Thank you for your interest in the {position} position at HireLoop.

{reason}

While your background and experience are impressive, we have chosen to proceed with candidates whose skills and experience better match the specific needs of this role.

Future Opportunities: We encourage you to:
- Continue developing your skills in the areas mentioned in the job description
- Keep us in mind for future opportunities that may be a better match
- Apply again when you feel your experience better aligns with our needs

We appreciate the time and effort you put into your application and wish you the best of luck in your career journey.

Best regards,
HireLoop Interview Team
Human Resources Department
"""
        return subject, message

    async def send_rejection_email(self, to_email: str, candidate_name: str, position: str, reason: str = None) -> bool:
        """Send the standard rejection email using the shared template."""
        subject, message = self.build_rejection_email(candidate_name, position, reason)
        return await self.send_email(to_email=to_email, subject=subject, message=message)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        is_html: bool = False
    ) -> bool:
        """
        Generic email sending method
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            message: Email content (plain text or HTML)
            is_html: Whether the message is HTML formatted
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("📧 Email service is not enabled")
            return False

        try:
            logger.info(f"📧 Sending email to {to_email}: {subject}")

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email

            # Add message content
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))

            def _send_blocking():
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                    server.send_message(msg)

            # smtplib is blocking I/O — offload it so it doesn't stall the event loop
            # (this method is awaited directly from request handlers, not always via
            # an outer run_in_threadpool call like the LangGraph-triggered emails are).
            from starlette.concurrency import run_in_threadpool
            await run_in_threadpool(_send_blocking)

            logger.info(f"✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
