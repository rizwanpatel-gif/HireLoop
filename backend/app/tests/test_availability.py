"""
Interviewer Availability API Demo
================================

Comprehensive testing suite for the availability checking endpoint:
- Tests GET /api/availability/{interviewer_id} endpoint
- Demonstrates calendar integration and conflict detection
- Shows available time slots with confidence levels
- Validates filtering and recommendation logic
"""

import asyncio
import aiohttp
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AvailabilityAPIDemo:
    """Demo client for testing availability API functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_availability(
        self,
        interviewer_id: str,
        check_date: date,
        start_hour: int = 9,
        end_hour: int = 18,
        min_slot_duration: int = 30,
        timezone: str = "UTC",
        include_tentative: bool = False
    ) -> Dict[str, Any]:
        """Check availability for a specific interviewer"""
        
        url = f"{self.base_url}/api/availability/{interviewer_id}"
        
        params = {
            "check_date": check_date.isoformat(),
            "start_hour": start_hour,
            "end_hour": end_hour,
            "min_slot_duration": min_slot_duration,
            "timezone": timezone,
            "include_tentative": include_tentative
        }
        
        try:
            logger.info(f"🔍 Checking availability for {interviewer_id}")
            logger.info(f"   Date: {check_date}")
            logger.info(f"   Hours: {start_hour}:00 - {end_hour}:00")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Availability check successful")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Availability check failed: {response.status}")
                    logger.error(f"   Error: {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return {"error": str(e)}
    
    def format_availability_response(self, response: Dict[str, Any]) -> None:
        """Format and display availability response"""
        
        if "error" in response:
            print(f"\n❌ Error: {response['error']}")
            return
        
        interviewer = response.get('interviewer', {})
        available_slots = response.get('available_slots', [])
        busy_slots = response.get('busy_slots', [])
        recommended_slots = response.get('recommended_slots', [])
        
        print(f"\n📋 Availability Report for {interviewer.get('name', 'Unknown')}")
        print(f"📧 Email: {interviewer.get('email', 'N/A')}")
        print(f"🏢 Department: {interviewer.get('department', 'N/A')}")
        print(f"📅 Date: {response.get('check_date', 'N/A')}")
        print(f"🕐 Working Hours: {response.get('working_hours_start', 'N/A')} - {response.get('working_hours_end', 'N/A')}")
        print(f"🌐 Timezone: {response.get('timezone', 'N/A')}")
        
        # Availability summary
        availability_pct = response.get('availability_percentage', 0)
        total_available = response.get('total_available_minutes', 0)
        total_busy = response.get('total_busy_minutes', 0)
        
        print(f"\n📊 Availability Summary:")
        print(f"   ✅ Available: {total_available} minutes ({availability_pct}%)")
        print(f"   ❌ Busy: {total_busy} minutes ({100 - availability_pct:.1f}%)")
        print(f"   📈 Calendar Sync: {response.get('calendar_sync_status', 'unknown')}")
        
        # Available time slots
        if available_slots:
            print(f"\n🟢 Available Time Slots ({len(available_slots)} slots):")
            for i, slot in enumerate(available_slots, 1):
                start_time = datetime.fromisoformat(slot['start_time'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(slot['end_time'].replace('Z', '+00:00'))
                duration = slot.get('duration_minutes', 0)
                confidence = slot.get('confidence_level', 'unknown')
                notes = slot.get('notes', '')
                
                confidence_emoji = {
                    'high': '🟢',
                    'medium': '🟡', 
                    'low': '🔴'
                }.get(confidence, '⚪')
                
                print(f"   {i}. {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} "
                      f"({duration} min) {confidence_emoji} {confidence.upper()}")
                
                if notes:
                    print(f"      💡 {notes}")
        else:
            print(f"\n🚫 No available time slots found")
        
        # Busy periods
        if busy_slots:
            print(f"\n🔴 Busy Periods ({len(busy_slots)} conflicts):")
            for i, slot in enumerate(busy_slots, 1):
                start_time = datetime.fromisoformat(slot['start_time'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(slot['end_time'].replace('Z', '+00:00'))
                reason = slot.get('reason', 'Unknown')
                source = slot.get('source', 'unknown')
                event_title = slot.get('event_title', reason)
                
                source_emoji = {
                    'google_calendar': '📅',
                    'existing_interview': '💼',
                    'block': '🚫'
                }.get(source, '❓')
                
                print(f"   {i}. {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} "
                      f"{source_emoji} {event_title}")
        
        # Recommended slots
        if recommended_slots:
            print(f"\n⭐ Recommended Slots (Top {len(recommended_slots)}):")
            for i, slot in enumerate(recommended_slots, 1):
                start_time = datetime.fromisoformat(slot['start_time'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(slot['end_time'].replace('Z', '+00:00'))
                duration = slot.get('duration_minutes', 0)
                confidence = slot.get('confidence_level', 'unknown')
                
                print(f"   {i}. {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} "
                      f"({duration} min) - {confidence.upper()} confidence")
    
    async def run_comprehensive_demo(self):
        """Run comprehensive availability checking demo"""
        
        print("🚀 Starting Interviewer Availability API Demo")
        print("=" * 60)
        
        # Test data
        interviewer_ids = ["sarah_wilson", "michael_chen", "emily_rodriguez", "david_kim"]
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        test_scenarios = [
            {
                "name": "📅 Today's Availability (Standard Hours)",
                "interviewer_id": "sarah_wilson",
                "check_date": tomorrow,  # Use tomorrow since today might be past
                "start_hour": 9,
                "end_hour": 18,
                "min_slot_duration": 30
            },
            {
                "name": "🌅 Early Morning Availability",
                "interviewer_id": "michael_chen", 
                "check_date": tomorrow,
                "start_hour": 7,
                "end_hour": 12,
                "min_slot_duration": 45
            },
            {
                "name": "🌆 Extended Evening Hours",
                "interviewer_id": "emily_rodriguez",
                "check_date": tomorrow,
                "start_hour": 14,
                "end_hour": 20,
                "min_slot_duration": 60
            },
            {
                "name": "📈 Next Week Planning",
                "interviewer_id": "david_kim",
                "check_date": next_week,
                "start_hour": 9,
                "end_hour": 17,
                "min_slot_duration": 90
            },
            {
                "name": "⚡ Quick 15-minute Slots",
                "interviewer_id": "sarah_wilson",
                "check_date": tomorrow,
                "start_hour": 13,
                "end_hour": 16,
                "min_slot_duration": 15
            }
        ]
        
        # Run test scenarios
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. {scenario['name']}")
            print("-" * 50)
            
            response = await self.check_availability(
                interviewer_id=scenario['interviewer_id'],
                check_date=scenario['check_date'],
                start_hour=scenario['start_hour'],
                end_hour=scenario['end_hour'],
                min_slot_duration=scenario['min_slot_duration']
            )
            
            self.format_availability_response(response)
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        # Test error scenarios
        print(f"\n🧪 Testing Error Scenarios")
        print("-" * 50)
        
        error_tests = [
            {
                "name": "❌ Invalid Interviewer ID",
                "interviewer_id": "invalid_interviewer",
                "check_date": tomorrow
            },
            {
                "name": "❌ Past Date",
                "interviewer_id": "sarah_wilson", 
                "check_date": today - timedelta(days=1)
            },
            {
                "name": "❌ Invalid Hours (End before Start)",
                "interviewer_id": "sarah_wilson",
                "check_date": tomorrow,
                "start_hour": 18,
                "end_hour": 9
            }
        ]
        
        for i, test in enumerate(error_tests, 1):
            print(f"\n   {i}. {test['name']}")
            
            response = await self.check_availability(
                interviewer_id=test['interviewer_id'],
                check_date=test['check_date'],
                start_hour=test.get('start_hour', 9),
                end_hour=test.get('end_hour', 18)
            )
            
            if "error" in response:
                print(f"      ✅ Expected error: {response['error']}")
            else:
                print(f"      ❓ Unexpected success")
        
        print(f"\n✅ Availability API Demo Completed!")
        print("=" * 60)
    
    async def test_multiple_interviewers(self):
        """Test availability for multiple interviewers"""
        
        print(f"\n🔄 Testing Multiple Interviewer Availability")
        print("-" * 50)
        
        interviewer_ids = ["sarah_wilson", "michael_chen", "emily_rodriguez"]
        check_date = date.today() + timedelta(days=1)
        
        availability_results = {}
        
        for interviewer_id in interviewer_ids:
            response = await self.check_availability(
                interviewer_id=interviewer_id,
                check_date=check_date,
                start_hour=10,
                end_hour=16,
                min_slot_duration=60
            )
            
            availability_results[interviewer_id] = response
            await asyncio.sleep(0.5)  # Small delay
        
        # Summary comparison
        print(f"\n📊 Availability Comparison ({check_date}):")
        print(f"{'Interviewer':<20} {'Available':<10} {'Busy':<10} {'Availability':<12} {'Top Slot'}")
        print("-" * 70)
        
        for interviewer_id, data in availability_results.items():
            if "error" not in data:
                interviewer_name = data.get('interviewer', {}).get('name', interviewer_id)[:18]
                available_min = data.get('total_available_minutes', 0)
                busy_min = data.get('total_busy_minutes', 0)
                availability_pct = data.get('availability_percentage', 0)
                
                recommended = data.get('recommended_slots', [])
                top_slot = "None"
                if recommended:
                    slot = recommended[0]
                    start_time = datetime.fromisoformat(slot['start_time'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(slot['end_time'].replace('Z', '+00:00'))
                    top_slot = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
                
                print(f"{interviewer_name:<20} {available_min:<10} {busy_min:<10} {availability_pct:<11.1f}% {top_slot}")
            else:
                print(f"{interviewer_id:<20} {'ERROR':<10} {'ERROR':<10} {'ERROR':<12} {'ERROR'}")
    
    async def analyze_optimal_times(self):
        """Analyze optimal interview times across multiple interviewers"""
        
        print(f"\n🎯 Analyzing Optimal Interview Times")
        print("-" * 50)
        
        # Check morning vs afternoon availability
        time_slots = [
            {"name": "Morning (9-12)", "start": 9, "end": 12},
            {"name": "Lunch (12-13)", "start": 12, "end": 13},
            {"name": "Afternoon (13-17)", "start": 13, "end": 17},
            {"name": "Evening (17-19)", "start": 17, "end": 19}
        ]
        
        interviewer_ids = ["sarah_wilson", "michael_chen", "emily_rodriguez", "david_kim"]
        check_date = date.today() + timedelta(days=2)
        
        slot_analysis = {}
        
        for slot in time_slots:
            slot_name = slot['name']
            slot_analysis[slot_name] = {
                'total_available': 0,
                'interviewer_count': 0,
                'avg_availability': 0
            }
            
            for interviewer_id in interviewer_ids:
                response = await self.check_availability(
                    interviewer_id=interviewer_id,
                    check_date=check_date,
                    start_hour=slot['start'],
                    end_hour=slot['end'],
                    min_slot_duration=30
                )
                
                if "error" not in response:
                    available_min = response.get('total_available_minutes', 0)
                    slot_analysis[slot_name]['total_available'] += available_min
                    slot_analysis[slot_name]['interviewer_count'] += 1
                
                await asyncio.sleep(0.3)
        
        # Calculate averages and display results
        print(f"\n📈 Time Slot Analysis ({check_date}):")
        print(f"{'Time Slot':<20} {'Avg Available':<15} {'Total Available':<15} {'Interviewers'}")
        print("-" * 65)
        
        for slot_name, data in slot_analysis.items():
            count = data['interviewer_count']
            total = data['total_available']
            avg = total / count if count > 0 else 0
            
            print(f"{slot_name:<20} {avg:<14.1f} {total:<14} {count}")
        
        # Find best time slot
        best_slot = max(slot_analysis.items(), key=lambda x: x[1]['total_available'])
        print(f"\n🏆 Best Time Slot: {best_slot[0]} ({best_slot[1]['total_available']} total minutes)")

async def main():
    """Main demo function"""
    
    print("🎬 Interviewer Availability API Demo Starting...")
    print("📡 Make sure the API server is running on http://localhost:8000")
    print("⏳ Waiting 3 seconds for server to be ready...")
    
    await asyncio.sleep(3)
    
    try:
        async with AvailabilityAPIDemo() as demo:
            # Run comprehensive demo
            await demo.run_comprehensive_demo()
            
            # Test multiple interviewers
            await demo.test_multiple_interviewers()
            
            # Analyze optimal times
            await demo.analyze_optimal_times()
            
        print(f"\n🎉 Demo completed successfully!")
        print("💡 Check the API documentation at: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        logger.exception("Demo error details:")
        print(f"\n💥 Demo failed: {e}")
        print("🔧 Make sure the API server is running: python candidate_management_api.py")

if __name__ == "__main__":
    asyncio.run(main())
