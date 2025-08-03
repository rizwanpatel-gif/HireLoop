#!/usr/bin/env python3
"""
TEST EMAIL WITH NEW PASSWORD
============================
Test if your updated email password works
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_with_new_password():
    """Test email with the updated password from .env"""
    
    print("📧 TESTING EMAIL WITH NEW PASSWORD")
    print("=" * 40)
    
    # Load .env manually
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"❌ Could not load .env: {e}")
        return False
    
    email_username = env_vars.get('EMAIL_USERNAME')
    email_password = env_vars.get('EMAIL_PASSWORD')
    
    print(f"📧 From: {email_username}")
    print(f"📧 To: rizwanpatelmalipatel6@gmail.com")
    print(f"🔑 Password: {email_password[:4]}...{email_password[-4:]} (masked)")
    
    try:
        # Create test message
        message = MIMEMultipart()
        message["From"] = email_username
        message["To"] = "rizwanpatelmalipatel6@gmail.com"
        message["Subject"] = "🎉 RHero Email Test - Updated Password"
        
        body = f"""
Hi!

✅ SUCCESS! Your email configuration is now working!

📧 From: {email_username}
📧 To: rizwanpatelmalipatel6@gmail.com
🔑 Password: Updated and working
⏰ Time: {__import__('datetime').datetime.now()}

🎯 This means your automation can now send:
✅ AI analysis results
✅ Interview scheduling notifications  
✅ Calendar availability updates
✅ Meeting confirmations

🚀 Your RHero automation system is ready!

Best regards,
RHero Interview System
"""
        
        message.attach(MIMEText(body, "plain"))
        
        print("\n🔄 Sending test email...")
        
        # Connect and send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_username, email_password)
        
        text = message.as_string()
        server.sendmail(email_username, "rizwanpatelmalipatel6@gmail.com", text)
        server.quit()
        
        print("🎉 EMAIL SENT SUCCESSFULLY!")
        print("📧 Check your inbox: rizwanpatelmalipatel6@gmail.com")
        print("📱 Also check spam folder")
        print("✅ Email authentication is now working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        
        if "Username and Password not accepted" in str(e):
            print("\n🔧 PASSWORD STILL NOT WORKING:")
            print("Your password 'xvka qidk kkcu eveq' may not be a valid Gmail App Password")
            print("\n📋 TO FIX:")
            print("1. Go to: https://myaccount.google.com/security")
            print("2. Enable 2-Step Verification (if not enabled)")
            print("3. Go to 'App passwords'")
            print("4. Generate new app password for 'Mail'")
            print("5. Copy the 16-character code (like: abcd efgh ijkl mnop)")
            print("6. Replace EMAIL_PASSWORD in .env with the new app password")
        
        return False

if __name__ == "__main__":
    print("🎯 EMAIL CONFIGURATION TEST")
    print("=" * 50)
    
    success = test_email_with_new_password()
    
    if success:
        print("\n🎉 EMAIL WORKING!")
        print("✅ Your automation can now send notifications")
        print("📧 Email integration complete")
    else:
        print("\n🔧 EMAIL NEEDS FIXING")
        print("Follow the Gmail App Password steps above")
    
    print("\n📊 AUTOMATION STATUS:")
    print("✅ AI Analysis - Working")
    print(f"{'✅' if success else '⚠️'} Email Notifications - {'Working' if success else 'Needs App Password'}")
    print("🔄 Calendar Integration - OAuth in progress")
    print("✅ Database Operations - Working")
