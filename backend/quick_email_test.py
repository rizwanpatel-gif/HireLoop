#!/usr/bin/env python3
"""
IMMEDIATE EMAIL TEST
===================
Testing: FROM rizwanpatelmalipatel@gmail.com TO rizwanpatelmalipatel6@gmail.com
"""

import requests
import json

def quick_email_test():
    print("🔥 IMMEDIATE EMAIL TEST")
    print("📧 FROM: rizwanpatelmalipatel@gmail.com (configured in .env)")
    print("📧 TO: rizwanpatelmalipatel6@gmail.com (test recipient)")
    print("=" * 60)
    
    # Complete candidate data with all required fields
    candidate = {
        "name": "TEST EMAIL USER",
        "email": "rizwanpatelmalipatel6@gmail.com",
        "position": "Test Position",
        "skills": "Python, JavaScript",
        "experience_years": 2,
        "education": "Computer Science",
        "current_title": "Software Developer",
        "resume_text": "Experienced developer with strong technical skills",
        "resume_summary": "Testing email automation",
        "phone": "+1234567890",
        "location": "Remote"
    }
    
    try:
        print("🚀 Creating candidate to trigger automation...")
        response = requests.post(
            "http://localhost:8000/api/candidates/",
            headers={"Content-Type": "application/json"},
            json=candidate,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   🆔 Candidate ID: {result['id']}")
            print(f"   📧 Email: {result['email']}")
            print(f"   📊 Status: {result['status']}")
            print(f"\n📬 EMAIL SHOULD BE SENT TO: rizwanpatelmalipatel6@gmail.com")
            print(f"📬 EMAIL SENT FROM: rizwanpatelmalipatel@gmail.com")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_email_test()
