"""
Enhanced usage example demonstrating database connection, session management, 
and Google Calendar event creation with OAuth2 authentication
"""
from database import DatabaseManager, get_db_session, test_connection
from models import User, Candidate, Interview, UserRole, InterviewType
from datetime import datetime, timedelta
import pytz

# Import Google Calendar service
try:
    from google_calendar_service import GoogleCalendarService
    from oauth2_config import OAuth2Config
    CALENDAR_AVAILABLE = True
except ImportError:
    print("⚠️ Google Calendar modules not available. Calendar examples will be skipped.")
    CALENDAR_AVAILABLE = False

def demonstrate_calendar_event_creation():
    """
    Demonstrate comprehensive Google Calendar event creation with OAuth2
    """
    if not CALENDAR_AVAILABLE:
        print("📅 Calendar demonstration skipped - modules not available")
        return
    
    print("\n=== Google Calendar Event Creation Demo ===")
    
    try:
        # Initialize calendar service
        calendar_service = GoogleCalendarService()
        
        # Check if user is authenticated (replace with actual interviewer email)
        interviewer_email = input("Enter interviewer email for calendar demo (or 'skip' to skip): ").strip()
        
        if interviewer_email.lower() == 'skip':
            print("📅 Calendar demo skipped by user")
            return
        
        if not interviewer_email:
            print("❌ Valid email required for calendar demo")
            return
        
        print(f"🔐 Checking authentication for {interviewer_email}...")
        
        # Authenticate if needed
        if not calendar_service.is_authenticated(interviewer_email):
            print("🔑 Authentication required. Starting OAuth2 flow...")
            auth_success = calendar_service.authenticate(interviewer_email)
            
            if not auth_success:
                print("❌ Authentication failed. Skipping calendar demo.")
                return
        else:
            print("✅ User already authenticated")
        
        # Get user info
        user_info = calendar_service.get_user_info()
        if user_info:
            print(f"👤 Authenticated as: {user_info['email']}")
            print(f"📅 Calendar: {user_info['calendar_summary']}")
        
        # Create a comprehensive calendar event
        print("\n📝 Creating comprehensive calendar event...")
        
        # Sample interview data
        interview_start = datetime.now() + timedelta(days=1, hours=2)  # Tomorrow, 2 hours from now
        
        result = calendar_service.create_calendar_event_with_details(
            title="Senior Python Developer Interview",
            candidate_name="John Doe",
            candidate_email="john.doe@example.com",
            position="Senior Python Developer",
            interviewer_name=interviewer_email.split('@')[0].title(),
            interviewer_email=interviewer_email,
            start_datetime=interview_start,
            duration_minutes=90,
            interview_type="Technical",
            notes="""
Technical Interview Focus Areas:
• Python programming and best practices
• System design and architecture
• Database design and optimization
• API development with FastAPI
• Problem-solving and algorithms

Please prepare:
- Laptop with coding environment
- Portfolio/previous projects to discuss
- Questions about the role and company
            """.strip(),
            additional_attendees=["hr@company.com"]
        )
        
        if result:
            print("✅ Calendar event created successfully!")
            print(f"   🆔 Event ID: {result['event_id']}")
            print(f"   📋 Title: {result['title']}")
            print(f"   🕒 Start: {result['start_time']}")
            print(f"   ⏱️ Duration: {result['duration_minutes']} minutes")
            print(f"   👥 Attendees: {result['attendees_count']}")
            
            if result['meet_link']:
                print(f"   🎥 Google Meet: {result['meet_link']}")
            
            if result['event_link']:
                print(f"   🔗 Calendar Link: {result['event_link']}")
            
            print(f"   ⏰ Reminders: {'✅' if result['reminders_set'] else '❌'}")
            print(f"   📧 Invitations: {'✅' if result['invitations_sent'] else '❌'}")
            
            # Store event ID for potential future use
            return result['event_id']
        else:
            print("❌ Failed to create calendar event")
            return None
            
    except Exception as e:
        print(f"❌ Error in calendar demo: {e}")
        return None

