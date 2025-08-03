"""
OAuth2 Flow Example and Demo Script
Demonstrates the complete OAuth2 authentication flow for Google Calendar API
"""
import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demonstrate_oauth2_flow():
    """
    Complete demonstration of OAuth2 flow with Google Calendar
    """
    print("🚀 Google Calendar OAuth2 Flow Demonstration")
    print("=" * 60)
    
    try:
        # Import our enhanced calendar service
        from google_calendar_service import GoogleCalendarService
        from oauth2_config import OAuth2Config
        
        # Initialize configuration
        config = OAuth2Config()
        print(f"📋 Configuration loaded:")
        print(f"   Credentials file: {config.get_credentials_file()}")
        print(f"   Token directory: {config.get_token_directory()}")
        print(f"   Scopes: {len(config.get_scopes())} configured")
        print()
        
        # Validate environment
        valid_creds, creds_message = config.validate_credentials_file()
        if not valid_creds:
            print(f"❌ Credentials validation failed: {creds_message}")
            print("Please follow the setup guide to create credentials.json")
            return False
        
        print("✅ Credentials file is valid")
        
        # Get user email for demo
        user_email = input("Enter your Gmail address for testing: ").strip()
        if not user_email:
            print("❌ Email address is required")
            return False
        
        print(f"\n🔐 Starting OAuth2 flow for: {user_email}")
        
        # Initialize calendar service
        calendar_service = GoogleCalendarService()
        
        # Test authentication
        print("📱 Opening browser for authentication...")
        print("   Please complete the OAuth consent in your browser")
        
        auth_success = calendar_service.authenticate(user_email)
        
        if auth_success:
            print("✅ Authentication successful!")
            
            # Get user information
            user_info = calendar_service.get_user_info()
            print(f"\n👤 User Information:")
            print(f"   Email: {user_info['email']}")
            print(f"   Calendar: {user_info['calendar_summary']}")
            print(f"   Timezone: {user_info['timezone']}")
            print(f"   Authenticated at: {user_info['authenticated_at']}")
            
            # Test availability check
            print(f"\n📅 Testing availability check...")
            start_date = datetime.now()
            end_date = start_date + timedelta(days=1)
            
            availability = calendar_service.get_availability(
                user_email, start_date, end_date
            )
            
            print(f"   Checked: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Busy periods found: {len(availability['busy'])}")
            
            if availability['busy']:
                print("   Busy times:")
                for busy_time in availability['busy'][:3]:  # Show first 3
                    start = busy_time['start']
                    end = busy_time['end']
                    print(f"     • {start} to {end}")
                if len(availability['busy']) > 3:
                    print(f"     ... and {len(availability['busy']) - 3} more")
            
            # Test event creation (optional)
            create_test_event = input("\n🎯 Create a test calendar event? (y/n): ").lower().strip()
            
            if create_test_event == 'y':
                test_event_data = {
                    'id': 'test_123',
                    'scheduled_time': datetime.now() + timedelta(hours=2),
                    'duration': 30,
                    'type': 'technical',
                    'candidate_name': 'Test Candidate',
                    'interviewer_name': user_info['email'].split('@')[0],
                    'notes': 'This is a test event created by the OAuth2 demo'
                }
                
                print(f"📝 Creating test event...")
                event_id = calendar_service.create_interview_event(
                    interview_data=test_event_data,
                    candidate_email="test.candidate@example.com",
                    interviewer_email=user_email
                )
                
                if event_id:
                    print(f"✅ Test event created successfully!")
                    print(f"   Event ID: {event_id}")
                    print(f"   Check your Google Calendar for the event")
                else:
                    print("❌ Failed to create test event")
            
            # Show token information
            print(f"\n🔑 Token Information:")
            from oauth2_setup import OAuth2SetupManager
            
            setup_manager = OAuth2SetupManager()
            tokens = setup_manager.list_stored_tokens()
            
            user_token = next((t for t in tokens if t['user_email'] == user_email), None)
            if user_token:
                print(f"   Token file: {user_token['file']}")
                print(f"   Created: {user_token['created_at']}")
                print(f"   Valid: {'✅' if user_token['valid'] else '❌'}")
                if user_token['expires_in']:
                    print(f"   Expires in: {user_token['expires_in']}")
                print(f"   Scopes: {len(user_token['scopes'])}")
            
            return True
            
        else:
            print("❌ Authentication failed!")
            print("Check the logs for more details")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required packages are installed:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Error in OAuth2 demonstration")
        return False


def demonstrate_token_management():
    """
    Demonstrate token management features
    """
    print("\n🔧 Token Management Demonstration")
    print("=" * 40)
    
    try:
        from oauth2_setup import OAuth2SetupManager
        
        manager = OAuth2SetupManager()
        
        # List stored tokens
        print("📋 Stored Tokens:")
        tokens = manager.list_stored_tokens()
        
        if tokens:
            for token in tokens:
                status = "✅ Valid" if token['valid'] else "❌ Invalid"
                print(f"   {status} - {token['user_email']}")
                print(f"     File: {token['file']}")
                print(f"     Created: {token['created_at']}")
                if token['expires_in']:
                    print(f"     Expires in: {token['expires_in']}")
                if 'issues' in token and token['issues']:
                    for issue in token['issues']:
                        print(f"     Issue: {issue}")
                print()
        else:
            print("   No stored tokens found")
        
        # Clean up expired tokens
        print("🧹 Cleaning up expired tokens...")
        removed_count = manager.cleanup_expired_tokens()
        print(f"   Removed {removed_count} expired tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in token management demo: {e}")
        return False


