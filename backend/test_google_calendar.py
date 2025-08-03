#!/usr/bin/env python3
"""
GOOGLE CALENDAR API TEST
========================
Test Google Calendar integration and show your availability
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the current directory to path to import our services
sys.path.append('.')

def test_google_calendar_detailed():
    """Comprehensive Google Calendar API test"""
    
    print("📅 GOOGLE CALENDAR API COMPREHENSIVE TEST")
    print("=" * 60)
    
    load_dotenv()
    
    # Show current configuration
    print("🔧 CONFIGURATION:")
    print(f"   GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID', 'Not set')[:20]}...")
    print(f"   GOOGLE_CLIENT_SECRET: {os.getenv('GOOGLE_CLIENT_SECRET', 'Not set')[:10]}...")
    print(f"   GOOGLE_REDIRECT_URI: {os.getenv('GOOGLE_REDIRECT_URI', 'Not set')}")
    print()
    
    try:
        print("📦 STEP 1: Importing Calendar Service...")
        from app.services.calendar_service import GoogleCalendarService
        print("✅ Calendar service imported successfully")
        
        print("\n🔧 STEP 2: Initializing Calendar Service...")
        calendar_service = GoogleCalendarService()
        print("✅ Calendar service initialized")
        
        print("\n📧 STEP 3: Testing with your email...")
        your_email = os.getenv('EMAIL_USERNAME', 'rizwanpatelmalipatel@gmail.com')
        print(f"   Email: {your_email}")
        
        # Test for today and next few days
        test_dates = []
        for i in range(3):  # Today + next 2 days
            test_date = datetime.now() + timedelta(days=i)
            test_dates.append(test_date)
        
        print(f"\n🗓️ STEP 4: Testing availability for {len(test_dates)} days...")
        
        for i, test_date in enumerate(test_dates):
            day_name = test_date.strftime('%A, %B %d, %Y')
            print(f"\n📅 Day {i+1}: {day_name}")
            print("-" * 40)
            
            # Test morning slot (9 AM - 10 AM)
            start_time = test_date.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = test_date.replace(hour=10, minute=0, second=0, microsecond=0)
            
            print(f"⏰ Testing slot: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
            
            try:
                availability = calendar_service.get_availability(
                    your_email,
                    start_time,
                    end_time
                )
                
                if 'error' in availability:
                    print(f"❌ Error: {availability['error']}")
                    
                    if "not authenticated" in availability['error'].lower():
                        print("🔧 AUTHENTICATION NEEDED:")
                        print("   1. Go to: https://console.cloud.google.com/")
                        print("   2. Create project & enable Calendar API")
                        print("   3. Create OAuth2 credentials")
                        print("   4. Download credentials.json")
                        print("   5. Run OAuth flow")
                        
                else:
                    busy_times = availability.get('busy', [])
                    
                    if not busy_times:
                        print(f"🟢 FREE - No conflicts found!")
                        print(f"✅ Available: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
                    else:
                        print(f"🔴 BUSY - {len(busy_times)} conflict(s):")
                        for j, busy in enumerate(busy_times, 1):
                            busy_start = busy.get('start', 'Unknown')
                            busy_end = busy.get('end', 'Unknown')
                            print(f"   Conflict {j}: {busy_start} - {busy_end}")
                            
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        # Test creating a test event
        print(f"\n🎯 STEP 5: Testing Event Creation...")
        
        try:
            # Create a test interview event for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            test_event_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
            
            interview_data = {
                'scheduled_time': test_event_time,
                'duration': 60,
                'type': 'Test Interview',
                'candidate_name': 'Test Candidate',
                'interviewer_name': 'Rizwan Patel',
                'position': 'Test Position',
                'notes': 'This is a test event for calendar integration',
                'id': 'test_candidate_999'
            }
            
            print(f"📅 Creating test event for: {test_event_time.strftime('%A, %B %d at %I:%M %p')}")
            
            event_result = calendar_service.create_interview_event(
                interview_data,
                "rizwanpatelmalipatel6@gmail.com",  # Test candidate email
                your_email  # Your email as interviewer
            )
            
            if event_result:
                print("✅ TEST EVENT CREATED SUCCESSFULLY!")
                print(f"   📎 Event ID: {event_result.get('event_id', 'N/A')}")
                print(f"   🎥 Meet Link: {event_result.get('meet_link', 'N/A')}")
                print(f"   📧 Invites sent to: rizwanpatelmalipatel6@gmail.com, {your_email}")
                print("   🗑️ You can delete this test event from your calendar")
            else:
                print("❌ Test event creation failed")
                
        except Exception as e:
            print(f"❌ Event creation test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure calendar service is properly implemented")
        return False
        
    except Exception as e:
        print(f"❌ Calendar test failed: {e}")
        return False

def test_calendar_auth_status():
    """Check calendar authentication status"""
    print("\n🔐 AUTHENTICATION STATUS CHECK")
    print("=" * 40)
    
    # Check for credentials file
    creds_files = ['credentials.json', 'token.json', 'client_secret.json']
    
    for file in creds_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
    
    # Check environment variables
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI']
    
    print("\n🌍 Environment Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set ({value[:10]}...)")
        else:
            print(f"❌ {var}: Not set")

if __name__ == "__main__":
    print("🎯 GOOGLE CALENDAR INTEGRATION TEST")
    print("=" * 60)
    
    # Check auth status first
    test_calendar_auth_status()
    
    # Run comprehensive test
    success = test_google_calendar_detailed()
    
    print("\n" + "=" * 60)
    print("📊 CALENDAR TEST RESULTS:")
    
    if success:
        print("✅ Google Calendar integration test completed")
        print("📅 Check the output above for availability results")
        print("🎥 If test event was created, check your Google Calendar")
    else:
        print("❌ Google Calendar integration needs setup")
        print("🔧 Follow the authentication steps shown above")
    
    print("\n🎯 NEXT STEPS:")
    print("1. If calendar works → Your automation will use it")
    print("2. If calendar fails → Automation will work without it")
    print("3. Fix authentication → Full calendar integration")
    print("📧 Email notifications will work independently")