def demonstrate_database_calendar_integration():
    """
    Demonstrate integration between database records and calendar events
    """
    print("\n=== Database + Calendar Integration Demo ===")
    
    if not CALENDAR_AVAILABLE:
        print("📅 Calendar integration demo skipped - modules not available")
        return
    
    # Create database manager
    db_manager = DatabaseManager()
    
    try:
        with db_manager.get_db_context() as db:
            # Create sample data with calendar integration
            print("📊 Creating database records with calendar integration...")
            
            # Create interviewer
            interviewer = User(
                email="interviewer@company.com",
                name="Alice Johnson",
                role=UserRole.INTERVIEWER,
                google_calendar_id="interviewer@company.com"
            )
            db.add(interviewer)
            db.flush()
            
            # Create candidate
            candidate = Candidate(
                name="Sarah Wilson",
                email="sarah.wilson@email.com",
                position="Full Stack Developer",
                skills='["React", "Node.js", "Python", "PostgreSQL"]',
                ai_score=9.2
            )
            db.add(candidate)
            db.flush()
            
            # Schedule interview with calendar event
            interview_time = datetime.now() + timedelta(days=2, hours=14)  # Day after tomorrow at 2 PM
            
            interview = Interview(
                candidate_id=candidate.id,
                interviewer_id=interviewer.id,
                scheduled_time=interview_time,
                duration=75,
                type=InterviewType.TECHNICAL,
                notes="Full stack technical interview focusing on React and Python"
            )
            db.add(interview)
            db.flush()
            
            print(f"✅ Created interview record (ID: {interview.id})")
            
            # Now create calendar event if authentication is available
            calendar_service = GoogleCalendarService()
            
            # For demo purposes, we'll simulate the calendar creation
            print("📅 Creating corresponding calendar event...")
            
            # Prepare interview data for calendar
            interview_data = {
                'id': interview.id,
                'scheduled_time': interview.scheduled_time,
                'duration': interview.duration,
                'type': interview.type.value,
                'candidate_name': candidate.name,
                'interviewer_name': interviewer.name,
                'position': candidate.position,
                'notes': interview.notes
            }
            
            # This would normally require OAuth authentication
            print(f"📋 Interview Data Prepared:")
            print(f"   Candidate: {candidate.name} ({candidate.email})")
            print(f"   Position: {candidate.position}")
            print(f"   Interviewer: {interviewer.name} ({interviewer.email})")
            print(f"   Time: {interview.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Duration: {interview.duration} minutes")
            print(f"   Type: {interview.type.value}")
            
            # In a real scenario, you would:
            # 1. Check if interviewer is authenticated
            # 2. Create calendar event
            # 3. Store event ID in interview record
            
            # Simulate successful event creation
            simulated_event_id = f"event_{interview.id}_{int(datetime.now().timestamp())}"
            interview.google_event_id = simulated_event_id
            
            print(f"✅ Simulated calendar event creation")
            print(f"   Event ID: {simulated_event_id}")
            print(f"   Status: Interview record updated with event ID")
            
    except Exception as e:
        print(f"❌ Error in database+calendar demo: {e}")

def main():
    """Main function demonstrating database usage and calendar integration"""
    
    # Test database connection
    print("Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed!")
        return
    print("✅ Database connection successful!")
    
    # Create database manager instance
    db_manager = DatabaseManager()
    
    # Create tables
    print("\nCreating database tables...")
    db_manager.create_tables()
    print("✅ Tables created successfully!")
    
    # Example 1: Using context manager (recommended for simple operations)
    print("\n=== Example 1: Using Context Manager ===")
    with db_manager.get_db_context() as db:
        # Create a user
        user = User(
            email="test@example.com",
            name="Test User",
            role=UserRole.INTERVIEWER,
            google_calendar_id="test@example.com"
        )
        db.add(user)
        db.flush()  # Flush to get the ID without committing
        
        print(f"Created user: {user.name} (ID: {user.id})")
        
        # Create a candidate
        candidate = Candidate(
            name="Test Candidate",
            email="candidate@example.com",
            position="Software Engineer",
            skills='["Python", "FastAPI", "SQLAlchemy"]',
            ai_score=8.5
        )
        db.add(candidate)
        db.flush()
        
        print(f"Created candidate: {candidate.name} (ID: {candidate.id})")
        
        # Schedule an interview
        interview = Interview(
            candidate_id=candidate.id,
            interviewer_id=user.id,
            scheduled_time=datetime.now() + timedelta(days=7),
            duration=60,
            type=InterviewType.TECHNICAL
        )
        db.add(interview)
        db.flush()
        
        print(f"Scheduled interview (ID: {interview.id}) for {interview.scheduled_time}")
    
    # Example 2: Using direct session (manual session management)
    print("\n=== Example 2: Using Direct Session ===")
    session = get_db_session()
    try:
        # Query all users
        users = session.query(User).all()
        print(f"Total users in database: {len(users)}")
        
        # Query all candidates
        candidates = session.query(Candidate).all()
        print(f"Total candidates in database: {len(candidates)}")
        
        # Query scheduled interviews
        scheduled_interviews = session.query(Interview).filter(
            Interview.status == 'scheduled'
        ).all()
        print(f"Scheduled interviews: {len(scheduled_interviews)}")
        
        # Query interviews with relationships
        interviews_with_details = session.query(Interview).join(
            Candidate, Interview.candidate_id == Candidate.id
        ).join(
            User, Interview.interviewer_id == User.id
        ).all()
        
        print("\nInterview Details:")
        for interview in interviews_with_details:
            print(f"  - {interview.candidate.name} interviewed by {interview.interviewer.name}")
            print(f"    Scheduled: {interview.scheduled_time}")
            print(f"    Type: {interview.type.value}")
            print(f"    Status: {interview.status.value}")
            
    except Exception as e:
        session.rollback()
        print(f"Error during database operations: {e}")
        raise
    finally:
        session.close()
    
    # Example 3: Database statistics
    print("\n=== Example 3: Database Statistics ===")
    with db_manager.get_db_context() as db:
        stats = {
            "total_users": db.query(User).count(),
            "total_candidates": db.query(Candidate).count(),
            "total_interviews": db.query(Interview).count(),
            "users_by_role": {},
            "interviews_by_type": {}
        }
        
        # Count users by role
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            stats["users_by_role"][role.value] = count
        
        # Count interviews by type
        for interview_type in InterviewType:
            count = db.query(Interview).filter(Interview.type == interview_type).count()
            stats["interviews_by_type"][interview_type.value] = count
        
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    # Example 4: Raw SQL execution
    print("\n=== Example 4: Raw SQL Execution ===")
    try:
        # Execute raw SQL to get user count
        result = db_manager.execute_raw_sql("SELECT COUNT(*) as user_count FROM users")
        print(f"User count from raw SQL: {result[0][0]}")
        
        # Execute parameterized query
        result = db_manager.execute_raw_sql(
            "SELECT name, email FROM users WHERE role = :role",
            {"role": UserRole.INTERVIEWER.value}
        )
        print("Interviewers:")
        for row in result:
            print(f"  - {row[0]} ({row[1]})")
            
    except Exception as e:
        print(f"Raw SQL execution error: {e}")
    
    # Example 5: Google Calendar Integration
    demonstrate_calendar_event_creation()
    
    # Example 6: Database + Calendar Integration
    demonstrate_database_calendar_integration()
    
    print("\n✅ All examples completed successfully!")
    
    if CALENDAR_AVAILABLE:
        print("\n📅 Calendar Integration Features Demonstrated:")
        print("   • OAuth2 authentication flow")
        print("   • Comprehensive event creation with Google Meet")
        print("   • Email invitations to all attendees")
        print("   • Multiple reminder settings (24h, 30min, 10min)")
        print("   • Event ID storage for database integration")
        print("   • Enhanced event descriptions and formatting")
    
    print("\n🎯 Next Steps:")
    print("   1. Set up Google Cloud Console credentials")
    print("   2. Configure OAuth2 authentication")
    print("   3. Test calendar integration with real users")
    print("   4. Integrate with FastAPI endpoints")

