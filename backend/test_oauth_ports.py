"""
Google OAuth Port Testing Script
Tests which ports work for OAuth redirect_uri configuration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import GoogleCalendarService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_oauth_authentication():
    """Test Google OAuth authentication with different ports"""
    
    print("🔐 GOOGLE OAUTH PORT TESTING")
    print("=" * 50)
    print()
    
    print("📝 GOOGLE CLOUD CONSOLE SETUP INSTRUCTIONS:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Select your project (or create one)")
    print("3. Navigate to 'APIs & Services' > 'Credentials'")
    print("4. Click on your OAuth 2.0 Client ID")
    print("5. In 'Authorized redirect URIs', add these URLs:")
    print("   • http://localhost:8080/")
    print("   • http://localhost:8000/")
    print("   • http://localhost:3000/")
    print("   • http://localhost:9000/")
    print("   • http://localhost:8888/")
    print("6. Click 'Save'")
    print()
    print("⚠️  IMPORTANT: Wait 5-10 minutes after saving for changes to propagate!")
    print()
    
    # Test authentication
    calendar_service = GoogleCalendarService()
    test_email = "rizwanpatelmalipatel@gmail.com"
    
    print(f"🧪 Testing OAuth authentication for: {test_email}")
    print("📝 This will open your browser for authentication...")
    print()
    
    try:
        result = calendar_service.authenticate(test_email)
        
        if result:
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print(f"🎉 OAuth flow completed successfully!")
            print()
            print("📋 NEXT STEPS:")
            print("1. Your token.json has been updated")
            print("2. You can now test the full automation workflow")
            print("3. Try creating a candidate to test scheduling")
            
            return True
        else:
            print("❌ AUTHENTICATION FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ AUTHENTICATION ERROR: {e}")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("1. Check if you added all redirect URIs to Google Cloud Console")
        print("2. Wait 5-10 minutes after making changes in Google Cloud Console")
        print("3. Make sure your credentials.json file is valid")
        print("4. Try disabling antivirus/firewall temporarily")
        
        return False

if __name__ == "__main__":
    success = test_oauth_authentication()
    
    if success:
        print("\n🚀 Ready to test the automation workflow!")
        print("Run: python test_automation_workflow.py")
    else:
        print("\n🔧 Please fix OAuth issues first before proceeding")