def demonstrate_integration_example():
    """
    Show how to integrate OAuth2 with the interview scheduling system
    """
    print("\n🔗 Integration Example")
    print("=" * 30)
    
    example_code = '''
# Example: Integrating OAuth2 with Interview Scheduling

from google_calendar_service import GoogleCalendarService
from models import Interview, User, Candidate
from datetime import datetime, timedelta

async def schedule_interview_with_calendar(
    interview_data: dict,
    db_session
) -> dict:
    """
    Schedule interview with Google Calendar integration
    """
    # Initialize calendar service
    calendar_service = GoogleCalendarService()
    
    # Get interviewer details
    interviewer = db_session.query(User).filter(
        User.id == interview_data['interviewer_id']
    ).first()
    
    if not interviewer:
        raise ValueError("Interviewer not found")
    
    # Ensure interviewer is authenticated with Google Calendar
    if not calendar_service.is_authenticated(interviewer.email):
        # In a web app, redirect to OAuth flow
        auth_url = create_auth_url(interviewer.email)
        return {
            "status": "auth_required",
            "auth_url": auth_url,
            "message": "Interviewer needs to authenticate with Google Calendar"
        }
    
    # Check interviewer availability
    start_time = interview_data['scheduled_time']
    end_time = start_time + timedelta(minutes=interview_data['duration'])
    
    availability = calendar_service.get_availability(
        interviewer.email, start_time, end_time
    )
    
    if availability['busy']:
        return {
            "status": "conflict",
            "message": "Interviewer is not available at requested time",
            "busy_periods": availability['busy']
        }
    
    # Get candidate details
    candidate = db_session.query(Candidate).filter(
        Candidate.id == interview_data['candidate_id']
    ).first()
    
    # Create calendar event
    event_id = calendar_service.create_interview_event(
        interview_data=interview_data,
        candidate_email=candidate.email,
        interviewer_email=interviewer.email
    )
    
    if event_id:
        # Save to database
        interview = Interview(
            candidate_id=interview_data['candidate_id'],
            interviewer_id=interview_data['interviewer_id'],
            scheduled_time=interview_data['scheduled_time'],
            duration=interview_data['duration'],
            type=interview_data['type'],
            google_event_id=event_id,
            status='scheduled'
        )
        
        db_session.add(interview)
        db_session.commit()
        
        return {
            "status": "success",
            "interview_id": interview.id,
            "google_event_id": event_id,
            "message": "Interview scheduled successfully"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to create calendar event"
        }

# FastAPI endpoint example
@app.post("/api/interviews/schedule")
async def schedule_interview_endpoint(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db)
):
    """Schedule interview with calendar integration"""
    result = await schedule_interview_with_calendar(
        interview_data.dict(), db
    )
    
    if result["status"] == "auth_required":
        return {
            "message": result["message"],
            "auth_url": result["auth_url"],
            "action_required": "oauth_authentication"
        }
    elif result["status"] == "conflict":
        raise HTTPException(409, result["message"])
    elif result["status"] == "success":
        return result
    else:
        raise HTTPException(500, result["message"])
'''
    
    print("📝 Here's how to integrate OAuth2 with your interview scheduling:")
    print(example_code)
    
    return True


async def run_async_demo():
    """Run async demonstration features"""
    print("\n⚡ Async Integration Demo")
    print("=" * 30)
    
    try:
        from google_calendar_service import GoogleCalendarService
        
        calendar_service = GoogleCalendarService()
        
        # Simulate async scheduling
        print("🔄 Simulating async interview scheduling...")
        
        # This would normally be called from FastAPI endpoints
        async def simulate_scheduling():
            await asyncio.sleep(1)  # Simulate async work
            return {
                "status": "scheduled",
                "message": "Interview scheduled successfully (simulated)"
            }
        
        result = await simulate_scheduling()
        print(f"✅ {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Async demo error: {e}")
        return False


def main():
    """Main demonstration script"""
    print("🎯 Google Calendar OAuth2 Complete Demonstration")
    print("=" * 60)
    print("This script demonstrates:")
    print("1. OAuth2 authentication flow")
    print("2. Token management")
    print("3. Calendar API integration")
    print("4. Integration examples")
    print("=" * 60)
    
    # Check if this is a non-interactive environment
    if not sys.stdin.isatty():
        print("⚠️  Running in non-interactive mode")
        print("Skipping user input demonstrations")
        return
    
    try:
        # Step 1: OAuth2 Flow
        print("\n🔹 Step 1: OAuth2 Authentication Flow")
        oauth_success = demonstrate_oauth2_flow()
        
        if oauth_success:
            # Step 2: Token Management
            print("\n🔹 Step 2: Token Management")
            demonstrate_token_management()
            
            # Step 3: Integration Example
            print("\n🔹 Step 3: Integration Examples")
            demonstrate_integration_example()
            
            # Step 4: Async Demo
            print("\n🔹 Step 4: Async Integration")
            asyncio.run(run_async_demo())
            
            print("\n🎉 Demonstration completed successfully!")
            print("\n📚 Next Steps:")
            print("1. Review the setup guide: google-calendar-oauth2-setup.md")
            print("2. Configure your Google Cloud Console")
            print("3. Set up credentials.json")
            print("4. Integrate with your FastAPI application")
            print("5. Test with real users")
            
        else:
            print("\n❌ OAuth2 demonstration failed")
            print("Please check the setup guide and try again")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstration cancelled by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        logger.exception("Error in main demonstration")


if __name__ == "__main__":
    main()