if __name__ == "__main__":
    main()
    
    # Example 2: Using direct session (manual session management)
    print("\n=== Example 2: Using Direct Session ===")
    session = get_db_session()
    try:
        # Query all users
        users = session.query(User).all()
        print(f"Total users in database: {len(users)}")
        
        # Query all candidates
        candidates = session.query(Candidate).all()
        print(f"Total candidates in database: {len(candidates)}")
        
        # Query scheduled interviews
        scheduled_interviews = session.query(Interview).filter(
            Interview.status == 'scheduled'
        ).all()
        print(f"Scheduled interviews: {len(scheduled_interviews)}")
        
        # Query interviews with relationships
        interviews_with_details = session.query(Interview).join(
            Candidate, Interview.candidate_id == Candidate.id
        ).join(
            User, Interview.interviewer_id == User.id
        ).all()
        
        print("\nInterview Details:")
        for interview in interviews_with_details:
            print(f"  - {interview.candidate.name} interviewed by {interview.interviewer.name}")
            print(f"    Scheduled: {interview.scheduled_time}")
            print(f"    Type: {interview.type.value}")
            print(f"    Status: {interview.status.value}")
            
    except Exception as e:
        session.rollback()
        print(f"Error during database operations: {e}")
        raise
    finally:
        session.close()
    
    # Example 3: Database statistics
    print("\n=== Example 3: Database Statistics ===")
    with db_manager.get_db_context() as db:
        stats = {
            "total_users": db.query(User).count(),
            "total_candidates": db.query(Candidate).count(),
            "total_interviews": db.query(Interview).count(),
            "users_by_role": {},
            "interviews_by_type": {}
        }
        
        # Count users by role
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            stats["users_by_role"][role.value] = count
        
        # Count interviews by type
        for interview_type in InterviewType:
            count = db.query(Interview).filter(Interview.type == interview_type).count()
            stats["interviews_by_type"][interview_type.value] = count
        
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    # Example 4: Raw SQL execution
    print("\n=== Example 4: Raw SQL Execution ===")
    try:
        # Execute raw SQL to get user count
        result = db_manager.execute_raw_sql("SELECT COUNT(*) as user_count FROM users")
        print(f"User count from raw SQL: {result[0][0]}")
        
        # Execute parameterized query
        result = db_manager.execute_raw_sql(
            "SELECT name, email FROM users WHERE role = :role",
            {"role": UserRole.INTERVIEWER.value}
        )
        print("Interviewers:")
        for row in result:
            print(f"  - {row[0]} ({row[1]})")
            
    except Exception as e:
        print(f"Raw SQL execution error: {e}")
    
    print("\n✅ All examples completed successfully!")

if __name__ == "__main__":
    main()
