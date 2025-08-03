#!/usr/bin/env python3
"""
SIMPLE GOOGLE CALENDAR TEST
===========================
"""

import os
import sys
sys.path.append('.')

print("📅 GOOGLE CALENDAR INTEGRATION TEST")
print("=" * 50)

# Check environment variables first
print("🔧 CHECKING CONFIGURATION:")
print(f"GOOGLE_CLIENT_ID: {'✅ Set' if os.getenv('GOOGLE_CLIENT_ID') else '❌ Missing'}")
print(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if os.getenv('GOOGLE_CLIENT_SECRET') else '❌ Missing'}")
print(f"GOOGLE_REDIRECT_URI: {'✅ Set' if os.getenv('GOOGLE_REDIRECT_URI') else '❌ Missing'}")

# Check for credentials files
print("\n📁 CHECKING CREDENTIAL FILES:")
files_to_check = ['credentials.json', 'token.json', 'client_secret.json']
for file in files_to_check:
    if os.path.exists(file):
        print(f"✅ Found: {file}")
    else:
        print(f"❌ Missing: {file}")

print("\n🔍 TESTING CALENDAR SERVICE IMPORT:")
try:
    from app.services.calendar_service import GoogleCalendarService
    print("✅ Calendar service imported successfully")
    
    print("\n🚀 INITIALIZING CALENDAR SERVICE:")
    calendar_service = GoogleCalendarService()
    print("✅ Calendar service created")
    
    print("\n📧 TESTING WITH YOUR EMAIL:")
    from datetime import datetime, timedelta
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    your_email = os.getenv('EMAIL_USERNAME', 'rizwanpatelmalipatel@gmail.com')
    print(f"Email: {your_email}")
    
    # Test tomorrow at 2 PM for 1 hour
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    print(f"\n⏰ CHECKING AVAILABILITY:")
    print(f"Date: {start_time.strftime('%A, %B %d, %Y')}")
    print(f"Time: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
    
    # Test calendar availability
    availability = calendar_service.get_availability(your_email, start_time, end_time)
    
    if 'error' in availability:
        print(f"\n❌ CALENDAR ERROR: {availability['error']}")
        
        if "not authenticated" in availability['error'].lower():
            print("\n🔧 AUTHENTICATION NEEDED:")
            print("📋 QUICK SETUP STEPS:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Create new project (or select existing)")
            print("3. Enable Google Calendar API")
            print("4. Create OAuth 2.0 credentials")
            print("5. Download credentials.json to this folder")
            print("6. Run authentication flow")
            
            print("\n📁 OR: Create credentials.json manually:")
            print("Put this in credentials.json:")
            print('''{
  "web": {
    "client_id": "your-client-id-here",
    "client_secret": "your-client-secret-here",
    "redirect_uris": ["http://localhost:8000/auth/callback"]
  }
}''')
    else:
        busy_times = availability.get('busy', [])
        
        if not busy_times:
            print(f"\n🟢 YOU ARE FREE!")
            print(f"✅ Available: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
            print(f"📅 Date: {start_time.strftime('%A, %B %d, %Y')}")
        else:
            print(f"\n🔴 YOU ARE BUSY ({len(busy_times)} conflicts)")
            for i, busy in enumerate(busy_times, 1):
                print(f"   Conflict {i}: {busy.get('start', 'Unknown')} - {busy.get('end', 'Unknown')}")
    
    print(f"\n📊 CALENDAR SERVICE STATUS:")
    print(f"✅ Import: Working")
    print(f"✅ Initialize: Working") 
    print(f"{'✅' if 'error' not in availability else '❌'} API Call: {'Working' if 'error' not in availability else 'Needs Authentication'}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\n🔧 POSSIBLE FIXES:")
    print("1. Make sure app/services/calendar_service.py exists")
    print("2. Check if Google API libraries are installed")
    print("3. Verify the calendar service implementation")

except Exception as e:
    print(f"❌ Test failed: {e}")
    print("\n🔧 Check calendar service configuration")

print(f"\n🎯 SUMMARY:")
print("📅 This test checks if Google Calendar API is working")
print("📧 Email automation works independently of calendar")
print("🚀 Your automation system will work with or without calendar")
print("🔧 Calendar integration is optional but recommended")
