"""
Google Calendar Event Creation Example
Demonstrates comprehensive calendar event creation with OAuth2 authentication,
Google Meet integration, and automatic email invitations.
"""
import os
import sys
from datetime import datetime, timedelta
import pytz
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_interview_event():
    """
    Create a sample interview calendar event with all features
    
    Returns:
        Dict with event details if successful, None otherwise
    """
    try:
        # Import Google Calendar service
        from google_calendar_service import GoogleCalendarService
        
        print("🚀 Google Calendar Event Creation Demo")
        print("=" * 50)
        
        # Initialize calendar service
        calendar_service = GoogleCalendarService()
        
        # Get interviewer email for authentication
        interviewer_email = input("Enter interviewer email address: ").strip()
        
        if not interviewer_email:
            print("❌ Email address is required")
            return None
        
        # Authenticate the user
        print(f"\n🔐 Authenticating {interviewer_email}...")
        
        if not calendar_service.is_authenticated(interviewer_email):
            print("📱 Starting OAuth2 authentication...")
            print("   Your browser will open for Google Calendar permissions")
            
            auth_success = calendar_service.authenticate(interviewer_email)
            
            if not auth_success:
                print("❌ Authentication failed")
                return None
        else:
            print("✅ Already authenticated")
        
        # Get user information
        user_info = calendar_service.get_user_info()
        if user_info:
            print(f"👤 Authenticated as: {user_info['email']}")
            print(f"📅 Default calendar: {user_info['calendar_summary']}")
        
        # Get interview details from user
        print(f"\n📝 Enter interview details:")
        
        candidate_name = input("Candidate name: ").strip() or "John Doe"
        candidate_email = input("Candidate email: ").strip() or "john.doe@example.com"
        position = input("Position: ").strip() or "Software Engineer"
        interview_type = input("Interview type (Technical/HR/Cultural): ").strip() or "Technical"
        
        # Get interview date and time
        print(f"\n🕒 Schedule interview:")
        
        try:
            date_input = input("Date (YYYY-MM-DD, or press Enter for tomorrow): ").strip()
            if not date_input:
                interview_date = datetime.now().date() + timedelta(days=1)
            else:
                interview_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            
            time_input = input("Time (HH:MM, or press Enter for 14:00): ").strip()
            if not time_input:
                interview_time = "14:00"
            else:
                interview_time = time_input
            
            # Combine date and time
            datetime_str = f"{interview_date} {interview_time}"
            interview_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            
            # Set timezone to Asia/Kolkata
            kolkata_tz = pytz.timezone('Asia/Kolkata')
            interview_datetime = kolkata_tz.localize(interview_datetime)
            
        except ValueError as e:
            print(f"❌ Invalid date/time format: {e}")
            print("Using default: Tomorrow at 2:00 PM")
            interview_datetime = datetime.now() + timedelta(days=1)
            interview_datetime = interview_datetime.replace(hour=14, minute=0, second=0, microsecond=0)
            interview_datetime = pytz.timezone('Asia/Kolkata').localize(interview_datetime)
        
        # Get duration
        try:
            duration_input = input("Duration in minutes (default: 60): ").strip()
            duration = int(duration_input) if duration_input else 60
        except ValueError:
            duration = 60
        
        # Get additional notes
        notes = input("Additional notes (optional): ").strip()
        if not notes:
            notes = f"""
Interview Preparation:
• Review candidate's resume and portfolio
• Prepare {interview_type.lower()} questions
• Test Google Meet connection before the interview
• Have job description and requirements ready

Technical Focus Areas:
• Programming skills and best practices
• Problem-solving approach
• System design capabilities
• Previous project experience
            """.strip()
        
        # Get additional attendees
        additional_attendees = []
        while True:
            attendee = input("Additional attendee email (press Enter to finish): ").strip()
            if not attendee:
                break
            additional_attendees.append(attendee)
        
        print(f"\n📋 Creating calendar event...")
        print(f"   📅 Date: {interview_datetime.strftime('%A, %B %d, %Y')}")
        print(f"   🕒 Time: {interview_datetime.strftime('%I:%M %p %Z')}")
        print(f"   ⏱️ Duration: {duration} minutes")
        print(f"   👤 Candidate: {candidate_name} ({candidate_email})")
        print(f"   👨‍💼 Interviewer: {interviewer_email}")
        print(f"   💼 Position: {position}")
        print(f"   🎯 Type: {interview_type}")
        
        if additional_attendees:
            print(f"   👥 Additional attendees: {', '.join(additional_attendees)}")
        
        # Create the event using the enhanced function
        result = calendar_service.create_calendar_event_with_details(
            title=f"{interview_type} Interview",
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            position=position,
            interviewer_name=interviewer_email.split('@')[0].title(),
            interviewer_email=interviewer_email,
            start_datetime=interview_datetime,
            duration_minutes=duration,
            interview_type=interview_type,
            notes=notes,
            additional_attendees=additional_attendees if additional_attendees else None
        )
        
        if result:
            print(f"\n✅ Calendar event created successfully!")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📋 Event Details:")
            print(f"   🆔 Event ID: {result['event_id']}")
            print(f"   📝 Title: {result['title']}")
            print(f"   📅 Start: {result['start_time']}")
            print(f"   ⏱️ Duration: {result['duration_minutes']} minutes")
            print(f"   🌍 Timezone: {result['timezone']}")
            print(f"   👥 Attendees: {result['attendees_count']}")
            
            print(f"\n🔗 Links:")
            if result['event_link']:
                print(f"   📅 Calendar Event: {result['event_link']}")
            
            if result['meet_link']:
                print(f"   🎥 Google Meet: {result['meet_link']}")
            else:
                print(f"   🎥 Google Meet: Will be available shortly")
            
            if result['meet_phone']:
                print(f"   📞 Phone: {result['meet_phone']}")
            
            if result['meet_access_code']:
                print(f"   🔑 Access Code: {result['meet_access_code']}")
            
            print(f"\n📧 Notifications:")
            print(f"   ✅ Email invitations sent to all attendees")
            print(f"   ⏰ Reminders set for:")
            print(f"      • 24 hours before (email)")
            print(f"      • 30 minutes before (popup)")
            print(f"      • 10 minutes before (email)")
            
            print(f"\n🎯 Next Steps:")
            print(f"   1. Attendees will receive email invitations")
            print(f"   2. Google Meet link will be active 15 minutes before start")
            print(f"   3. Automatic reminders will be sent")
            print(f"   4. Event can be found in Google Calendar")
            
            return result
        else:
            print(f"\n❌ Failed to create calendar event")
            print(f"   Check the logs for error details")
            return None
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"   Please ensure Google Calendar modules are installed:")
        print(f"   pip install google-api-python-client google-auth-oauthlib")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Error in calendar event creation demo")
        return None

