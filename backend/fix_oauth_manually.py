#!/usr/bin/env python3
"""
FIXED GOOGLE CALENDAR OAUTH
===========================
Fix the redirect_uri_mismatch error
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def fix_oauth_flow():
    """Run OAuth with correct redirect URI"""
    
    print("🔧 FIXING GOOGLE CALENDAR OAUTH")
    print("=" * 50)
    
    # Update your Google Cloud Console first
    print("📋 GOOGLE CLOUD CONSOLE SETUP:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click on your OAuth 2.0 Client ID")
    print("3. Add these EXACT redirect URIs:")
    print("   http://localhost:8080/")
    print("   http://localhost:8080")
    print("   urn:ietf:wg:oauth:2.0:oob")
    print("4. Save changes")
    print("5. Wait 2-3 minutes for changes to propagate")
    print()
    
    # Load environment variables
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
    
    client_id = env_vars.get('GOOGLE_CLIENT_ID')
    client_secret = env_vars.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Google credentials in .env")
        return False
    
    print(f"✅ Using Client ID: {client_id[:30]}...")
    
    # Create credentials.json with correct redirect URI from your Google Cloud Console
    credentials_data = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost:8080/", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    print("\n🔧 Creating credentials.json with correct format...")
    try:
        with open('credentials.json', 'w') as f:
            json.dump(credentials_data, f, indent=2)
        print("✅ credentials.json updated")
    except Exception as e:
        print(f"❌ Failed to create credentials.json: {e}")
        return False
    
    # Run OAuth flow
    print("\n🔐 Starting OAuth flow...")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        
        # Use the standard redirect URI for desktop applications
        # This will use http://localhost:8080/ which is standard for desktop apps
        
        print("🌐 Opening browser for authentication...")
        print("📋 If browser doesn't open, copy the URL that appears")
        
        creds = flow.run_local_server(
            port=8080,
            authorization_prompt_message='Please visit this URL to authorize the application: {url}',
            success_message='The auth flow is complete; you may close this window.',
            open_browser=True
        )
        
        print("✅ OAuth authentication successful!")
        
        # Save the credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("✅ token.json created successfully")
        
        # Test the API
        print("\n🧪 Testing Google Calendar API...")
        from googleapiclient.discovery import build
        
        service = build('calendar', 'v3', credentials=creds)
        calendars = service.calendarList().list().execute()
        
        print(f"✅ Calendar API working! Found {len(calendars.get('items', []))} calendars")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth failed: {e}")
        print("\n🔧 MANUAL FIX:")
        print("1. Update Google Cloud Console redirect URIs:")
        print("   - http://localhost:8080/")
        print("   - http://localhost:8080")
        print("   - urn:ietf:wg:oauth:2.0:oob")
        print("2. Wait 2-3 minutes")
        print("3. Run this script again")
        return False

def manual_oauth_instructions():
    """Show manual OAuth setup instructions"""
    print("\n📋 MANUAL OAUTH SETUP (IF AUTOMATIC FAILS):")
    print("=" * 50)
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click 'CREATE CREDENTIALS' → 'OAuth client ID'")
    print("3. Choose 'Desktop application'")
    print("4. Name it 'RHero Calendar'")
    print("5. Download the JSON file")
    print("6. Rename it to 'credentials.json'")
    print("7. Place it in this backend folder")
    print("8. Run this script again")

if __name__ == "__main__":
    print("🎯 GOOGLE CALENDAR OAUTH FIX")
    print("=" * 60)
    
    success = fix_oauth_flow()
    
    if success:
        print("\n🎉 GOOGLE CALENDAR INTEGRATION COMPLETE!")
        print("✅ OAuth authentication successful")
        print("✅ token.json created")
        print("✅ Calendar API tested and working")
        print("\n🚀 Your automation now has full calendar integration!")
    else:
        print("\n❌ OAuth setup failed")
        manual_oauth_instructions()
        print("\n💡 TIP: Desktop application type usually works better than web application")
    
    print(f"\n📧 NEXT: Test email with: python test_email_new_password.py")
    print(f"🤖 THEN: Run full automation test")
