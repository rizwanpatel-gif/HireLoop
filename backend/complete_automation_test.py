#!/usr/bin/env python3
"""
COMPLETE AUTOMATION TEST SUITE
===============================
Testing Enhanced Automation v2.0 with REAL EMAIL
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_automation():
    print("🚀 COMPLETE AUTOMATION TEST SUITE")
    print("=" * 60)
    print("📧 FROM: rizwanpatelmalipatel@gmail.com")
    print("📧 TO: rizwanpatelmalipatel6@gmail.com")
    print("=" * 60)
    
    # TEST 1: With preferred interview time (Calendar Integration)
    print("\n🔥 TEST 1: WITH PREFERRED INTERVIEW TIME")
    print("📅 Should trigger calendar availability check")
    
    candidate1 = {
        "name": "David Kim",
        "email": "rizwanpatelmalipatel6@gmail.com",
        "position": "DevOps Engineer",
        "skills": "Docker, Kubernetes, AWS, Jenkins",
        "experience_years": 4,
        "education": "Computer Science",
        "current_title": "DevOps Specialist",
        "resume_text": "DevOps engineer with 4 years experience in containerization, CI/CD pipelines, and cloud infrastructure automation.",
        "resume_summary": "Experienced DevOps Engineer",
        "interview_datetime": "2025-08-05T15:00:00"
    }
    
    result1 = create_candidate_and_show_result(candidate1, "TEST 1")
    
    print("\n" + "="*60)
    print("🔥 TEST 2: WITHOUT PREFERRED INTERVIEW TIME")
    print("📧 Should trigger analysis-complete email only")
    
    # TEST 2: Without preferred interview time (Analysis Only)
    candidate2 = {
        "name": "Sarah Johnson",
        "email": "rizwanpatelmalipatel6@gmail.com",
        "position": "Frontend Developer", 
        "skills": "React, TypeScript, CSS, JavaScript",
        "experience_years": 3,
        "education": "Software Engineering",
        "current_title": "UI Developer",
        "resume_text": "Frontend developer with 3 years experience building modern React applications with TypeScript.",
        "resume_summary": "Experienced Frontend Developer"
        # No interview_datetime
    }
    
    result2 = create_candidate_and_show_result(candidate2, "TEST 2")
    
    # Show recent candidates
    print("\n" + "="*60)
    print("📋 RECENT AUTOMATION RESULTS")
    show_recent_candidates()
    
    print("\n" + "="*60)
    print("✅ COMPLETE AUTOMATION TEST FINISHED!")
    print("📧 Check your email: rizwanpatelmalipatel6@gmail.com")
    print("📱 Check both inbox and spam folder")
    print("🖥️ Check server logs for detailed workflow execution")

def create_candidate_and_show_result(candidate_data, test_name):
    try:
        print(f"\n🔄 Creating candidate: {candidate_data['name']}")
        print(f"🎯 Position: {candidate_data['position']}")
        print(f"📅 Interview Time: {candidate_data.get('interview_datetime', 'Not specified')}")
        
        response = requests.post(
            f"{BASE_URL}/api/candidates/",
            headers={"Content-Type": "application/json"},
            json=candidate_data,
            timeout=30
        )
        
        print(f"📊 Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {test_name} SUCCESS!")
            print(f"   🆔 ID: {result['id']}")
            print(f"   📊 Status: {result['status']}")
            print(f"   📧 Email: {result['email']}")
            
            # Give automation time to complete
            print("⏳ Waiting for automation to complete...")
            time.sleep(3)
            
            return result
        else:
            print(f"❌ {test_name} FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ {test_name} ERROR: {e}")
        return None

def show_recent_candidates():
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/")
        if response.status_code == 200:
            candidates = response.json()
            
            print(f"📊 Total candidates: {len(candidates)}")
            print("\n🔍 Last 5 candidates:")
            
            for candidate in candidates[-5:]:
                print(f"\n👤 {candidate['name']} (ID: {candidate['id']})")
                print(f"   📧 Email: {candidate['email']}")
                print(f"   🎯 Position: {candidate['position']}")
                print(f"   📊 Status: {candidate['status']}")
                print(f"   🤖 AI Score: {candidate.get('ai_overall_score', 'Pending')}")
                print(f"   📅 Interview: {candidate.get('interview_datetime', 'Not set')}")
                print(f"   ✅ Scheduled: {candidate.get('interview_scheduled', False)}")
                
        else:
            print(f"❌ Error getting candidates: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_complete_automation()
