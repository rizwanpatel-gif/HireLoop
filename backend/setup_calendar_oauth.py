#!/usr/bin/env python3
"""
GOOGLE CALENDAR OAUTH SETUP
===========================
Complete the OAuth authentication for Google Calendar API
"""

import os
import sys
sys.path.append('.')

def setup_google_calendar_oauth():
    """Complete Google Calendar OAuth setup"""
    
    print("🔐 GOOGLE CALENDAR OAUTH SETUP")
    print("=" * 50)
    
    # Load environment variables manually
    def load_env():
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        except Exception as e:
            print(f"Could not load .env: {e}")
    
    load_env()
    
    # Check current credentials
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    
    print("✅ CURRENT CONFIGURATION:")
    print(f"   Client ID: {client_id[:30]}..." if client_id else "❌ Missing")
    print(f"   Client Secret: {client_secret[:15]}..." if client_secret else "❌ Missing") 
    print(f"   Redirect URI: {redirect_uri}" if redirect_uri else "❌ Missing")
    
    if not all([client_id, client_secret, redirect_uri]):
        print("❌ Missing credentials in .env file")
        return False
    
    print("\n🔧 STEP 1: Creating credentials.json file...")
    
    # Create credentials.json from .env values
    credentials_content = f'''{{
  "web": {{
    "client_id": "{client_id}",
    "client_secret": "{client_secret}",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["{redirect_uri}"]
  }}
}}'''
    
    try:
        with open('credentials.json', 'w') as f:
            f.write(credentials_content)
        print("✅ credentials.json created successfully")
    except Exception as e:
        print(f"❌ Failed to create credentials.json: {e}")
        return False
    
    print("\n🚀 STEP 2: Testing Calendar Service...")
    
    try:
        from app.services.calendar_service import GoogleCalendarService
        print("✅ Calendar service imported")
        
        calendar_service = GoogleCalendarService()
        print("✅ Calendar service initialized")
        
        print("\n🔐 STEP 3: Running OAuth Authentication...")
        print("📋 This will:")
        print("   1. Open your web browser")
        print("   2. Ask you to sign in to Google")
        print("   3. Request calendar permissions")
        print("   4. Create token.json file")
        print("   5. Enable full calendar integration")
        
        # Test authentication
        your_email = os.getenv('EMAIL_USERNAME', 'rizwanpatelmalipatel@gmail.com')
        
        print(f"\n⏰ Testing calendar access for: {your_email}")
        
        from datetime import datetime, timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        print("🔄 Attempting calendar API call...")
        print("   (This may open browser for OAuth consent)")
        
        availability = calendar_service.get_availability(your_email, start_time, end_time)
        
        if 'error' in availability:
            print(f"\n⚠️ OAuth needed: {availability['error']}")
            
            # Try to trigger OAuth flow manually
            print("\n🔧 MANUAL OAUTH STEPS:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Select your project")
            print("3. Go to APIs & Services > Credentials")
            print("4. Click on your OAuth 2.0 client ID")
            print("5. Add authorized redirect URI: http://localhost:8000/auth/callback")
            print("6. Enable Google Calendar API if not already enabled")
            
            return False
        else:
            print("🎉 OAUTH SUCCESSFUL!")
            busy_times = availability.get('busy', [])
            
            if not busy_times:
                print(f"🟢 Calendar working! You're free tomorrow at {start_time.strftime('%I:%M %p')}")
            else:
                print(f"🔴 Calendar working! You have {len(busy_times)} conflicts tomorrow")
            
            print("✅ token.json should now exist")
            print("✅ Google Calendar fully integrated")
            return True
            
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        return False

def create_oauth_helper():
    """Create a simple OAuth helper script"""
    
    oauth_script = '''#!/usr/bin/env python3
"""
GOOGLE CALENDAR OAUTH HELPER
============================
Run this to complete OAuth authentication
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate():
    """Run OAuth flow"""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found")
                print("Run the main setup script first")
                return False
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ OAuth authentication complete!")
    print("✅ token.json created")
    print("✅ Google Calendar integration ready")
    return True

if __name__ == '__main__':
    authenticate()
'''
    
    try:
        with open('oauth_helper.py', 'w') as f:
            f.write(oauth_script)
        print("✅ oauth_helper.py created")
        return True
    except Exception as e:
        print(f"❌ Failed to create oauth_helper.py: {e}")
        return False

if __name__ == "__main__":
    print("🎯 GOOGLE CALENDAR OAUTH SETUP")
    print("=" * 60)
    
    # Run OAuth setup
    success = setup_google_calendar_oauth()
    
    if not success:
        print("\n🔧 ALTERNATIVE APPROACH:")
        create_oauth_helper()
        
        print("\n📋 MANUAL STEPS:")
        print("1. Make sure Google Calendar API is enabled:")
        print("   https://console.cloud.google.com/apis/library/calendar-json.googleapis.com")
        print("2. Run: python oauth_helper.py")
        print("3. Follow browser OAuth flow")
        print("4. Grant calendar permissions")
        print("5. token.json will be created")
    
    print("\n🎯 AFTER OAUTH COMPLETION:")
    print("✅ Your automation will have full calendar integration")
    print("📅 Availability checking will work")
    print("🎥 Interview scheduling with Meet links")
    print("📧 Fix email (Gmail app password) for complete automation")
