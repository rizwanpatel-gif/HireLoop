#!/usr/bin/env python3
"""
AUTOMATION TEST WITHOUT CALENDAR
================================
Test automation workflow with email notifications
(Skip calendar integration for now)
"""

import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def test_simple_email():
    """Test email with current settings"""
    load_dotenv()
    
    print("📧 TESTING EMAIL WITH CURRENT SETTINGS")
    print("=" * 40)
    
    email_username = os.getenv('EMAIL_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"📧 From: {email_username}")
    print(f"📧 To: rizwanpatelmalipatel6@gmail.com")
    print(f"🔑 Password: {email_password[:4]}...{email_password[-4:]} (masked)")
    
    # Try to send a simple test email
    try:
        message = MIMEMultipart()
        message["From"] = email_username
        message["To"] = "rizwanpatelmalipatel6@gmail.com"
        message["Subject"] = "🎯 RHero Test - Simple Email"
        
        body = f"""
Hi!

This is a test email from RHero automation system.

✅ If you receive this, email is working!
📧 From: {email_username}
📧 To: rizwanpatelmalipatel6@gmail.com

Time: {__import__('datetime').datetime.now()}

Best regards,
RHero System
"""
        
        message.attach(MIMEText(body, "plain"))
        
        print("🔄 Attempting to send email...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_username, email_password)
        
        text = message.as_string()
        server.sendmail(email_username, "rizwanpatelmalipatel6@gmail.com", text)
        server.quit()
        
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("📧 Check: rizwanpatelmalipatel6@gmail.com")
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        
        if "Username and Password not accepted" in str(e):
            print("\n🔧 FIX NEEDED:")
            print("1. Go to: https://myaccount.google.com/security")
            print("2. Enable 2-Step Verification")
            print("3. Generate App Password for Mail")
            print("4. Replace EMAIL_PASSWORD in .env with app password")
            print("5. App password format: abcd efgh ijkl mnop")
        
        return False

def test_automation_without_calendar():
    """Test automation workflow without calendar"""
    print("\n📋 TESTING AUTOMATION WITHOUT CALENDAR")
    print("=" * 40)
    
    candidate = {
        "name": "No Calendar Test",
        "email": "rizwanpatelmalipatel6@gmail.com",
        "position": "Test Developer",
        "skills": "Python, JavaScript",
        "experience_years": 2,
        "education": "Computer Science",
        "current_title": "Developer",
        "resume_text": "Test developer for email automation",
        "resume_summary": "Testing automation without calendar"
        # No interview_datetime - should trigger analysis-only
    }
    
    try:
        print("🚀 Creating candidate (analysis-only workflow)...")
        response = requests.post(
            "http://localhost:8000/api/candidates/",
            headers={"Content-Type": "application/json"},
            json=candidate,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AUTOMATION SUCCESS!")
            print(f"   🆔 ID: {result['id']}")
            print(f"   📊 Status: {result['status']}")
            print(f"   📧 Email: {result['email']}")
            return True
        else:
            print(f"❌ Automation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 SIMPLIFIED AUTOMATION TEST")
    print("=" * 50)
    
    # Test email first
    email_works = test_simple_email()
    
    # Test automation
    automation_works = test_automation_without_calendar()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"📧 Email: {'✅ Working' if email_works else '❌ Needs App Password'}")
    print(f"🤖 Automation: {'✅ Working' if automation_works else '❌ Failed'}")
    
    if email_works and automation_works:
        print("🎉 BASIC AUTOMATION IS WORKING!")
        print("📧 Check your email for notifications")
    else:
        print("🔧 Fix email authentication first")
        print("📋 Follow the Gmail App Password guide above")
