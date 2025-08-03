"""
Interview Scheduling Demo Script
===============================

This script demonstrates the complete interview scheduling workflow:
1. Create test candidates
2. Wait for AI analysis completion
3. Schedule interviews with AI-powered interviewer matching
4. Show Google Calendar integration
5. Display comprehensive results

Usage:
    python interview_scheduling_demo.py
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class InterviewSchedulingDemo:
    """
    Comprehensive demonstration of the interview scheduling system
    """
    
    def __init__(self):
        self.candidates = []
        self.interviews = []
        
    async def run_complete_demo(self):
        """Run the complete interview scheduling demonstration"""
        
        print("🚀 Interview Scheduling System Demo")
        print("=" * 60)
        
        try:
            # Step 1: Check API availability
            await self.check_api_health()
            
            # Step 2: Create test candidates
            await self.create_test_candidates()
            
            # Step 3: Wait for AI analysis
            await self.wait_for_ai_analysis()
            
            # Step 4: Schedule interviews
            await self.schedule_interviews()
            
            # Step 5: Monitor interview status
            await self.monitor_interview_status()
            
            # Step 6: Show comprehensive results
            await self.show_final_results()
            
            print("\n🎉 Interview scheduling demonstration completed successfully!")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed: {e}")
    
    async def check_api_health(self):
        """Check if the API is running and accessible"""
        
        print("\n🔍 Step 1: Checking API Health")
        print("-" * 40)
        
        try:
            response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
            if response.status_code == 200:
                print("   ✅ API is running and accessible")
                print(f"   📖 Documentation: {API_BASE_URL}/docs")
            else:
                raise Exception(f"API returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ API is not running")
            print(f"   💡 Please start the API with: python candidate_management_api.py")
            raise Exception("API not accessible")
        except Exception as e:
            print(f"   ❌ API health check failed: {e}")
            raise
    
    async def create_test_candidates(self):
        """Create comprehensive test candidates for the demo"""
        
        print("\n📝 Step 2: Creating Test Candidates")
        print("-" * 40)
        
        test_candidates = [
            {
                "name": "Sarah Chen",
                "email": "sarah.chen@demo.com",
                "position": "Senior Full Stack Developer",
                "experience_years": 6.0,
                "phone": "+1-555-0123",
                "location": "San Francisco, CA",
                "skills": [
                    {"name": "Python", "level": "expert", "years_experience": 6.0, "projects_count": 20},
                    {"name": "React", "level": "advanced", "years_experience": 4.0, "projects_count": 15},
                    {"name": "PostgreSQL", "level": "advanced", "years_experience": 5.0, "projects_count": 12},
                    {"name": "Docker", "level": "intermediate", "years_experience": 3.0, "projects_count": 8},
                    {"name": "AWS", "level": "intermediate", "years_experience": 2.0, "projects_count": 6}
                ],
                "education": "MS Computer Science, Stanford University",
                "previous_companies": ["Google", "Airbnb", "Stripe"],
                "github_url": "https://github.com/sarahchen",
                "linkedin_url": "https://linkedin.com/in/sarahchen",
                "cover_letter": "I'm excited to apply for the Senior Full Stack Developer position. With 6 years of experience building scalable web applications, I've led teams at Google and Airbnb to deliver high-impact products...",
                "resume_text": "Sarah Chen - Senior Full Stack Developer\n\nEXPERIENCE:\nSenior Software Engineer @ Google (2021-2023)\n- Led development of payment processing system handling $10M+ daily\n- Architected microservices infrastructure serving 100M+ users\n- Mentored 5 junior developers\n\nSoftware Engineer @ Airbnb (2019-2021)\n- Built real-time booking system with 99.9% uptime\n- Optimized database queries reducing response time by 40%\n\nSOFTWARE ENGINEER @ Stripe (2018-2019)\n- Developed API endpoints for payment processing\n- Implemented fraud detection algorithms",
                "preferred_salary": 180000.0,
                "availability": "Available in 2 weeks",
                "remote_preference": "remote"
            },
            {
                "name": "Michael Rodriguez",
                "email": "michael.rodriguez@demo.com", 
                "position": "DevOps Engineer",
                "experience_years": 4.0,
                "phone": "+1-555-0456",
                "location": "Austin, TX",
                "skills": [
                    {"name": "Kubernetes", "level": "advanced", "years_experience": 3.0, "projects_count": 10},
                    {"name": "Terraform", "level": "advanced", "years_experience": 4.0, "projects_count": 15},
                    {"name": "Python", "level": "intermediate", "years_experience": 3.0, "projects_count": 8},
                    {"name": "AWS", "level": "expert", "years_experience": 4.0, "projects_count": 20},
                    {"name": "Jenkins", "level": "advanced", "years_experience": 3.0, "projects_count": 12}
                ],
                "education": "BS Computer Engineering, University of Texas",
                "previous_companies": ["Netflix", "Uber"],
                "github_url": "https://github.com/mrodriguez",
                "cover_letter": "As a DevOps Engineer with 4 years of experience, I specialize in building robust, scalable infrastructure. At Netflix, I managed Kubernetes clusters serving millions of users...",
                "resume_text": "Michael Rodriguez - DevOps Engineer\n\nEXPERIENCE:\nSenior DevOps Engineer @ Netflix (2022-2024)\n- Managed Kubernetes clusters with 1000+ nodes\n- Implemented CI/CD pipelines reducing deployment time by 60%\n- Automated infrastructure provisioning with Terraform\n\nDevOps Engineer @ Uber (2020-2022)\n- Built monitoring and alerting systems\n- Optimized AWS costs saving $2M annually",
                "preferred_salary": 140000.0,
                "availability": "Available immediately",
                "remote_preference": "hybrid"
            },
            {
                "name": "Emily Johnson",
                "email": "emily.johnson@demo.com",
                "position": "Frontend Developer",
                "experience_years": 2.5,
                "phone": "+1-555-0789",
                "location": "New York, NY",
                "skills": [
                    {"name": "React", "level": "advanced", "years_experience": 2.5, "projects_count": 12},
                    {"name": "TypeScript", "level": "intermediate", "years_experience": 2.0, "projects_count": 8},
                    {"name": "CSS", "level": "advanced", "years_experience": 3.0, "projects_count": 15},
                    {"name": "Node.js", "level": "beginner", "years_experience": 1.0, "projects_count": 3},
                    {"name": "GraphQL", "level": "intermediate", "years_experience": 1.5, "projects_count": 5}
                ],
                "education": "Bootcamp Graduate - Flatiron School",
                "previous_companies": ["Shopify"],
                "portfolio_url": "https://emilyjohnson.dev",
                "github_url": "https://github.com/emilyjohnson",
                "cover_letter": "I'm passionate about creating beautiful, accessible user interfaces. During my time at Shopify, I contributed to merchant dashboard improvements that increased user engagement by 25%...",
                "resume_text": "Emily Johnson - Frontend Developer\n\nEXPERIENCE:\nFrontend Developer @ Shopify (2022-2024)\n- Developed merchant dashboard features serving 1M+ users\n- Improved web performance scores by 30%\n- Collaborated with design team on UI/UX improvements\n\nJunior Developer @ Local Agency (2021-2022)\n- Built responsive websites for small businesses\n- Maintained client WordPress sites",
                "preferred_salary": 95000.0,
                "availability": "Available in 1 week",
                "remote_preference": "on-site"
            }
        ]
        
        for candidate_data in test_candidates:
            try:
                # Prepare form data
                form_data = {
                    "name": candidate_data["name"],
                    "email": candidate_data["email"],
                    "position": candidate_data["position"],
                    "experience_years": candidate_data["experience_years"],
                    "skills": json.dumps(candidate_data["skills"]),
                    "phone": candidate_data.get("phone"),
                    "location": candidate_data.get("location"),
                    "education": candidate_data.get("education"),
                    "previous_companies": json.dumps(candidate_data.get("previous_companies", [])),
                    "github_url": candidate_data.get("github_url"),
                    "linkedin_url": candidate_data.get("linkedin_url"),
                    "portfolio_url": candidate_data.get("portfolio_url"),
                    "cover_letter": candidate_data.get("cover_letter"),
                    "resume_text": candidate_data.get("resume_text"),
                    "preferred_salary": candidate_data.get("preferred_salary"),
                    "availability": candidate_data.get("availability"),
                    "remote_preference": candidate_data.get("remote_preference", "hybrid")
                }
                
                # Create candidate via API
                response = requests.post(
                    f"{API_BASE_URL}/api/candidates/",
                    data=form_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    candidate_id = result["candidate_id"]
                    self.candidates.append({
                        "id": candidate_id,
                        "name": candidate_data["name"],
                        "position": candidate_data["position"],
                        "email": candidate_data["email"]
                    })
                    print(f"   ✅ Created: {candidate_data['name']} (ID: {candidate_id[:8]}...)")
                else:
                    print(f"   ❌ Failed to create {candidate_data['name']}: {response.text}")
                
                # Small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error creating {candidate_data['name']}: {e}")
        
        print(f"\n   📊 Total candidates created: {len(self.candidates)}")
    
    async def wait_for_ai_analysis(self):
        """Wait for AI analysis to complete for all candidates"""
        
        print("\n🤖 Step 3: Waiting for AI Analysis Completion")
        print("-" * 40)
        
        max_wait_time = 180  # 3 minutes
        check_interval = 5   # 5 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            completed_count = 0
            
            for candidate in self.candidates:
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/api/candidates/{candidate['id']}/analysis",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        analysis_data = response.json()
                        
                        if analysis_data.get("status") == "completed":
                            completed_count += 1
                            
                            if not candidate.get("analysis_completed"):
                                candidate["analysis_completed"] = True
                                overall_score = analysis_data.get("overall_score", 0)
                                print(f"   ✅ {candidate['name']}: Analysis completed (Score: {overall_score}/100)")
                
                except Exception as e:
                    logger.error(f"Error checking analysis for {candidate['name']}: {e}")
            
            if completed_count == len(self.candidates):
                print(f"\n   🎯 All {len(self.candidates)} candidates analyzed successfully!")
                break
            
            remaining = len(self.candidates) - completed_count
            elapsed = int(time.time() - start_time)
            print(f"   ⏳ {remaining} analyses remaining... ({elapsed}s elapsed)")
            
            await asyncio.sleep(check_interval)
        
        if completed_count < len(self.candidates):
            print(f"   ⚠️ Only {completed_count}/{len(self.candidates)} analyses completed within timeout")
    
    async def schedule_interviews(self):
        """Schedule interviews for all analyzed candidates"""
        
        print("\n🗓️ Step 4: Scheduling Interviews")
        print("-" * 40)
        
        # Schedule interviews starting from tomorrow
        base_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        for i, candidate in enumerate(self.candidates):
            try:
                # Schedule interview at different times to avoid conflicts
                interview_time = base_time + timedelta(hours=i * 2)
                
                # Determine interview type based on position
                interview_type = "technical"
                if "frontend" in candidate['position'].lower():
                    interview_type = "technical"
                elif "devops" in candidate['position'].lower():
                    interview_type = "system_design"
                elif "senior" in candidate['position'].lower():
                    interview_type = "technical"
                
                # Create interview request
                interview_request = {
                    "candidate_id": candidate["id"],
                    "preferred_time": interview_time.isoformat(),
                    "duration_minutes": 90,
                    "interview_type": interview_type,
                    "interview_round": 1,
                    "is_remote": True,
                    "additional_attendees": ["hr@company.com"],
                    "notes": f"Technical interview for {candidate['position']} position"
                }
                
                print(f"\n   🔄 Scheduling interview for {candidate['name']}...")
                print(f"      Position: {candidate['position']}")
                print(f"      Time: {interview_time.strftime('%A, %B %d at %I:%M %p')}")
                print(f"      Type: {interview_type.title()}")
                
                # Schedule interview via API
                response = requests.post(
                    f"{API_BASE_URL}/api/schedule-interview/",
                    json=interview_request,
                    headers=HEADERS,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    interview_data = result["interview"]
                    
                    self.interviews.append({
                        "id": interview_data["interview_id"],
                        "candidate_name": candidate["name"],
                        "interviewer_name": interview_data["interviewer_name"],
                        "scheduled_time": interview_time,
                        "interview_type": interview_type,
                        "match_score": interview_data["ai_match_score"],
                        "status": "scheduled"
                    })
                    
                    print(f"      ✅ Interview scheduled successfully!")
                    print(f"      👨‍💼 Interviewer: {interview_data['interviewer_name']}")
                    print(f"      📊 AI Match Score: {interview_data['ai_match_score']:.1f}/100")
                    print(f"      🎯 Confidence: {interview_data['ai_match_confidence']:.1f}")
                    print(f"      🆔 Interview ID: {interview_data['interview_id'][:8]}...")
                    
                else:
                    print(f"      ❌ Failed to schedule interview: {response.text}")
                
                # Delay between scheduling requests
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"      ❌ Error scheduling interview for {candidate['name']}: {e}")
        
        print(f"\n   📈 Total interviews scheduled: {len(self.interviews)}")
    
    async def monitor_interview_status(self):
        """Monitor the status of scheduled interviews including calendar events"""
        
        print("\n📊 Step 5: Monitoring Interview Status")
        print("-" * 40)
        
        max_wait_time = 120  # 2 minutes
        check_interval = 10  # 10 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            calendar_events_created = 0
            
            for interview in self.interviews:
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/api/interviews/{interview['id']}/status",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        
                        if status_data.get("calendar_event_created"):
                            calendar_events_created += 1
                            
                            if not interview.get("calendar_checked"):
                                interview["calendar_checked"] = True
                                interview["google_meet_link"] = status_data.get("google_meet_link")
                                
                                print(f"   ✅ {interview['candidate_name']}: Calendar event created")
                                if status_data.get("google_meet_link"):
                                    print(f"      🎥 Google Meet link generated")
                                print(f"      📧 Email invitations sent")
                
                except Exception as e:
                    logger.error(f"Error checking interview status: {e}")
            
            if calendar_events_created == len(self.interviews):
                print(f"\n   🎯 All {len(self.interviews)} calendar events created!")
                break
            
            remaining = len(self.interviews) - calendar_events_created
            elapsed = int(time.time() - start_time)
            print(f"   ⏳ {remaining} calendar events pending... ({elapsed}s elapsed)")
            
            await asyncio.sleep(check_interval)
        
        if calendar_events_created < len(self.interviews):
            print(f"   ⚠️ Only {calendar_events_created}/{len(self.interviews)} calendar events created within timeout")
    
    async def show_final_results(self):
        """Display comprehensive results of the interview scheduling demo"""
        
        print("\n📋 Step 6: Final Results Summary")
        print("=" * 60)
        
        # Candidate Summary
        print("\n👥 CANDIDATES CREATED:")
        print("-" * 30)
        for candidate in self.candidates:
            status = "✅ Analyzed" if candidate.get("analysis_completed") else "⏳ Pending"
            print(f"   {status} {candidate['name']} ({candidate['position']})")
        
        # Interview Summary
        print(f"\n🗓️ INTERVIEWS SCHEDULED:")
        print("-" * 30)
        for interview in self.interviews:
            calendar_status = "📅 Calendar Created" if interview.get("calendar_checked") else "⏳ Pending"
            time_str = interview['scheduled_time'].strftime('%m/%d %I:%M %p')
            
            print(f"   {calendar_status}")
            print(f"      👤 Candidate: {interview['candidate_name']}")
            print(f"      👨‍💼 Interviewer: {interview['interviewer_name']}")
            print(f"      📊 Match Score: {interview['match_score']:.1f}/100")
            print(f"      🕒 Time: {time_str}")
            print(f"      🎯 Type: {interview['interview_type'].title()}")
            if interview.get("google_meet_link"):
                print(f"      🎥 Google Meet: Ready")
            print()
        
        # Statistics
        print("📊 STATISTICS:")
        print("-" * 30)
        print(f"   📝 Candidates Created: {len(self.candidates)}")
        print(f"   🤖 AI Analyses Completed: {sum(1 for c in self.candidates if c.get('analysis_completed'))}")
        print(f"   🗓️ Interviews Scheduled: {len(self.interviews)}")
        print(f"   📅 Calendar Events Created: {sum(1 for i in self.interviews if i.get('calendar_checked'))}")
        
        if self.interviews:
            avg_match_score = sum(i['match_score'] for i in self.interviews) / len(self.interviews)
            print(f"   📈 Average Match Score: {avg_match_score:.1f}/100")
        
        # Next Steps
        print(f"\n🚀 NEXT STEPS:")
        print("-" * 30)
        print("   1. 📧 Check email inboxes for calendar invitations")
        print("   2. 🎥 Google Meet links are ready for interviews")
        print("   3. ⏰ Automatic reminders will be sent before interviews")
        print("   4. 📱 Interviewers can access candidate profiles via API")
        print("   5. 📊 Interview feedback can be submitted after completion")
        
        # API Endpoints
        print(f"\n🔗 USEFUL API ENDPOINTS:")
        print("-" * 30)
        print(f"   📖 API Documentation: {API_BASE_URL}/docs")
        print(f"   👥 List Candidates: GET {API_BASE_URL}/api/candidates/")
        print(f"   🗓️ List Interviews: GET {API_BASE_URL}/api/interviews/")
        print(f"   📊 Interview Status: GET {API_BASE_URL}/api/interviews/{{id}}/status")


async def main():
    """Main demo function"""
    
    print("🎯 Complete Interview Scheduling System Demo")
    print("=" * 60)
    print("This demo demonstrates the full interview scheduling workflow:")
    print("  • ✅ Candidate creation and management")
    print("  • 🤖 AI-powered candidate analysis")
    print("  • 🎯 Smart interviewer matching")
    print("  • 🗓️ Automated interview scheduling")
    print("  • 📅 Google Calendar integration")
    print("  • 🎥 Google Meet link generation")
    print("  • 📧 Automated email notifications")
    print()
    
    demo = InterviewSchedulingDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Check if we're in an existing event loop
    try:
        loop = asyncio.get_running_loop()
        print("⚠️ Running in existing event loop - creating task")
        loop.create_task(main())
    except RuntimeError:
        # No existing loop, run normally
        asyncio.run(main())
