"""
Interview Dashboard Demo
=======================

Demonstrates the comprehensive interview dashboard with:
- GET /api/interviews/ endpoint with JOIN queries
- Complete candidate and interviewer details
- Interview status, timing, and meeting links
- Proper filtering and pagination
- Formatted response for frontend consumption
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class InterviewDashboardDemo:
    """Demo class for interview dashboard functionality"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    def run_dashboard_demo(self):
        """Run comprehensive dashboard demonstration"""
        
        print("📊 Interview Dashboard & Availability Demo")
        print("=" * 60)
        print()
        
        try:
            # Step 1: Check API health
            self._check_api_health()
            
            # Step 2: Test basic dashboard endpoint
            self._test_basic_dashboard()
            
            # Step 3: Test dashboard with filters
            self._test_dashboard_filters()
            
            # Step 4: Test pagination and sorting
            self._test_pagination_sorting()
            
            # Step 5: Test specific queries
            self._test_specific_queries()
            
            # Step 6: Show dashboard summary
            self._show_dashboard_summary()
            
        except Exception as e:
            print(f"❌ Dashboard demo failed: {e}")
    
    def _check_api_health(self):
        """Check if the API is running"""
        print("🔍 Step 1: Checking API Health")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ API server is running")
                print(f"   📖 Documentation: {self.base_url}/docs")
                print(f"   📊 Dashboard: {self.base_url}/api/interviews/")
            else:
                print(f"   ⚠️ API returned status: {response.status_code}")
        except requests.exceptions.RequestException:
            print("   ❌ API server not accessible")
            print("   💡 Start with: python candidate_management_api.py")
            return False
        
        print()
        return True
    
    def _test_basic_dashboard(self):
        """Test basic dashboard functionality"""
        print("📊 Step 2: Testing Basic Dashboard Endpoint")
        print("-" * 50)
        
        try:
            # Get basic dashboard data
            response = requests.get(f"{self.base_url}/api/interviews/")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Dashboard endpoint working")
                print(f"   📊 Total interviews: {data['total_count']}")
                print(f"   📄 Page: {data['page']}/{((data['total_count'] + data['page_size'] - 1) // data['page_size'])}")
                print(f"   📋 Items per page: {data['page_size']}")
                print(f"   📈 Interviews returned: {len(data['interviews'])}")
                
                # Show summary statistics
                summary = data.get('summary', {})
                print(f"   📊 Summary Statistics:")
                print(f"      🔮 Upcoming: {summary.get('upcoming_count', 0)}")
                print(f"      ✅ Completed: {summary.get('completed_count', 0)}")
                print(f"      🤖 Automation Rate: {summary.get('automation_rate', 0)}%")
                
                # Show some interview details
                if data['interviews']:
                    print(f"\\n   📋 Sample Interview Details:")
                    interview = data['interviews'][0]
                    print(f"      👤 Candidate: {interview['candidate_name']}")
                    print(f"      💼 Position: {interview['candidate_position']}")
                    print(f"      👨‍💼 Interviewer: {interview['interviewer_name']}")
                    print(f"      🕒 Scheduled: {interview['scheduled_time']}")
                    print(f"      📊 Status: {interview['status']} ({interview['status_color']})")
                    print(f"      🤖 AI Score: {interview.get('ai_match_score', 'N/A')}")
                    print(f"      ⚡ Automation: {interview['automation_score']}/4")
                    
                    if interview.get('time_until_interview'):
                        print(f"      ⏰ Timing: {interview['time_until_interview']}")
                    
                    if interview.get('google_meet_link'):
                        print(f"      🎥 Google Meet: Available")
                    
                    if interview.get('ai_recommended_focus_areas'):
                        focus = ', '.join(interview['ai_recommended_focus_areas'][:2])
                        print(f"      🎯 AI Focus: {focus}")
            else:
                print(f"   ❌ Dashboard request failed: {response.status_code}")
                print(f"      Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Dashboard test error: {e}")
        
        print()
    
    def _test_dashboard_filters(self):
        """Test dashboard filtering capabilities"""
        print("🔍 Step 3: Testing Dashboard Filters")
        print("-" * 40)
        
        filters_to_test = [
            {
                "name": "Upcoming Interviews",
                "params": {"is_upcoming": "true"},
                "description": "Show only future interviews"
            },
            {
                "name": "Technical Interviews",
                "params": {"interview_type": ["technical"]},
                "description": "Filter by interview type"
            },
            {
                "name": "Confirmed Status",
                "params": {"status": ["confirmed"]},
                "description": "Show only confirmed interviews"
            },
            {
                "name": "High Automation",
                "params": {},  # Will filter in response analysis
                "description": "Interviews with calendar events",
                "custom_filter": lambda i: i.get('calendar_event_id') is not None
            }
        ]
        
        for filter_test in filters_to_test:
            try:
                print(f"   🔍 Testing: {filter_test['name']}")
                print(f"      Description: {filter_test['description']}")
                
                # Make request with filters
                response = requests.get(
                    f"{self.base_url}/api/interviews/",
                    params=filter_test['params']
                )
                
                if response.status_code == 200:
                    data = response.json()
                    interviews = data['interviews']
                    
                    # Apply custom filter if specified
                    if 'custom_filter' in filter_test:
                        interviews = [i for i in interviews if filter_test['custom_filter'](i)]
                    
                    print(f"      ✅ Found: {len(interviews)} interviews")
                    
                    if interviews:
                        # Show sample results
                        sample = interviews[0]
                        print(f"      📋 Sample: {sample['candidate_name']} - {sample['status']}")
                        
                        if filter_test['name'] == "Upcoming Interviews":
                            print(f"         ⏰ {sample.get('time_until_interview', 'Timing unknown')}")
                        elif filter_test['name'] == "Technical Interviews":
                            print(f"         🎯 Type: {sample['interview_type']}")
                        elif filter_test['name'] == "Confirmed Status":
                            print(f"         ✅ Status: {sample['status']}")
                
                else:
                    print(f"      ❌ Filter test failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Filter error: {e}")
            
            print()
    
    def _test_pagination_sorting(self):
        """Test pagination and sorting features"""
        print("📄 Step 4: Testing Pagination & Sorting")
        print("-" * 45)
        
        sort_tests = [
            {
                "field": "scheduled_time",
                "order": "desc",
                "description": "Latest interviews first"
            },
            {
                "field": "candidate_name", 
                "order": "asc",
                "description": "Alphabetical by candidate"
            },
            {
                "field": "status",
                "order": "asc",
                "description": "Group by status"
            }
        ]
        
        for sort_test in sort_tests:
            try:
                print(f"   📊 Testing Sort: {sort_test['description']}")
                
                response = requests.get(
                    f"{self.base_url}/api/interviews/",
                    params={
                        "sort_field": sort_test['field'],
                        "sort_order": sort_test['order'],
                        "page_size": 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    interviews = data['interviews']
                    
                    print(f"      ✅ Sorted by {sort_test['field']} ({sort_test['order']})")
                    print(f"      📋 Results (showing {len(interviews)}):")
                    
                    for i, interview in enumerate(interviews[:3], 1):
                        if sort_test['field'] == 'scheduled_time':
                            value = interview['scheduled_time'][:16]  # Show date and time
                        elif sort_test['field'] == 'candidate_name':
                            value = interview['candidate_name']
                        elif sort_test['field'] == 'status':
                            value = interview['status']
                        else:
                            value = "N/A"
                        
                        print(f"         {i}. {interview['candidate_name']} - {value}")
                
                else:
                    print(f"      ❌ Sort test failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Sort error: {e}")
        
        print()
        
        # Test pagination
        try:
            print("   📄 Testing Pagination:")
            
            # Get page 1
            response1 = requests.get(
                f"{self.base_url}/api/interviews/",
                params={"page": 1, "page_size": 3}
            )
            
            # Get page 2
            response2 = requests.get(
                f"{self.base_url}/api/interviews/",
                params={"page": 2, "page_size": 3}
            )
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                print(f"      ✅ Page 1: {len(data1['interviews'])} interviews")
                print(f"      ✅ Page 2: {len(data2['interviews'])} interviews")
                print(f"      📊 Total: {data1['total_count']} interviews")
                
                # Check for different interviews
                ids1 = {i['interview_id'] for i in data1['interviews']}
                ids2 = {i['interview_id'] for i in data2['interviews']}
                
                if ids1.isdisjoint(ids2):
                    print(f"      ✅ Pagination working correctly (no duplicate IDs)")
                else:
                    print(f"      ⚠️ Pagination may have issues (duplicate IDs found)")
            
        except Exception as e:
            print(f"      ❌ Pagination error: {e}")
        
        print()
    
    def _test_specific_queries(self):
        """Test specific use case queries"""
        print("🎯 Step 5: Testing Specific Use Cases")
        print("-" * 45)
        
        use_cases = [
            {
                "name": "Today's Interviews",
                "description": "Find interviews happening today",
                "query": self._get_today_interviews
            },
            {
                "name": "High Priority Interviews", 
                "description": "Interviews needing attention",
                "query": self._get_priority_interviews
            },
            {
                "name": "Automation Status",
                "description": "Check automation coverage",
                "query": self._get_automation_status
            }
        ]
        
        for use_case in use_cases:
            try:
                print(f"   🎯 {use_case['name']}: {use_case['description']}")
                result = use_case['query']()
                print(f"      ✅ Query completed: {result}")
                
            except Exception as e:
                print(f"      ❌ Use case error: {e}")
        
        print()
    
    def _get_today_interviews(self) -> str:
        """Get interviews scheduled for today"""
        # This would typically filter by date range
        response = requests.get(f"{self.base_url}/api/interviews/", params={"page_size": 50})
        
        if response.status_code == 200:
            data = response.json()
            today = datetime.now().date()
            
            today_interviews = [
                i for i in data['interviews']
                if datetime.fromisoformat(i['scheduled_time'].replace('Z', '+00:00')).date() == today
            ]
            
            return f"Found {len(today_interviews)} interviews today"
        
        return "Failed to get today's interviews"
    
    def _get_priority_interviews(self) -> str:
        """Get interviews that need attention"""
        response = requests.get(f"{self.base_url}/api/interviews/", params={"page_size": 50})
        
        if response.status_code == 200:
            data = response.json()
            
            priority_interviews = [
                i for i in data['interviews']
                if (i['is_overdue'] or 
                    i['automation_score'] < 2 or
                    not i.get('calendar_event_id'))
            ]
            
            return f"Found {len(priority_interviews)} high-priority interviews"
        
        return "Failed to get priority interviews"
    
    def _get_automation_status(self) -> str:
        """Check overall automation coverage"""
        response = requests.get(f"{self.base_url}/api/interviews/", params={"page_size": 100})
        
        if response.status_code == 200:
            data = response.json()
            total = len(data['interviews'])
            
            if total == 0:
                return "No interviews to analyze"
            
            with_calendar = sum(1 for i in data['interviews'] if i.get('calendar_event_id'))
            with_meet = sum(1 for i in data['interviews'] if i.get('google_meet_link'))
            with_notifications = sum(1 for i in data['interviews'] if i.get('calendar_invites_sent'))
            
            calendar_pct = (with_calendar / total) * 100
            meet_pct = (with_meet / total) * 100
            notification_pct = (with_notifications / total) * 100
            
            return f"Calendar: {calendar_pct:.1f}%, Meet: {meet_pct:.1f}%, Notifications: {notification_pct:.1f}%"
        
        return "Failed to get automation status"
    
    def _show_dashboard_summary(self):
        """Show final dashboard summary"""
        print("📈 Step 6: Dashboard Summary & Insights")
        print("-" * 45)
        
        try:
            response = requests.get(f"{self.base_url}/api/interviews/", params={"page_size": 100})
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                interviews = data['interviews']
                
                print("   📊 OVERALL STATISTICS:")
                print(f"      📋 Total Interviews: {data['total_count']}")
                print(f"      🔮 Upcoming: {summary.get('upcoming_count', 0)}")
                print(f"      ✅ Completed: {summary.get('completed_count', 0)}")
                print(f"      🤖 Automation Rate: {summary.get('automation_rate', 0)}%")
                
                # Status breakdown
                status_breakdown = summary.get('status_breakdown', {})
                print("\\n   📊 STATUS BREAKDOWN:")
                for status, count in status_breakdown.items():
                    print(f"      {status.title()}: {count}")
                
                # Automation analysis
                if interviews:
                    avg_automation = sum(i['automation_score'] for i in interviews) / len(interviews)
                    high_automation = sum(1 for i in interviews if i['automation_score'] >= 3)
                    
                    print("\\n   ⚡ AUTOMATION ANALYSIS:")
                    print(f"      📊 Average Score: {avg_automation:.1f}/4")
                    print(f"      🎯 High Automation: {high_automation}/{len(interviews)}")
                    print(f"      📈 Success Rate: {(high_automation/len(interviews)*100):.1f}%")
                
                # Recent activity
                now = datetime.now()
                recent = [
                    i for i in interviews 
                    if (now - datetime.fromisoformat(i['created_at'].replace('Z', '+00:00'))).days <= 7
                ]
                
                print("\\n   📅 RECENT ACTIVITY (Last 7 days):")
                print(f"      📝 New Interviews: {len(recent)}")
                if recent:
                    avg_ai_score = sum(i.get('ai_match_score', 0) for i in recent if i.get('ai_match_score')) / len([i for i in recent if i.get('ai_match_score')])
                    print(f"      🤖 Avg AI Match Score: {avg_ai_score:.1f}")
                
            else:
                print(f"   ❌ Failed to get dashboard summary: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Summary error: {e}")
        
        print("\\n🎉 Interview Dashboard Demo Complete!")
        print("=" * 60)
        print("\\n💡 Key Features Demonstrated:")
        print("   ✅ Comprehensive JOIN queries for candidate/interviewer data")
        print("   ✅ Real-time interview status and timing calculations")
        print("   ✅ Meeting links and calendar integration status")
        print("   ✅ Advanced filtering and pagination")
        print("   ✅ Frontend-ready formatted responses")
        print("   ✅ Dashboard summary statistics")
        print("   ✅ Automation metrics and insights")
        print("\\n📚 API Usage:")
        print(f"   🌐 Dashboard: GET {self.base_url}/api/interviews/")
        print("   📄 With pagination: ?page=1&page_size=20")
        print("   🔍 With filters: ?status=confirmed&interview_type=technical")
        print("   📊 With sorting: ?sort_field=scheduled_time&sort_order=desc")

def main():
    """Run the dashboard demo"""
    print("📊 Starting Interview Dashboard Demo...")
    print("   This demonstrates the comprehensive dashboard with:")
    print("   • JOIN queries for complete interview data")
    print("   • Advanced filtering and pagination")
    print("   • Real-time status and automation metrics")
    print("   • Frontend-optimized response format")
    print()
    
    demo = InterviewDashboardDemo()
    demo.run_dashboard_demo()

if __name__ == "__main__":
    main()
