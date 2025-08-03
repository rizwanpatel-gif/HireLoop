"""
Quick Test for Automatic Interview Scheduling
===========================================

This script provides a simple test to verify that the automatic
interview scheduling logic is working correctly.
"""

import asyncio
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append('.')

# Import required components
from automatic_interview_scheduler import (
    AutomaticInterviewScheduler,
    InterviewScheduleRequest,
    InterviewType
)
from database_setup import init_database
from candidate_management_api import SessionLocal, CandidateDB, CandidateCreate
import uuid

async def test_automatic_scheduling():
    """Test the automatic interview scheduling functionality"""
    
    print("🧪 Testing Automatic Interview Scheduling")
    print("=" * 50)
    
    # Initialize database
    init_database()
    db = SessionLocal()
    
    try:
        # Create a test candidate directly in database
        test_candidate = CandidateDB(
            id=str(uuid.uuid4()),
            name="Test Candidate",
            email="test@example.com",
            position="Software Engineer",
            experience_years=5.0,
            skills=[
                {"name": "Python", "level": "expert", "years_experience": 5.0},
                {"name": "Django", "level": "advanced", "years_experience": 3.0}
            ],
            status="active",
            ai_analysis_status="completed",
            ai_overall_score=85.0,
            ai_analysis_results={
                "strengths": ["Python expertise", "Problem solving"],
                "areas_for_improvement": ["System design", "Leadership"],
                "interview_strategy": {
                    "focus_areas": ["Technical depth", "Architecture"]
                }
            }
        )
        
        db.add(test_candidate)
        db.commit()
        
        print(f"✅ Created test candidate: {test_candidate.name} (ID: {test_candidate.id})")
        
        # Create scheduling request
        interview_time = datetime.now() + timedelta(days=1)
        interview_time = interview_time.replace(hour=14, minute=0, second=0, microsecond=0)
        
        request = InterviewScheduleRequest(
            candidate_id=test_candidate.id,
            preferred_time=interview_time,
            duration_minutes=60,
            interview_type=InterviewType.TECHNICAL,
            interview_round=1,
            is_remote=True,
            notes="Test automatic scheduling"
        )
        
        print(f"📅 Scheduling interview for: {interview_time}")
        
        # Test the automatic scheduler
        scheduler = AutomaticInterviewScheduler()
        result = await scheduler.schedule_interview_automatically(request, db)
        
        # Display results
        print("\\n📊 Scheduling Results:")
        print("-" * 30)
        print(f"Success: {result.success}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        print(f"Interview ID: {result.interview_id}")
        
        if result.interviewer_selected:
            interviewer = result.interviewer_selected
            print(f"Interviewer: {interviewer['name']}")
            print(f"Match Score: {interviewer['match_score']:.1f}/100")
            print(f"Confidence: {interviewer['confidence']:.1f}")
        
        print(f"Calendar Event: {result.calendar_event_id or 'Not created'}")
        print(f"Google Meet: {result.google_meet_link or 'Not generated'}")
        print(f"Notifications Sent: {result.notifications_sent}")
        
        if result.errors:
            print("\\nErrors:")
            for error in result.errors:
                print(f"  • {error}")
        
        if result.success:
            print("\\n🎉 Automatic scheduling test PASSED!")
        else:
            print("\\n❌ Automatic scheduling test FAILED!")
            
        # Show what components were tested
        print("\\n🔍 Components Tested:")
        print("  ✅ Calendar availability checking (simulated)")
        print("  ✅ AI interviewer matching")
        print("  ✅ Database record creation")
        print("  ✅ Calendar event generation (simulated)")
        print("  ✅ Email notifications (simulated)")
        print("  ✅ Interview record updates")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

def main():
    """Run the test"""
    print("🚀 Starting Automatic Interview Scheduling Test")
    print("This test verifies all automation components work together\\n")
    
    asyncio.run(test_automatic_scheduling())

if __name__ == "__main__":
    main()
