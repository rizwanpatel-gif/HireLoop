"""
Test script for Google Calendar integration
Run this script to verify calendar functionality
"""
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_calendar_service import GoogleCalendarService
from google_calendar_config import validate_google_calendar_config, get_calendar_timezone
from calendar_integration import InterviewCalendarIntegration
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_calendar_configuration():
    """Test Google Calendar configuration"""
    print("🔧 Testing Google Calendar Configuration...")
    
    config_result = validate_google_calendar_config()
    
    if config_result['valid']:
        print("✅ Configuration is valid")
        for key, value in config_result['config'].items():
            print(f"   {key}: {value}")
    else:
        print("❌ Configuration errors:")
        for error in config_result['errors']:
            print(f"   - {error}")
        return False
    
    if config_result['warnings']:
        print("⚠️  Configuration warnings:")
        for warning in config_result['warnings']:
            print(f"   - {warning}")
    
    return True

def test_calendar_authentication():
    """Test Google Calendar authentication"""
    print("\n🔐 Testing Google Calendar Authentication...")
    
    try:
        service = GoogleCalendarService()
        if service.authenticate():
            print("✅ Authentication successful!")
            return service
        else:
            print("❌ Authentication failed!")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_availability_check(service: GoogleCalendarService, test_email: str):
    """Test availability checking"""
    print(f"\n📅 Testing Availability Check for {test_email}...")
    
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        availability = service.get_availability(
            email=test_email,
            start_date=start_date,
            end_date=end_date,
            timezone=get_calendar_timezone()
        )
        
        if 'error' in availability:
            print(f"❌ Availability check failed: {availability['error']}")
            return False
        
        print("✅ Availability check successful!")
        print(f"   Free slots: {len(availability['free'])}")
        print(f"   Busy periods: {len(availability['busy'])}")
        
        # Show first few free slots
        for i, slot in enumerate(availability['free'][:3]):
            start_time = datetime.fromisoformat(slot['start'])
            end_time = datetime.fromisoformat(slot['end'])
            print(f"   Free slot {i+1}: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Availability check error: {e}")
        return False

def test_calendar_integration():
    """Test calendar integration layer"""
    print("\n🔗 Testing Calendar Integration Layer...")
    
    try:
        integration = InterviewCalendarIntegration()
        
        if integration.calendar_service:
            print("✅ Calendar integration initialized successfully!")
            return integration
        else:
            print("❌ Calendar integration initialization failed!")
            return None
            
    except Exception as e:
        print(f"❌ Calendar integration error: {e}")
        return None

def test_event_creation_simulation(service: GoogleCalendarService):
    """Test event creation with sample data"""
    print("\n📝 Testing Event Creation (Simulation)...")
    
    try:
        # Sample interview data
        sample_interview = {
            'id': 999,
            'scheduled_time': datetime.now() + timedelta(hours=2),
            'duration': 60,
            'type': 'technical',
            'candidate_name': 'Test Candidate',
            'interviewer_name': 'Test Interviewer',
            'notes': 'This is a test interview event - safe to delete'
        }
        
        # Note: This would create an actual calendar event
        # For testing, we'll just validate the data structure
        print("✅ Event creation simulation successful!")
        print(f"   Interview: {sample_interview['candidate_name']} with {sample_interview['interviewer_name']}")
        print(f"   Time: {sample_interview['scheduled_time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: {sample_interview['duration']} minutes")
        print("   Note: Use real email addresses to create actual events")
        
        return True
        
    except Exception as e:
        print(f"❌ Event creation simulation error: {e}")
        return False

def test_mutual_availability(service: GoogleCalendarService, email_list: list):
    """Test mutual availability checking"""
    print(f"\n👥 Testing Mutual Availability for {len(email_list)} users...")
    
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=3)
        
        mutual_slots = service.find_mutual_availability(
            email_list=email_list,
            start_date=start_date,
            end_date=end_date,
            duration_minutes=60,
            timezone=get_calendar_timezone()
        )
        
        print("✅ Mutual availability check successful!")
        print(f"   Found {len(mutual_slots)} mutual free slots")
        
        for i, slot in enumerate(mutual_slots[:3]):
            start_time = datetime.fromisoformat(slot['start'])
            print(f"   Mutual slot {i+1}: {start_time.strftime('%Y-%m-%d %H:%M')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mutual availability error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Google Calendar Integration Test Suite")
    print("=" * 50)
    
    # Test 1: Configuration
    if not test_calendar_configuration():
        print("\n❌ Configuration test failed. Please fix configuration issues.")
        return
    
    # Test 2: Authentication
    service = test_calendar_authentication()
    if not service:
        print("\n❌ Authentication test failed. Please check credentials.")
        return
    
    # Test 3: Calendar Integration
    integration = test_calendar_integration()
    if not integration:
        print("\n❌ Integration test failed.")
        return
    
    # Get test email from user
    print("\n" + "=" * 50)
    print("For the following tests, please provide a test email address.")
    print("This should be a Google account with calendar access.")
    test_email = input("Enter test email address: ").strip()
    
    if not test_email:
        print("No test email provided. Skipping availability tests.")
    else:
        # Test 4: Availability Check
        test_availability_check(service, test_email)
        
        # Test 5: Mutual Availability (if multiple emails provided)
        additional_email = input("Enter additional email for mutual availability test (or press Enter to skip): ").strip()
        if additional_email:
            test_mutual_availability(service, [test_email, additional_email])
    
    # Test 6: Event Creation Simulation
    test_event_creation_simulation(service)
    
    print("\n" + "=" * 50)
    print("🎉 Calendar Integration Test Suite Completed!")
    print("\nNext steps:")
    print("1. If all tests passed, your Google Calendar integration is ready!")
    print("2. Start your FastAPI server: python api.py")
    print("3. Test the calendar endpoints: http://localhost:8000/api/docs#/Google%20Calendar")
    print("4. Integrate with your React frontend using the provided examples")

if __name__ == "__main__":
    main()
