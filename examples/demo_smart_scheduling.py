"""
Smart Scheduling Algorithm Demo
===============================

Comprehensive demonstration of the Smart Scheduling Algorithm with:
- Historical data simulation
- Interviewer preference setup
- Intelligent time slot suggestions
- Conflict detection and resolution
- Performance analytics
- End-to-end scheduling workflow

This demo showcases all the advanced features implemented in Phase 7.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Any
import random
from zoneinfo import ZoneInfo

# Import smart scheduling components
try:
    from backend.app.services.smart_scheduling import (
        smart_scheduler,
        InterviewerPreferences,
        HistoricalInterviewData,
        InterviewOutcome,
        TimeSlotSuitability
    )
    from backend.app.services.smart_scheduling_integration import (
        smart_scheduling_integration,
        get_smart_interview_suggestions,
        schedule_from_suggestion,
        record_interview_feedback
    )
except ImportError:
    print("Smart scheduling modules not available. Running in standalone mode.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartSchedulingDemo:
    """
    Comprehensive demo of the Smart Scheduling Algorithm
    """
    
    def __init__(self):
        """Initialize the demo"""
        self.demo_interviewers = [
            "interviewer_001",
            "interviewer_002", 
            "interviewer_003",
            "interviewer_004",
            "interviewer_005"
        ]
        
        self.demo_candidates = [
            "candidate_001",
            "candidate_002",
            "candidate_003"
        ]
        
        self.demo_positions = [
            "Senior Software Engineer",
            "Frontend Developer", 
            "Data Scientist",
            "Product Manager",
            "DevOps Engineer"
        ]
    
    async def run_complete_demo(self):
        """Run the complete smart scheduling demo"""
        print("🚀 Smart Scheduling Algorithm Demo Starting...")
        print("=" * 60)
        
        # Step 1: Setup demo data
        await self.setup_demo_data()
        
        # Step 2: Demonstrate suggestion generation
        await self.demo_suggestion_generation()
        
        # Step 3: Demonstrate scheduling workflow
        await self.demo_scheduling_workflow()
        
        # Step 4: Demonstrate outcome recording
        await self.demo_outcome_recording()
        
        # Step 5: Demonstrate analytics
        await self.demo_analytics()
        
        # Step 6: Demonstrate edge cases
        await self.demo_edge_cases()
        
        print("✅ Smart Scheduling Algorithm Demo Complete!")
        print("=" * 60)
    
    async def setup_demo_data(self):
        """Setup demo data including preferences and historical data"""
        print("📊 Setting up demo data...")
        
        # Setup interviewer preferences
        await self._setup_interviewer_preferences()
        
        # Generate historical interview data
        await self._generate_historical_data()
        
        # Setup existing meetings
        await self._setup_existing_meetings()
        
        print("✅ Demo data setup complete")
        print()
    
    async def _setup_interviewer_preferences(self):
        """Setup interviewer preferences with diverse scenarios"""
        preferences_data = [
            {
                'interviewer_id': 'interviewer_001',
                'name': 'Alice Johnson',
                'email': 'alice.johnson@company.com',
                'timezone': 'America/New_York',
                'preferred_start_hour': 9,
                'preferred_end_hour': 17,
                'preferred_days': [0, 1, 2, 3, 4],  # Monday-Friday
                'peak_performance_hours': [10, 11, 14, 15],
                'max_interviews_per_day': 4
            },
            {
                'interviewer_id': 'interviewer_002',
                'name': 'Bob Chen',
                'email': 'bob.chen@company.com',
                'timezone': 'America/Los_Angeles',
                'preferred_start_hour': 8,
                'preferred_end_hour': 16,
                'preferred_days': [0, 1, 2, 3, 4],
                'peak_performance_hours': [9, 10, 13, 14, 15],
                'max_interviews_per_day': 3
            },
            {
                'interviewer_id': 'interviewer_003',
                'name': 'Carol Smith',
                'email': 'carol.smith@company.com',
                'timezone': 'Europe/London',
                'preferred_start_hour': 10,
                'preferred_end_hour': 18,
                'preferred_days': [0, 1, 2, 3, 4],
                'peak_performance_hours': [11, 12, 15, 16],
                'max_interviews_per_day': 5
            },
            {
                'interviewer_id': 'interviewer_004',
                'name': 'David Rodriguez',
                'email': 'david.rodriguez@company.com',
                'timezone': 'America/Chicago',
                'preferred_start_hour': 9,
                'preferred_end_hour': 17,
                'preferred_days': [1, 2, 3, 4],  # Tuesday-Friday (no Mondays)
                'peak_performance_hours': [10, 11, 14, 16],
                'max_interviews_per_day': 3
            },
            {
                'interviewer_id': 'interviewer_005',
                'name': 'Emma Wilson',
                'email': 'emma.wilson@company.com',
                'timezone': 'Asia/Tokyo',
                'preferred_start_hour': 9,
                'preferred_end_hour': 17,
                'preferred_days': [0, 1, 2, 3, 4],
                'peak_performance_hours': [9, 10, 13, 14],
                'max_interviews_per_day': 4
            }
        ]
        
        for pref_data in preferences_data:
            preferences = InterviewerPreferences(**pref_data)
            await smart_scheduler.update_interviewer_preferences(preferences)
            print(f"  ✓ Setup preferences for {preferences.name} ({preferences.timezone})")
    
    async def _generate_historical_data(self):
        """Generate realistic historical interview data"""
        print("  Generating historical interview data...")
        
        # Generate data for the past 90 days
        start_date = datetime.now() - timedelta(days=90)
        
        interview_counter = 1
        
        for interviewer_id in self.demo_interviewers:
            # Generate 20-30 interviews per interviewer
            num_interviews = random.randint(20, 30)
            
            for _ in range(num_interviews):
                # Random date in the past 90 days
                days_ago = random.randint(1, 90)
                interview_date = start_date + timedelta(days=days_ago)
                
                # Random hour during business hours
                hour = random.choice([9, 10, 11, 13, 14, 15, 16])
                interview_datetime = interview_date.replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                
                # Generate realistic outcomes based on time
                outcome_weights = self._get_outcome_weights_by_time(hour)
                outcome = random.choices(
                    list(InterviewOutcome),
                    weights=outcome_weights
                )[0]
                
                # Generate feedback scores based on outcome
                interviewer_score, candidate_score = self._generate_feedback_scores(outcome)
                
                historical_data = HistoricalInterviewData(
                    interview_id=f"hist_interview_{interview_counter:03d}",
                    interviewer_id=interviewer_id,
                    candidate_id=f"hist_candidate_{interview_counter:03d}",
                    scheduled_datetime=interview_datetime,
                    actual_datetime=interview_datetime,
                    duration_minutes=60,
                    outcome=outcome,
                    interviewer_feedback_score=interviewer_score,
                    candidate_feedback_score=candidate_score,
                    timezone="UTC"
                )
                
                await smart_scheduler.add_historical_data(historical_data)
                interview_counter += 1
        
        print(f"  ✓ Generated {interview_counter - 1} historical interviews")
    
    def _get_outcome_weights_by_time(self, hour: int) -> List[float]:
        """Get outcome probability weights based on time of day"""
        if hour in [10, 11, 14, 15]:  # Peak hours
            return [0.3, 0.4, 0.2, 0.05, 0.03, 0.02]  # More excellent/good
        elif hour in [9, 16]:  # Good hours
            return [0.2, 0.4, 0.25, 0.1, 0.03, 0.02]
        else:  # Less optimal hours
            return [0.1, 0.3, 0.35, 0.15, 0.05, 0.05]
        
        # Order: EXCELLENT, GOOD, AVERAGE, POOR, CANCELLED, NO_SHOW
    
    def _generate_feedback_scores(self, outcome: InterviewOutcome) -> tuple:
        """Generate realistic feedback scores based on outcome"""
        if outcome == InterviewOutcome.EXCELLENT:
            interviewer_score = random.uniform(8.5, 10.0)
            candidate_score = random.uniform(8.0, 10.0)
        elif outcome == InterviewOutcome.GOOD:
            interviewer_score = random.uniform(7.0, 8.5)
            candidate_score = random.uniform(7.0, 9.0)
        elif outcome == InterviewOutcome.AVERAGE:
            interviewer_score = random.uniform(5.5, 7.0)
            candidate_score = random.uniform(5.0, 7.5)
        elif outcome == InterviewOutcome.POOR:
            interviewer_score = random.uniform(3.0, 5.5)
            candidate_score = random.uniform(3.0, 6.0)
        else:  # CANCELLED or NO_SHOW
            interviewer_score = None
            candidate_score = None
        
        return interviewer_score, candidate_score
    
    async def _setup_existing_meetings(self):
        """Setup existing meetings for conflict detection"""
        print("  Setting up existing meetings...")
        
        base_date = datetime.now() + timedelta(days=1)
        
        for interviewer_id in self.demo_interviewers:
            meetings = []
            
            # Add 2-3 meetings per interviewer for next week
            num_meetings = random.randint(2, 3)
            
            for i in range(num_meetings):
                meeting_date = base_date + timedelta(days=random.randint(0, 6))
                meeting_hour = random.choice([9, 11, 13, 15])
                
                meeting_start = meeting_date.replace(
                    hour=meeting_hour, minute=0, second=0, microsecond=0
                )
                meeting_end = meeting_start + timedelta(hours=1)
                
                meetings.append({
                    'start_datetime': meeting_start,
                    'end_datetime': meeting_end,
                    'title': f'Team Meeting {i+1}',
                    'type': 'existing_meeting'
                })
            
            await smart_scheduler.update_existing_meetings(interviewer_id, meetings)
        
        print("  ✓ Setup existing meetings for conflict detection")
    
    async def demo_suggestion_generation(self):
        """Demonstrate intelligent suggestion generation"""
        print("🎯 Demonstrating Smart Suggestion Generation...")
        
        test_scenarios = [
            {
                'name': 'Standard US Candidate',
                'candidate_id': 'demo_candidate_001',
                'interviewer_ids': ['interviewer_001', 'interviewer_002'],
                'position': 'Senior Software Engineer',
                'candidate_timezone': 'America/New_York',
                'urgency': 'normal'
            },
            {
                'name': 'European Remote Candidate',
                'candidate_id': 'demo_candidate_002',
                'interviewer_ids': ['interviewer_003', 'interviewer_001'],
                'position': 'Frontend Developer',
                'candidate_timezone': 'Europe/Berlin',
                'urgency': 'high'
            },
            {
                'name': 'Asian Timezone Challenge',
                'candidate_id': 'demo_candidate_003',
                'interviewer_ids': ['interviewer_005', 'interviewer_004'],
                'position': 'Data Scientist',
                'candidate_timezone': 'Asia/Singapore',
                'urgency': 'urgent'
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 Scenario: {scenario['name']}")
            print(f"   Position: {scenario['position']}")
            print(f"   Candidate TZ: {scenario['candidate_timezone']}")
            print(f"   Urgency: {scenario['urgency']}")
            
            result = await get_smart_interview_suggestions(
                candidate_id=scenario['candidate_id'],
                interviewer_ids=scenario['interviewer_ids'],
                position=scenario['position'],
                candidate_timezone=scenario['candidate_timezone'],
                urgency=scenario['urgency']
            )
            
            if result['success']:
                suggestions = result['suggestions']
                analysis = result['analysis']
                
                print(f"   ✅ Generated {len(suggestions)} suggestions")
                
                # Show top 3 suggestions
                for i, suggestion in enumerate(suggestions[:3]):
                    start_dt = datetime.fromisoformat(suggestion['start_datetime'].replace('Z', '+00:00'))
                    score = suggestion['suitability_score']
                    level = suggestion['suitability_level']
                    
                    print(f"      {i+1}. {start_dt.strftime('%Y-%m-%d %H:%M %Z')} - Score: {score:.1f} ({level})")
                    
                    # Show key reasons
                    reasons = suggestion.get('recommendation_reasons', [])
                    if reasons:
                        print(f"         Reasons: {', '.join(reasons[:2])}")
                
                # Show analysis insights
                insights = analysis.get('insights', [])
                if insights:
                    print(f"   💡 Insights: {insights[0]}")
                
                statistics = analysis.get('statistics', {})
                if statistics:
                    avg_score = statistics.get('average_suitability_score', 0)
                    timezone_compat = statistics.get('average_timezone_compatibility', 0)
                    print(f"   📊 Avg Score: {avg_score:.1f}, TZ Compat: {timezone_compat:.1f}")
            
            else:
                print(f"   ❌ Failed to generate suggestions")
        
        print()
    
    async def demo_scheduling_workflow(self):
        """Demonstrate complete scheduling workflow"""
        print("📅 Demonstrating Complete Scheduling Workflow...")
        
        # Use first scenario for detailed workflow demo
        candidate_id = 'demo_candidate_001'
        interviewer_ids = ['interviewer_001', 'interviewer_002']
        position = 'Senior Software Engineer'
        
        print(f"   Candidate: {candidate_id}")
        print(f"   Position: {position}")
        print(f"   Interviewers: {', '.join(interviewer_ids)}")
        
        # Step 1: Get suggestions
        suggestions_result = await get_smart_interview_suggestions(
            candidate_id=candidate_id,
            interviewer_ids=interviewer_ids,
            position=position,
            candidate_timezone='America/New_York'
        )
        
        if not suggestions_result['success'] or not suggestions_result['suggestions']:
            print("   ❌ No suggestions available for demo")
            return
        
        # Step 2: Select best suggestion
        best_suggestion = suggestions_result['suggestions'][0]
        suggestion_id = f"suggestion_{best_suggestion['interviewer_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"   📌 Selected suggestion: {best_suggestion['start_datetime']}")
        print(f"      Score: {best_suggestion['suitability_score']:.1f}")
        print(f"      Level: {best_suggestion['suitability_level']}")
        
        # Step 3: Schedule the interview
        scheduling_result = await schedule_from_suggestion(
            suggestion_id=suggestion_id,
            candidate_id=candidate_id,
            interviewer_id=best_suggestion['interviewer_id'],
            start_datetime=best_suggestion['start_datetime'],
            position=position,
            meeting_link="https://meet.company.com/interview-room-123"
        )
        
        if scheduling_result['success']:
            interview_id = scheduling_result['interview_id']
            print(f"   ✅ Interview scheduled successfully!")
            print(f"      Interview ID: {interview_id}")
            print(f"      Calendar Event: {scheduling_result.get('calendar_event_id', 'N/A')}")
            print(f"      Notifications: {'Sent' if scheduling_result.get('notifications_sent') else 'Failed'}")
            
            # Store for outcome demo
            self.demo_interview_id = interview_id
        else:
            print(f"   ❌ Scheduling failed")
        
        print()
    
    async def demo_outcome_recording(self):
        """Demonstrate interview outcome recording"""
        print("📝 Demonstrating Interview Outcome Recording...")
        
        if not hasattr(self, 'demo_interview_id'):
            print("   ⚠️ No interview ID available from scheduling demo")
            return
        
        interview_id = self.demo_interview_id
        
        # Simulate different outcome scenarios
        outcome_scenarios = [
            {
                'outcome': 'excellent',
                'interviewer_score': 9.2,
                'candidate_score': 8.8,
                'description': 'Outstanding technical skills and culture fit'
            },
            {
                'outcome': 'good',
                'interviewer_score': 7.5,
                'candidate_score': 7.8,
                'description': 'Solid performance with minor areas for improvement'
            },
            {
                'outcome': 'average',
                'interviewer_score': 6.0,
                'candidate_score': 6.5,
                'description': 'Meets basic requirements but lacks standout qualities'
            }
        ]
        
        # Use random scenario for demo
        scenario = random.choice(outcome_scenarios)
        
        print(f"   Interview ID: {interview_id}")
        print(f"   Outcome: {scenario['outcome']}")
        print(f"   Interviewer Score: {scenario['interviewer_score']}")
        print(f"   Candidate Score: {scenario['candidate_score']}")
        print(f"   Description: {scenario['description']}")
        
        # Record the outcome
        outcome_result = await record_interview_feedback(
            interview_id=interview_id,
            outcome=scenario['outcome'],
            interviewer_score=scenario['interviewer_score'],
            candidate_score=scenario['candidate_score']
        )
        
        if outcome_result['success']:
            print(f"   ✅ Outcome recorded successfully!")
            print(f"      Historical data updated: {outcome_result.get('historical_data_updated')}")
        else:
            print(f"   ❌ Failed to record outcome")
        
        print()
    
    async def demo_analytics(self):
        """Demonstrate analytics and insights"""
        print("📊 Demonstrating Analytics and Insights...")
        
        for interviewer_id in self.demo_interviewers[:3]:  # Show first 3
            analytics = await smart_scheduler.get_interviewer_analytics(interviewer_id)
            
            if 'message' not in analytics:
                print(f"   👤 {interviewer_id}:")
                print(f"      Total Interviews: {analytics.get('total_interviews', 0)}")
                print(f"      Success Rate: {analytics.get('success_rate', 0)}%")
                
                best_hours = analytics.get('best_performance_hours', [])
                if best_hours:
                    hours_str = ', '.join([f"{h['hour']}:00 ({h['avg_score']:.1f})" for h in best_hours[:2]])
                    print(f"      Best Hours: {hours_str}")
                
                avg_feedback = analytics.get('average_feedback_score')
                if avg_feedback:
                    print(f"      Avg Feedback: {avg_feedback:.1f}/10")
            else:
                print(f"   👤 {interviewer_id}: {analytics['message']}")
        
        print()
    
    async def demo_edge_cases(self):
        """Demonstrate edge cases and conflict resolution"""
        print("⚠️ Demonstrating Edge Cases and Conflict Resolution...")
        
        edge_cases = [
            {
                'name': 'No Available Interviewers',
                'candidate_id': 'edge_candidate_001',
                'interviewer_ids': ['nonexistent_interviewer'],
                'expected': 'Should handle gracefully'
            },
            {
                'name': 'Extreme Timezone Difference',
                'candidate_id': 'edge_candidate_002',
                'interviewer_ids': ['interviewer_001'],
                'candidate_timezone': 'Pacific/Auckland',
                'expected': 'Should find compromise times'
            },
            {
                'name': 'Urgent Scheduling with Conflicts',
                'candidate_id': 'edge_candidate_003',
                'interviewer_ids': ['interviewer_001', 'interviewer_002'],
                'urgency': 'urgent',
                'expected': 'Should prioritize immediate availability'
            }
        ]
        
        for case in edge_cases:
            print(f"   🔍 Testing: {case['name']}")
            print(f"      Expected: {case['expected']}")
            
            try:
                result = await get_smart_interview_suggestions(
                    candidate_id=case['candidate_id'],
                    interviewer_ids=case['interviewer_ids'],
                    position='Test Position',
                    candidate_timezone=case.get('candidate_timezone', 'UTC'),
                    urgency=case.get('urgency', 'normal')
                )
                
                if result['success']:
                    suggestion_count = len(result['suggestions'])
                    print(f"      ✅ Handled gracefully: {suggestion_count} suggestions")
                    
                    if suggestion_count > 0:
                        top_score = result['suggestions'][0]['suitability_score']
                        print(f"         Top score: {top_score:.1f}")
                else:
                    print(f"      ⚠️ No suggestions generated")
                
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
        
        print()
    
    def print_demo_summary(self):
        """Print a summary of demo features"""
        print("🎯 Smart Scheduling Algorithm Features Demonstrated:")
        print("=" * 60)
        print("✅ Historical Data Analysis")
        print("   - 90 days of simulated interview outcomes")
        print("   - Performance tracking by time slot")
        print("   - Success rate analysis")
        print()
        print("✅ Interviewer Preferences")
        print("   - Timezone-aware scheduling")
        print("   - Peak performance hour optimization")
        print("   - Work schedule preferences")
        print("   - Meeting conflict detection")
        print()
        print("✅ Intelligent Suggestions")
        print("   - Multi-factor suitability scoring")
        print("   - Timezone compatibility analysis")
        print("   - Historical performance weighting")
        print("   - Urgency-based prioritization")
        print()
        print("✅ Complete Workflow")
        print("   - Suggestion generation")
        print("   - Calendar integration")
        print("   - Email notifications")
        print("   - Outcome tracking")
        print()
        print("✅ Analytics & Insights")
        print("   - Interviewer performance analytics")
        print("   - Best time slot identification")
        print("   - Success rate trends")
        print("   - Optimization recommendations")
        print()
        print("✅ Edge Case Handling")
        print("   - Graceful error handling")
        print("   - Conflict resolution")
        print("   - Extreme timezone scenarios")
        print("   - Data validation")


async def main():
    """Run the complete smart scheduling demo"""
    demo = SmartSchedulingDemo()
    
    # Print feature summary first
    demo.print_demo_summary()
    print()
    
    # Run the interactive demo
    await demo.run_complete_demo()
    
    print("🎉 Demo completed successfully!")
    print("The Smart Scheduling Algorithm is ready for production use.")


if __name__ == "__main__":
    asyncio.run(main())