def create_multiple_interview_events():
    """
    Create multiple interview events for demonstration
    """
    try:
        from google_calendar_service import GoogleCalendarService
        
        print("\n🔄 Multiple Interview Events Demo")
        print("=" * 40)
        
        calendar_service = GoogleCalendarService()
        
        # Sample interview data
        interviews = [
            {
                "candidate_name": "Alice Johnson",
                "candidate_email": "alice.johnson@email.com",
                "position": "Frontend Developer",
                "interview_type": "Technical",
                "duration": 75,
                "notes": "Focus on React, JavaScript, and UI/UX principles"
            },
            {
                "candidate_name": "Bob Smith",
                "candidate_email": "bob.smith@email.com",
                "position": "Backend Developer",
                "interview_type": "Technical",
                "duration": 90,
                "notes": "Focus on Python, databases, and API design"
            },
            {
                "candidate_name": "Carol Williams",
                "candidate_email": "carol.williams@email.com",
                "position": "Product Manager",
                "interview_type": "HR",
                "duration": 60,
                "notes": "Focus on leadership, product strategy, and communication"
            }
        ]
        
        interviewer_email = input("Enter interviewer email for batch creation: ").strip()
        
        if not interviewer_email:
            print("❌ Email required for batch creation")
            return
        
        # Authenticate
        if not calendar_service.is_authenticated(interviewer_email):
            print("🔐 Authentication required...")
            if not calendar_service.authenticate(interviewer_email):
                print("❌ Authentication failed")
                return
        
        created_events = []
        base_datetime = datetime.now() + timedelta(days=1)
        base_datetime = base_datetime.replace(hour=10, minute=0, second=0, microsecond=0)
        base_datetime = pytz.timezone('Asia/Kolkata').localize(base_datetime)
        
        for i, interview_data in enumerate(interviews):
            # Schedule interviews 2 hours apart
            interview_time = base_datetime + timedelta(hours=i * 2)
            
            print(f"\n📅 Creating event {i + 1}/3: {interview_data['candidate_name']}")
            
            result = calendar_service.create_calendar_event_with_details(
                title=f"{interview_data['interview_type']} Interview",
                candidate_name=interview_data['candidate_name'],
                candidate_email=interview_data['candidate_email'],
                position=interview_data['position'],
                interviewer_name=interviewer_email.split('@')[0].title(),
                interviewer_email=interviewer_email,
                start_datetime=interview_time,
                duration_minutes=interview_data['duration'],
                interview_type=interview_data['interview_type'],
                notes=interview_data['notes']
            )
            
            if result:
                created_events.append(result)
                print(f"   ✅ Created: {result['title']}")
                print(f"   🕒 Time: {interview_time.strftime('%I:%M %p')}")
                print(f"   🆔 ID: {result['event_id']}")
            else:
                print(f"   ❌ Failed to create event for {interview_data['candidate_name']}")
        
        print(f"\n🎉 Batch creation complete!")
        print(f"   Created {len(created_events)} out of {len(interviews)} events")
        
        if created_events:
            print(f"\n📋 Summary of created events:")
            for event in created_events:
                print(f"   • {event['title']} - {event['start_time']}")
        
        return created_events
        
    except Exception as e:
        print(f"❌ Error in batch creation: {e}")
        return []

