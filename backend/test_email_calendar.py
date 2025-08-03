#!/usr/bin/env python3
"""
EMAIL & CALENDAR TEST
====================
Test email sending and Google Calendar API directly
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import sys
sys.path.append('.')

def test_email_directly():
    """Test email sending directly using SMTP"""
    load_dotenv()
    
    print("📧 TESTING EMAIL DIRECTLY")
    print("=" * 40)
    
    # Get email settings from .env
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    email_username = os.getenv('EMAIL_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"📧 SMTP Server: {smtp_server}:{smtp_port}")
    print(f"📧 From: {email_username}")
    print(f"📧 To: rizwanpatelmalipatel6@gmail.com")
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = email_username
        message["To"] = "rizwanpatelmalipatel6@gmail.com"
        message["Subject"] = "🎯 RHero Email Test - Direct SMTP"
        
        body = """
Hi!

This is a direct SMTP test from your RHero automation system.

✅ Email configuration is working!
🚀 Automation system is ready
📧 FROM: rizwanpatelmalipatel@gmail.com
📧 TO: rizwanpatelmalipatel6@gmail.com

Best regards,
RHero Interview System
"""
        
        message.attach(MIMEText(body, "plain"))
        
        # Connect to server and send email
        print("🔄 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("🔐 Logging in...")
        server.login(email_username, email_password)
        
        print("📨 Sending email...")
        text = message.as_string()
        server.sendmail(email_username, "rizwanpatelmalipatel6@gmail.com", text)
        server.quit()
        
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("📧 Check your inbox: rizwanpatelmalipatel6@gmail.com")
        print("📱 Also check spam folder")
        
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def test_google_calendar():
    """Test Google Calendar API to get your free time"""
    print("\n📅 TESTING GOOGLE CALENDAR API")
    print("=" * 40)
    
    try:
        from app.services.calendar_service import GoogleCalendarService
        
        calendar_service = GoogleCalendarService()
        
        # Test getting your availability for next few days
        from datetime import datetime, timedelta
        
        # Check tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
        
        print(f"📅 Checking availability for: {start_time.strftime('%A, %B %d, %Y')}")
        print(f"⏰ Time range: 9:00 AM - 5:00 PM")
        
        # Get your email from env
        load_dotenv()
        your_email = os.getenv('EMAIL_USERNAME', 'rizwanpatelmalipatel@gmail.com')
        
        print(f"👤 Calendar: {your_email}")
        
        availability = calendar_service.get_availability(
            your_email,
            start_time,
            end_time
        )
        
        if 'error' in availability:
            print(f"❌ Calendar API Error: {availability['error']}")
            print("🔧 Check Google Calendar API credentials in .env file")
            return False
        else:
            print("✅ GOOGLE CALENDAR API WORKING!")
            
            busy_times = availability.get('busy', [])
            
            if not busy_times:
                print(f"🟢 YOU ARE FREE ALL DAY! ({start_time.strftime('%A, %B %d')})")
                print("📅 Available: 9:00 AM - 5:00 PM")
            else:
                print(f"📅 Found {len(busy_times)} busy time(s):")
                for i, busy in enumerate(busy_times, 1):
                    print(f"   🔴 Busy #{i}: {busy.get('start', 'Unknown')} - {busy.get('end', 'Unknown')}")
                
                # Find free slots
                print("\n🟢 FREE TIME SLOTS:")
                current_time = start_time
                for busy in busy_times:
                    busy_start = busy.get('start')
                    if busy_start and current_time < datetime.fromisoformat(busy_start.replace('Z', '+00:00')):
                        free_end = datetime.fromisoformat(busy_start.replace('Z', '+00:00'))
                        print(f"   ✅ Free: {current_time.strftime('%I:%M %p')} - {free_end.strftime('%I:%M %p')}")
                    
            return True
            
    except Exception as e:
        print(f"❌ Calendar test failed: {e}")
        print("🔧 Make sure Google Calendar API is properly configured")
        return False

if __name__ == "__main__":
    print("🎯 RHero EMAIL & CALENDAR TEST")
    print("=" * 50)
    
    # Test email
    email_success = test_email_directly()
    
    # Test calendar
    calendar_success = test_google_calendar()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"📧 Email: {'✅ Working' if email_success else '❌ Failed'}")
    print(f"📅 Calendar: {'✅ Working' if calendar_success else '❌ Failed'}")
    
    if email_success and calendar_success:
        print("🎉 BOTH EMAIL AND CALENDAR ARE WORKING!")
    else:
        print("🔧 Some issues found - check configuration")
