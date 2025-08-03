"""
Example usage of the interview scheduling system models
"""
from models import DatabaseConfig, UserRole, InterviewType, InterviewStatus
from models import create_user, create_candidate, schedule_interview
from datetime import datetime, timedelta

def example_usage():
    """Demonstrate how to use the interview scheduling system"""
    
    # Initialize database
    db_config = DatabaseConfig("sqlite:///example_interview_system.db")
    db_config.create_tables()
    
    session = db_config.get_session()
    
    try:
        # Create users
        print("Creating users...")
        interviewer = create_user(
            session,
            email="interviewer@company.com",
            name="Senior Developer",
            role=UserRole.INTERVIEWER,
            google_calendar_id="interviewer@company.com"
        )
        
        # Create candidate
        print("Creating candidate...")
        candidate = create_candidate(
            session,
            name="Test Candidate",
            email="candidate@email.com",
            phone="+1-555-0123",
            position="Python Developer",
            resume_text="Experienced Python developer with 3 years of experience...",
            skills='["Python", "Django", "PostgreSQL", "REST APIs"]',
            ai_score=8.0
        )
        
        # Schedule interview
        print("Scheduling interview...")
        interview_time = datetime.now() + timedelta(days=7, hours=2)  # Next week
        
        interview = schedule_interview(
            session,
            candidate_id=candidate.id,
            interviewer_id=interviewer.id,
            scheduled_time=interview_time,
            duration=60,
            interview_type=InterviewType.TECHNICAL
        )
        
        print(f"✓ Interview scheduled with ID: {interview.id}")
        print(f"  Candidate: {candidate.name}")
        print(f"  Interviewer: {interviewer.name}")
        print(f"  Scheduled for: {interview_time}")
        print(f"  Duration: {interview.duration} minutes")
        print(f"  Type: {interview.type.value}")
        
        # Query examples
        print("\nQuerying data...")
        
        # Get all interviews for a candidate
        candidate_interviews = session.query(Interview).filter_by(candidate_id=candidate.id).all()
        print(f"Candidate has {len(candidate_interviews)} interview(s)")
        
        # Get all interviews conducted by an interviewer
        from models import Interview
        interviewer_interviews = session.query(Interview).filter_by(interviewer_id=interviewer.id).all()
        print(f"Interviewer has {len(interviewer_interviews)} interview(s)")
        
        # Get interviews by status
        scheduled_interviews = session.query(Interview).filter_by(status=InterviewStatus.SCHEDULED).all()
        print(f"There are {len(scheduled_interviews)} scheduled interview(s)")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    example_usage()
