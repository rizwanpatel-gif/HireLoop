"""
Automatic Interview Scheduling Demo
===================================

Comprehensive demonstration of the new automatic interview scheduling system that:
1. Checks interviewer availability in Google Calendar
2. Creates interview database record with all details
3. Generates Google Calendar event with meeting link  
4. Sends confirmation notifications to both parties
5. Updates interview record with Google event ID

This demo shows the complete end-to-end automation process.
"""

import asyncio
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import system components
from automatic_interview_scheduler import (
    AutomaticInterviewScheduler, 
    schedule_interview_with_automation,
    SchedulingResult,
    SchedulingStatus
)
from interview_scheduling_api import (
    InterviewScheduleRequest, 
    InterviewType,
    schedule_interview_endpoint
)
from candidate_management_api import (
    CandidateDB, 
    CandidateCreate,
    get_db,
    SessionLocal
)
from database_setup import init_database
import requests
import time

class AutomaticSchedulingDemo:
    """Demo class for automatic interview scheduling"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.db = SessionLocal()
        self.scheduler = AutomaticInterviewScheduler()
        
    async def run_comprehensive_demo(self):
        """Run complete automatic scheduling demonstration"""
        
        print("🚀 Automatic Interview Scheduling System Demo")
        print("=" * 60)
        print()
        
        try:
            # Step 1: Check system health
            await self._check_system_health()
            
            # Step 2: Create test candidates
            candidates = await self._create_test_candidates()
            
            # Step 3: Wait for AI analysis (if needed)
            await self._ensure_ai_analysis_complete(candidates)
            
            # Step 4: Demonstrate automatic scheduling
            await self._demonstrate_automatic_scheduling(candidates)
            
            # Step 5: Show final results
            await self._show_final_results()
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"❌ Demo failed: {e}")
        
        finally:
            self.db.close()
    
    async def _check_system_health(self):
        """Check if the API system is running and accessible"""
        print("🔍 Step 1: Checking System Health")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ API server is running and accessible")
                print(f"   📖 Documentation: {self.base_url}/docs")
                print(f"   🗓️ Interview Scheduling: {self.base_url}/api/schedule-interview/")
            else:
                print(f"   ⚠️ API server returned status: {response.status_code}")
        except requests.exceptions.RequestException:
            print("   ❌ API server is not accessible")
            print("   💡 Please start the server with: python candidate_management_api.py")
            sys.exit(1)
        
        print()
    
    async def _create_test_candidates(self) -> List[Dict[str, Any]]:
        """Create test candidates for scheduling demo"""
        print("📝 Step 2: Creating Test Candidates for Automatic Scheduling")
        print("-" * 60)
        
        test_candidates = [
            {
                "name": "Alex Thompson",
                "email": "alex.thompson@demo.com",
                "position": "Senior Backend Engineer",
                "experience_years": 7.0,
                "skills": [
                    {"name": "Python", "level": "expert", "years_experience": 7.0},
                    {"name": "Django", "level": "advanced", "years_experience": 5.0},
                    {"name": "PostgreSQL", "level": "advanced", "years_experience": 6.0},
                    {"name": "AWS", "level": "intermediate", "years_experience": 4.0},
                    {"name": "Docker", "level": "advanced", "years_experience": 3.0}
                ],
                "previous_companies": ["TechCorp", "StartupXYZ"],
                "interview_type": InterviewType.TECHNICAL
            },
            {
                "name": "Maria Garcia",
                "email": "maria.garcia@demo.com", 
                "position": "DevOps Lead",
                "experience_years": 8.0,
                "skills": [
                    {"name": "Kubernetes", "level": "expert", "years_experience": 5.0},
                    {"name": "Terraform", "level": "advanced", "years_experience": 4.0},
                    {"name": "AWS", "level": "expert", "years_experience": 8.0},
                    {"name": "Jenkins", "level": "advanced", "years_experience": 6.0},
                    {"name": "Monitoring", "level": "expert", "years_experience": 7.0}
                ],
                "previous_companies": ["CloudTech", "BigCorp"],
                "interview_type": InterviewType.TECHNICAL
            },
            {
                "name": "David Chen",
                "email": "david.chen@demo.com",
                "position": "Frontend Developer",
                "experience_years": 4.0,
                "skills": [
                    {"name": "React", "level": "expert", "years_experience": 4.0},
                    {"name": "TypeScript", "level": "advanced", "years_experience": 3.0},
                    {"name": "Next.js", "level": "intermediate", "years_experience": 2.0},
                    {"name": "CSS", "level": "expert", "years_experience": 4.0},
                    {"name": "Node.js", "level": "intermediate", "years_experience": 2.0}
                ],
                "previous_companies": ["WebStudio", "DesignCorp"],
                "interview_type": InterviewType.TECHNICAL
            }
        ]
        
        created_candidates = []
        
        for candidate_data in test_candidates:
            try:
                # Create candidate via API
                candidate_payload = {
                    "name": candidate_data["name"],
                    "email": candidate_data["email"],
                    "position": candidate_data["position"],
                    "experience_years": candidate_data["experience_years"],
                    "skills": json.dumps(candidate_data["skills"]),
                    "previous_companies": json.dumps(candidate_data["previous_companies"])
                }
                
                response = requests.post(
                    f"{self.base_url}/api/candidates/",
                    data=candidate_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    candidate_id = result["candidate_id"]
                    
                    created_candidates.append({
                        "id": candidate_id,
                        "name": candidate_data["name"],
                        "position": candidate_data["position"],
                        "interview_type": candidate_data["interview_type"],
                        "data": candidate_data
                    })
                    
                    print(f"   ✅ Created: {candidate_data['name']} (ID: {candidate_id[:8]}...)")
                else:
                    print(f"   ❌ Failed to create {candidate_data['name']}: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error creating {candidate_data['name']}: {e}")
        
        print(f"\n   📊 Successfully created {len(created_candidates)} test candidates")
        print()
        return created_candidates
    
    async def _ensure_ai_analysis_complete(self, candidates: List[Dict[str, Any]]):
        """Ensure AI analysis is complete for all candidates"""
        print("🤖 Step 3: Ensuring AI Analysis Completion")
        print("-" * 45)
        
        for candidate in candidates:
            candidate_id = candidate["id"]
            name = candidate["name"]
            
            print(f"   🔄 Checking AI analysis for {name}...")
            
            # Check analysis status
            max_attempts = 12  # Wait up to 2 minutes
            for attempt in range(max_attempts):
                try:
                    response = requests.get(
                        f"{self.base_url}/api/candidates/{candidate_id}/analysis",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        analysis = response.json()
                        
                        if analysis["status"] == "completed":
                            score = analysis.get("overall_score", 0)
                            print(f"   ✅ {name}: Analysis completed (Score: {score}/100)")
                            break
                        elif analysis["status"] == "failed":
                            print(f"   ❌ {name}: Analysis failed")
                            break
                        else:
                            if attempt < max_attempts - 1:
                                print(f"   ⏳ {name}: Analysis in progress... (attempt {attempt + 1})")
                                await asyncio.sleep(10)
                            else:
                                print(f"   ⚠️ {name}: Analysis timeout - proceeding with basic matching")
                    else:
                        print(f"   ⚠️ {name}: Could not check analysis status")
                        break
                        
                except Exception as e:
                    print(f"   ❌ {name}: Error checking analysis: {e}")
                    break
        
        print()
    
    async def _demonstrate_automatic_scheduling(self, candidates: List[Dict[str, Any]]):
        """Demonstrate the automatic interview scheduling for each candidate"""
        print("🗓️ Step 4: Demonstrating Automatic Interview Scheduling")
        print("-" * 60)
        
        # Schedule interviews for each candidate
        for i, candidate in enumerate(candidates):
            candidate_id = candidate["id"]
            name = candidate["name"]
            position = candidate["position"]
            interview_type = candidate["interview_type"]
            
            print(f"\\n   🔄 Scheduling automatic interview for {name}...")
            print(f"      Position: {position}")
            print(f"      Type: {interview_type.value.title()}")
            
            # Calculate interview time (next week, different times)
            base_time = datetime.now() + timedelta(days=7 + i)  # Spread over next week
            interview_time = base_time.replace(hour=14 + i, minute=0, second=0, microsecond=0)
            
            print(f"      Preferred Time: {interview_time.strftime('%A, %B %d at %I:%M %p')}")
            
            try:
                # Create scheduling request
                request = InterviewScheduleRequest(
                    candidate_id=candidate_id,
                    preferred_time=interview_time,
                    duration_minutes=90,
                    interview_type=interview_type,
                    interview_round=1,
                    is_remote=True,
                    additional_attendees=["hr@company.com"],
                    notes=f"Automatic scheduling demo for {position} position"
                )
                
                # Use the automatic scheduler
                print(f"      🤖 Running automatic scheduling process...")
                scheduling_result = await schedule_interview_with_automation(request, self.db)
                
                if scheduling_result.success:
                    interviewer = scheduling_result.interviewer_selected
                    print(f"      ✅ Interview scheduled successfully!")
                    print(f"         👨‍💼 Interviewer: {interviewer['name']}")
                    print(f"         📊 AI Match Score: {interviewer['match_score']:.1f}/100")
                    print(f"         🎯 Confidence: {interviewer['confidence']:.1f}")
                    print(f"         📅 Calendar Event: {scheduling_result.calendar_event_id or 'Failed'}")
                    print(f"         🎥 Google Meet: {'Generated' if scheduling_result.google_meet_link else 'Failed'}")
                    print(f"         📧 Notifications: {'Sent' if scheduling_result.notifications_sent else 'Failed'}")
                    print(f"         ⚡ Automation Status: {scheduling_result.status}")
                    
                    # Add scheduling result to candidate for final summary
                    candidate["scheduling_result"] = scheduling_result
                    
                else:
                    print(f"      ❌ Automatic scheduling failed:")
                    print(f"         Error: {scheduling_result.message}")
                    for error in scheduling_result.errors:
                        print(f"         • {error}")
                    
                    candidate["scheduling_result"] = scheduling_result
                
            except Exception as e:
                print(f"      ❌ Scheduling error: {e}")
                logger.exception(f"Error scheduling interview for {name}")
        
        print()
    
    async def _show_final_results(self):
        """Show comprehensive final results of automatic scheduling"""
        print("📊 Step 5: Final Automatic Scheduling Results")
        print("=" * 60)
        
        # Get all interviews from database
        from interview_scheduling_api import InterviewDB
        interviews = self.db.query(InterviewDB).order_by(InterviewDB.created_at.desc()).limit(10).all()
        
        if interviews:
            print("\\n🗓️ AUTOMATICALLY SCHEDULED INTERVIEWS:")
            print("-" * 50)
            
            successful_schedules = 0
            total_automation_score = 0
            
            for interview in interviews:
                candidate = self.db.query(CandidateDB).filter(CandidateDB.id == interview.candidate_id).first()
                
                # Determine automation success level
                automation_features = []
                if interview.calendar_event_id:
                    automation_features.append("📅 Calendar Created")
                if interview.google_meet_link:
                    automation_features.append("🎥 Google Meet")
                if interview.calendar_invites_sent:
                    automation_features.append("📧 Notifications Sent")
                if interview.ai_match_score:
                    automation_features.append(f"🤖 AI Matched ({interview.ai_match_score:.1f}/100)")
                
                automation_score = len(automation_features)
                total_automation_score += automation_score
                
                if automation_score >= 3:
                    successful_schedules += 1
                    status_icon = "✅"
                else:
                    status_icon = "⚠️"
                
                print(f"   {status_icon} {candidate.name if candidate else 'Unknown'}")
                print(f"      👤 Position: {interview.position}")
                print(f"      👨‍💼 Interviewer: {interview.interviewer_name}")
                print(f"      🕒 Time: {interview.scheduled_time.strftime('%m/%d %I:%M %p')}")
                print(f"      🎯 Type: {interview.interview_type.title()}")
                print(f"      ⚡ Automation: {' • '.join(automation_features)}")
                print(f"      📊 Status: {interview.status}")
                print()
            
            # Summary statistics
            print("📈 AUTOMATION SUMMARY:")
            print("-" * 30)
            print(f"   📊 Total Interviews Scheduled: {len(interviews)}")
            print(f"   ✅ Fully Automated: {successful_schedules}")
            print(f"   📧 Average Automation Score: {total_automation_score/len(interviews):.1f}/4")
            print(f"   🎯 Success Rate: {(successful_schedules/len(interviews)*100):.1f}%")
            
            # Feature breakdown
            calendar_events = sum(1 for i in interviews if i.calendar_event_id)
            meet_links = sum(1 for i in interviews if i.google_meet_link)
            notifications = sum(1 for i in interviews if i.calendar_invites_sent)
            ai_matches = sum(1 for i in interviews if i.ai_match_score and i.ai_match_score > 0)
            
            print("\\n🔧 AUTOMATION FEATURES:")
            print("-" * 30)
            print(f"   📅 Calendar Events Created: {calendar_events}/{len(interviews)}")
            print(f"   🎥 Google Meet Links: {meet_links}/{len(interviews)}")
            print(f"   📧 Email Notifications: {notifications}/{len(interviews)}")
            print(f"   🤖 AI Interviewer Matching: {ai_matches}/{len(interviews)}")
            
        else:
            print("   📭 No interviews found in database")
        
        print("\\n🎉 Automatic Interview Scheduling Demo Complete!")
        print("=" * 60)
        print("\\n💡 Key Features Demonstrated:")
        print("   ✅ Real-time interviewer availability checking")
        print("   ✅ AI-powered interviewer matching with confidence scores")  
        print("   ✅ Comprehensive database record creation")
        print("   ✅ Automatic Google Calendar event generation")
        print("   ✅ Google Meet link creation and sharing")
        print("   ✅ Email notifications to all participants")
        print("   ✅ Interview status tracking and updates")
        print("   ✅ Error handling and retry mechanisms")
        print("\\n📚 Next Steps:")
        print("   • Review generated calendar events in Google Calendar")
        print("   • Check email confirmations sent to participants")
        print("   • Monitor interview status updates in the system")
        print("   • Test rescheduling and cancellation workflows")

# Demo execution functions
async def run_demo():
    """Run the automatic scheduling demo"""
    demo = AutomaticSchedulingDemo()
    await demo.run_comprehensive_demo()

def main():
    """Main entry point for demo"""
    print("🚀 Starting Automatic Interview Scheduling Demo...")
    print("   This demo showcases the complete automation features:")
    print("   • Interviewer availability checking")
    print("   • AI-powered matching")
    print("   • Calendar event creation")
    print("   • Email notifications")
    print("   • Database record management")
    print()
    
    try:
        # Initialize database
        init_database()
        
        # Run demo
        asyncio.run(run_demo())
        
    except KeyboardInterrupt:
        print("\\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demo failed: {e}")
        logger.exception("Demo error details")

if __name__ == "__main__":
    main()
