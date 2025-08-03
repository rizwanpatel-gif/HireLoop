"""
Quick test for the running API
"""
import requests
import json

def test_api():
    print("🧪 Testing RHero API...")
    
    # Test health endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            result = response.json()
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test candidate creation
    test_candidate = {
        "name": "Test User",
        "email": "test@example.com",
        "current_title": "Software Engineer",
        "skills": ["Python", "FastAPI", "React"],
        "resume_summary": "Experienced developer with 5 years in web development."
    }
    
    try:
        print("\n🧪 Testing candidate creation...")
        response = requests.post(
            "http://127.0.0.1:8000/api/candidates/",
            json=test_candidate,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Candidate created successfully!")
            print(f"   Name: {result['name']}")
            print(f"   Email: {result['email']}")
            print(f"   ID: {result['id']}")
            print(f"   Status: {result['status']}")
            return True
        else:
            print(f"❌ Candidate creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Candidate creation error: {e}")
        return False

if __name__ == "__main__":
    test_api()
