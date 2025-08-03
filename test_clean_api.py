"""
Simple test to verify the clean candidate creation works
"""

import requests
import json
from datetime import datetime, timedelta

# Test data - simple candidate as per your requirements
test_candidate = {
    "name": "John Doe",
    "email": "john.doe@example.com", 
    "current_title": "Senior Software Engineer",
    "skills": ["Python", "React", "PostgreSQL", "AWS"],
    "resume_summary": "Experienced software engineer with 8 years in full-stack development. Led multiple teams and delivered scalable web applications. Strong background in Python, React, and cloud technologies.",
    "preferred_interview_date": (datetime.now() + timedelta(days=3)).isoformat(),
    "phone": "+1 (555) 123-4567",
    "location": "San Francisco, CA",
    "experience_years": 8.5
}

def test_candidate_creation():
    """Test creating a candidate via the API"""
    
    print("🧪 Testing Candidate Creation API...")
    print(f"📋 Test Data: {json.dumps(test_candidate, indent=2)}")
    
    try:
        # Make request to API
        response = requests.post(
            "http://localhost:8000/api/candidates/",
            json=test_candidate,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Created candidate: {result['name']} (ID: {result['id']})")
            print(f"   Status: {result['status']}")
            print(f"   Skills: {result['skills']}")
            print(f"   Analysis Status: {result['ai_analysis_status']}")
            return result
        else:
            print(f"❌ FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("   Is the backend server running on http://localhost:8000?")
        print("   Start it with: cd backend && python main.py")
        return None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return None

def test_candidate_listing():
    """Test listing candidates"""
    
    print("\n🧪 Testing Candidate Listing API...")
    
    try:
        response = requests.get("http://localhost:8000/api/candidates/")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Total candidates: {result['total']}")
            print(f"   Current page: {result['page']}")
            
            if result['candidates']:
                print("   Recent candidates:")
                for candidate in result['candidates'][:3]:
                    print(f"     - {candidate['name']} ({candidate['email']}) - {candidate['status']}")
            return result
        else:
            print(f"❌ FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_health_check():
    """Test if the API is responsive"""
    
    print("\n🧪 Testing API Health Check...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend is healthy!")
            print(f"   Status: {result['status']}")
            print(f"   Service: {result['service']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RHero API Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    if health_ok:
        # Test 2: Create candidate
        created_candidate = test_candidate_creation()
        
        # Test 3: List candidates  
        candidates_list = test_candidate_listing()
        
        if created_candidate and candidates_list:
            print("\n🎉 All tests passed! The simplified candidate system is working.")
            print(f"✅ You can now submit candidates with: name, email, title, skills, resume_summary")
            print(f"✅ Frontend form should work at: http://localhost:3000")
        else:
            print("\n⚠️  Some tests failed. Check the error messages above.")
    else:
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend && python main.py")
    
    print("\n📋 Next steps:")
    print("   1. Start backend: cd backend && python main.py") 
    print("   2. Start frontend: cd frontend && npm start")
    print("   3. Open http://localhost:3000 to test the form")
