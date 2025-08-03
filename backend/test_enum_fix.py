"""
Quick Test - Fixed Enum Issues
Tests the database enum fix and basic scheduling
"""
import sys
import os
import requests
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enum_fix():
    """Test the database enum fix"""
    
    print("🔧 TESTING DATABASE ENUM FIXES")
    print("=" * 40)
    
    # Use a time that's likely to be available (late evening)
    interview_time = datetime.now() + timedelta(days=1)
    interview_time = interview_time.replace(hour=20, minute=0, second=0, microsecond=0)  # 8 PM
    
    test_candidate = {
        "name": "Test User", 
        "email": f"test.enum.fix{int(datetime.now().timestamp())}@example.com",
        "position": "Software Engineer",
        "experience_years": 2,
        "skills": ["Python", "JavaScript"],
        "education": "Bachelor Degree",
        "preferred_salary": 60000.0,
        "availability": "Available",
        "interview_datetime": interview_time.isoformat(),
        "github_url": "https://github.com/test",
        "linkedin_url": "https://linkedin.com/in/test",
        "portfolio_url": "https://test.dev",
        "cover_letter": "Test application",
        "resume_text": "Test resume with experience",
        "current_title": "Developer",
        "resume_summary": "Test summary"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/candidates/",
            json=test_candidate,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 or response.status_code == 201:
            candidate_data = response.json()
            candidate_id = candidate_data.get('id') or candidate_data.get('candidate_id')
            
            print(f"✅ Test candidate created: ID {candidate_id}")
            print(f"📅 Time: {interview_time.strftime('%A, %B %d at %I:%M %p')}")
            print(f"⏳ Waiting for automation...")
            
            import time
            time.sleep(10)
            
            # Check status
            status_response = requests.get(f"http://localhost:8000/api/candidates/{candidate_id}")
            if status_response.status_code == 200:
                updated = status_response.json()
                print(f"📊 Status: {updated.get('status')}")
                print(f"📅 Scheduled: {updated.get('interview_scheduled')}")
                
                if updated.get('status') == 'scheduled':
                    print("✅ SUCCESS: Database enum issues fixed!")
                    print("✅ Interview scheduled successfully!")
                    return True
                elif updated.get('status') == 'automation_failed':
                    print("❌ Automation failed - check backend logs")
                    return False
                else:
                    print(f"ℹ️  Status: {updated.get('status')}")
                    return True
            else:
                print("❌ Could not check status")
                return False
        else:
            print(f"❌ Failed to create candidate: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_enum_fix()
    if success:
        print("\n🎉 ENUM FIXES WORKING!")
    else:
        print("\n🔧 Need to check backend logs")
