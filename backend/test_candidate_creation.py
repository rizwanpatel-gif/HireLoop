#!/usr/bin/env python3
"""
Test script to verify candidate creation and automation workflow
"""

import requests
import json

def test_candidate_creation():
    """Test creating a candidate with array skills format"""
    
    url = "http://localhost:8000/api/candidates/"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Test data with skills as array
    candidate_data = {
        "name": "David Kim",
        "email": "david.kim.test@example.com",
        "position": "DevOps Engineer", 
        "skills": ["Docker", "Kubernetes", "AWS", "Jenkins"],  # Array format
        "experience_years": 4,
        "education": "Computer Science",
        "current_title": "DevOps Specialist",
        "resume_text": "Experienced DevOps Engineer",
        "resume_summary": "Testing automation",
        "interview_datetime": "2025-08-15T10:50:00"
    }
    
    try:
        print("🚀 Testing candidate creation...")
        print(f"📤 Sending data: {json.dumps(candidate_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=candidate_data)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Candidate created successfully!")
            return response.json()
        else:
            print(f"❌ Failed to create candidate: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return None

if __name__ == "__main__":
    result = test_candidate_creation()
    if result:
        print(f"🎉 Test completed successfully!")
        print(f"📋 Result: {json.dumps(result, indent=2)}")
    else:
        print("❌ Test failed")
