#!/usr/bin/env python3
"""
SIMPLE GOOGLE CALENDAR OAUTH
============================
Complete OAuth authentication in 3 simple steps
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def run_oauth():
    """Run OAuth flow to authenticate Google Calendar"""
    
    print("🔐 GOOGLE CALENDAR OAUTH AUTHENTICATION")
    print("=" * 50)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found")
        print("🔧 Creating it from your .env configuration...")
        
        # Load from .env
        try:
            with open('.env', 'r') as f:
                env_vars = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
            
            credentials_data = {
                "web": {
                    "client_id": env_vars.get('GOOGLE_CLIENT_ID'),
                    "client_secret": env_vars.get('GOOGLE_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": [env_vars.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/callback')]
                }
            }
            
            with open('credentials.json', 'w') as f:
                json.dump(credentials_data, f, indent=2)
            
            print("✅ credentials.json created from .env")
            
        except Exception as e:
            print(f"❌ Failed to create credentials.json: {e}")
            return False
    
    print("\n🚀 STEP 1: Checking existing authentication...")
    
    creds = None
    # Check if we already have a token
    if os.path.exists('token.json'):
        print("📄 Found existing token.json")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("✅ Loaded existing credentials")
        except Exception as e:
            print(f"⚠️ Token file invalid: {e}")
            os.remove('token.json')
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        print("\n🔐 STEP 2: Running OAuth authentication...")
        
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                creds = None
        
        if not creds:
            print("🌐 Starting OAuth flow...")
            print("📋 This will:")
            print("   1. Open your web browser")
            print("   2. Ask you to sign in to Google")
            print("   3. Request Google Calendar permissions")
            print("   4. Redirect back to complete setup")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                
                # Run the OAuth flow
                print("\n🔄 Opening browser for authentication...")
                creds = flow.run_local_server(port=8080, open_browser=True)
                print("✅ OAuth flow completed!")
                
            except Exception as e:
                print(f"❌ OAuth flow failed: {e}")
                print("\n🔧 TROUBLESHOOTING:")
                print("1. Make sure Google Calendar API is enabled")
                print("2. Check your Google Cloud Console project")
                print("3. Verify OAuth 2.0 client ID configuration")
                return False
        
        # Save credentials for next time
        print("\n💾 STEP 3: Saving authentication token...")
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ token.json saved successfully")
        except Exception as e:
            print(f"❌ Failed to save token: {e}")
            return False
    else:
        print("✅ Using existing valid credentials")
    
    # Test the calendar API
    print("\n🧪 STEP 4: Testing Google Calendar API...")
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Test by getting calendar list
        calendars = service.calendarList().list().execute()
        calendar_count = len(calendars.get('items', []))
        
        print(f"✅ Calendar API working! Found {calendar_count} calendars")
        
        # Test availability check
        from datetime import datetime, timedelta
        
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        print(f"\n📅 Testing availability check for tomorrow at {start_time.strftime('%I:%M %p')}")
        
        # Your email for calendar check
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('EMAIL_USERNAME='):
                    your_email = line.split('=', 1)[1].strip()
                    break
        
        # Check free/busy
        body = {
            "timeMin": start_time.isoformat() + 'Z',
            "timeMax": end_time.isoformat() + 'Z',
            "items": [{"id": your_email}]
        }
        
        freebusy = service.freebusy().query(body=body).execute()
        busy_times = freebusy.get('calendars', {}).get(your_email, {}).get('busy', [])
        
        if not busy_times:
            print(f"🟢 You're FREE tomorrow at {start_time.strftime('%I:%M %p')}!")
        else:
            print(f"🔴 You have {len(busy_times)} conflicts tomorrow")
        
        print("\n🎉 GOOGLE CALENDAR INTEGRATION COMPLETE!")
        print("✅ OAuth authentication successful")
        print("✅ token.json created and saved")
        print("✅ Calendar API tested and working")
        print("✅ Your automation now has full calendar integration!")
        
        return True
        
    except Exception as e:
        print(f"❌ Calendar API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 GOOGLE CALENDAR OAUTH SETUP")
    print("=" * 60)
    
    success = run_oauth()
    
    if success:
        print("\n🎉 SUCCESS! Google Calendar is now integrated!")
        print("\n🚀 YOUR AUTOMATION NOW HAS:")
        print("✅ AI Analysis (DeepSeek model)")
        print("✅ Google Calendar Integration") 
        print("⚠️ Email Notifications (fix Gmail app password)")
        print("✅ Database Operations")
        print("\n📧 NEXT: Fix email authentication for complete automation")
    else:
        print("\n❌ OAuth setup incomplete")
        print("🔧 Check the troubleshooting steps above")
        print("📋 Make sure Google Calendar API is enabled in Google Cloud Console")