def demonstrate_event_features():
    """
    Demonstrate specific calendar event features
    """
    print("\n🎯 Calendar Event Features Demo")
    print("=" * 40)
    
    features = [
        "✅ Automatic Google Meet link generation",
        "✅ Email invitations to all attendees",
        "✅ Multiple reminder settings (24h, 30min, 10min)",
        "✅ Enhanced event descriptions with formatting",
        "✅ Timezone-aware scheduling (Asia/Kolkata)",
        "✅ Event ID returned for database storage",
        "✅ Additional attendees support",
        "✅ Custom event properties and metadata",
        "✅ Professional event formatting",
        "✅ Error handling and validation",
        "✅ OAuth2 authentication with token management",
        "✅ Phone dial-in numbers for Google Meet"
    ]
    
    print("📋 Implemented Features:")
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n🔧 Technical Implementation:")
    print(f"   • OAuth2 flow with user-specific token storage")
    print(f"   • Google Calendar API v3 integration")
    print(f"   • Conference data creation for Google Meet")
    print(f"   • Comprehensive error handling and logging")
    print(f"   • Timezone management with pytz")
    print(f"   • Event validation and data sanitization")
    
    print(f"\n📧 Email Invitation Features:")
    print(f"   • Automatic sending to all attendees")
    print(f"   • Rich HTML formatting with event details")
    print(f"   • Google Meet link included in invitation")
    print(f"   • Calendar attachment (.ics file)")
    print(f"   • RSVP tracking and response handling")
    
    print(f"\n⏰ Reminder System:")
    print(f"   • 24 hours before: Email reminder with details")
    print(f"   • 30 minutes before: Pop-up reminder")
    print(f"   • 10 minutes before: Final email with join link")
    print(f"   • Customizable reminder settings")

def main():
    """
    Main function demonstrating calendar event creation
    """
    print("🎯 Google Calendar Event Creation Demo")
    print("=" * 60)
    print("This demo shows how to create comprehensive calendar events with:")
    print("• Automatic Google Meet link generation")
    print("• Email invitations to candidate and interviewer")
    print("• Multiple reminder settings (24h, 30min, 10min)")
    print("• Professional event formatting")
    print("• OAuth2 authentication")
    print("=" * 60)
    
    try:
        while True:
            print(f"\n📋 Choose demo option:")
            print(f"1. Create single interview event")
            print(f"2. Create multiple interview events")
            print(f"3. View feature overview")
            print(f"4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                result = create_sample_interview_event()
                
                if result:
                    # Store the event ID for potential future use
                    print(f"\n💾 Event ID for database storage: {result['event_id']}")
                    
            elif choice == '2':
                events = create_multiple_interview_events()
                
                if events:
                    print(f"\n💾 Event IDs for database storage:")
                    for event in events:
                        print(f"   {event['title']}: {event['event_id']}")
                        
            elif choice == '3':
                demonstrate_event_features()
                
            elif choice == '4':
                print("\n👋 Demo completed. Thank you!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Error in main demo")

if __name__ == "__main__":
    main()
