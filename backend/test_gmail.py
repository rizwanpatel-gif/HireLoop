"""
Simple Gmail Test
Tests the HTML email functionality independently
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automation_service import InterviewAutomationService

def test_gmail_functionality():
    """Test Gmail HTML email sending"""
    
    print("📧 TESTING GMAIL HTML EMAIL FUNCTIONALITY")
    print("=" * 50)
    
    # Initialize automation service
    automation = InterviewAutomationService()
    
    # Test HTML email
    test_email = "rizwanpatelmalipatel@gmail.com"  # Your email to test
    subject = "🧪 Test: Enhanced RHero Email System"
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .meeting-link { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Enhanced Email System Working!</h1>
            <p>RHero Automation Test</p>
        </div>
        <div class="content">
            <div class="success">
                <strong>✅ SUCCESS:</strong> Your enhanced automation system is working perfectly!
            </div>
            
            <h3>🚀 New Features Active:</h3>
            <ul>
                <li>✅ Qwen AI Model (better rate limits)</li>
                <li>✅ Beautiful HTML Gmail notifications</li>
                <li>✅ Google Calendar integration with Meet links</li>
                <li>✅ Fixed database enum issues</li>
                <li>✅ Instant email delivery</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="https://meet.google.com/sample-link" class="meeting-link">
                    🎥 Sample Meeting Link
                </a>
            </div>
            
            <p><strong>📧 Email Test:</strong> If you're reading this beautiful HTML email, your Gmail integration is working perfectly!</p>
            
            <p><em>This test email confirms that candidates and interviewers will receive professional, well-formatted notifications with meeting links.</em></p>
            
            <hr>
            <p style="text-align: center; color: #666;">
                <strong>RHero Interview System</strong><br>
                🤖 AI-Powered Recruitment Platform
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    print(f"📧 Sending test HTML email to: {test_email}")
    print("📋 Email content: Professional HTML format with styling")
    print()
    
    # Send test email
    success = automation.send_email(test_email, subject, html_content, is_html=True)
    
    if success:
        print("✅ HTML EMAIL SENT SUCCESSFULLY!")
        print()
        print("🎉 VERIFICATION:")
        print(f"1. Check your Gmail inbox: {test_email}")
        print("2. You should see a beautifully formatted HTML email")
        print("3. The email should have:")
        print("   • Gradient header background")
        print("   • Styled content areas")
        print("   • Green meeting link button")
        print("   • Professional formatting")
        print()
        print("✅ Your Gmail integration is working perfectly!")
        print("✅ Candidates will receive beautiful HTML emails!")
        print("✅ Meeting links will be prominently displayed!")
        
        return True
    else:
        print("❌ EMAIL SENDING FAILED!")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("1. Check your .env file EMAIL_USERNAME and EMAIL_PASSWORD")
        print("2. Ensure Gmail app password is correct")
        print("3. Check internet connection")
        print("4. Verify Gmail SMTP settings")
        
        return False

if __name__ == "__main__":
    test_gmail_functionality()
