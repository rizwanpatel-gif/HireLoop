"""
Enhanced Automation Workflow Tests
=================================

Focused tests for the enhanced availability checking and interview scheduling functionality.
Tests the new features:
- Automatic alternative slot finding when preferred time is busy
- Enhanced calendar event creation with proper attendee details and retry logic
- Edge cases like no availability within 24 hours
"""

import pytest
import asyncio
from datetime import datetime, timedelta, date
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDatabase:
    """Mock database session for testing"""
    
    def __init__(self):
        self.candidates = {}
        self.users = {}
        self.interviews = {}
        self.committed = False
        self.rolled_back = False
        
    def query(self, model):
        return MockQuery([])
    
    def add(self, obj):
        if hasattr(obj, 'id') and obj.id:
            pass  # Mock add operation
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        self.rolled_back = True
    
    def refresh(self, obj):
        pass

class MockQuery:
    """Mock query object for testing"""
    
    def __init__(self, items):
        self.items = items
    
    def filter(self, *args):
        return self
    
    def first(self):
        return self.items[0] if self.items else None

class TestEnhancedAvailabilityChecking:
    """Test the enhanced _check_availability method"""
    
    @pytest.fixture
    def automation_service(self):
        """Create automation service with mocked dependencies"""
        with patch('automation_service.AIService') as mock_ai_service, \
             patch('automation_service.GoogleCalendarService') as mock_calendar_service:
            
            from automation_service import InterviewAutomationService
            service = InterviewAutomationService()
            
            # Ensure the mocked services are properly set
            service.calendar_service = Mock()
            service.ai_service = Mock()
            return service
    
    @pytest.fixture
    def mock_candidate(self):
        """Create a mock candidate for testing"""
        candidate = Mock()
        candidate.id = 1
        candidate.name = "John Doe"
        candidate.email = "john.doe@example.com"
        candidate.position = "Python Developer"
        candidate.interview_datetime = datetime.now() + timedelta(days=1, hours=10)  # Tomorrow at 10 AM
        return candidate
    
    @pytest.fixture
    def mock_interviewer(self):
        """Create a mock interviewer for testing"""
        interviewer = Mock()
        interviewer.id = 1
        interviewer.name = "Jane Smith"
        interviewer.email = "jane.smith@company.com"
        return interviewer
    
    @pytest.mark.asyncio
    async def test_availability_check_preferred_time_free(self, automation_service, mock_candidate, mock_interviewer):
        """Test availability check when preferred time is free"""
        
        # Mock calendar service to return no conflicts
        automation_service.calendar_service.get_availability.return_value = {
            'busy': [],
            'free': [{'start': '2025-01-15T10:00:00', 'end': '2025-01-15T11:00:00'}]
        }
        
        result = await automation_service._check_availability(
            mock_candidate, 
            mock_interviewer, 
            mock_candidate.interview_datetime
        )
        
        assert result['available'] is True
        assert result['is_preferred_time'] is True
        assert result['time'] == mock_candidate.interview_datetime
        assert 'formatted_time' in result
        
        # Verify calendar API was called
        automation_service.calendar_service.get_availability.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_availability_check_preferred_time_busy_finds_alternative(self, automation_service, mock_candidate, mock_interviewer):
        """Test availability check when preferred time is busy but alternative is found"""
        
        # Use a specific weekday (Tuesday) in business hours (10 AM)
        from datetime import date
        tuesday = date(2025, 8, 5)  # A Tuesday
        preferred_time = datetime.combine(tuesday, datetime.min.time().replace(hour=10))
        # Alternative time 2 hours later (12 PM), still in business hours
        alternative_time = preferred_time + timedelta(hours=2)
        
        # Update mock candidate
        mock_candidate.interview_datetime = preferred_time
        
        # Mock calendar service responses with debug logging
        call_count = 0
        def mock_get_availability(email, start_time, end_time):
            nonlocal call_count
            call_count += 1
            logger.info(f"Mock calendar call #{call_count}: {start_time.strftime('%A %H:%M')} - {end_time.strftime('%H:%M')}")
            
            if start_time == preferred_time:
                # Preferred time is busy
                return {
                    'busy': [{'start': start_time.isoformat(), 'end': end_time.isoformat()}],
                    'free': []
                }
            elif start_time == alternative_time:
                # Alternative time is free
                logger.info(f"   -> Returning FREE for alternative time {start_time}")
                return {
                    'busy': [],
                    'free': [{'start': start_time.isoformat(), 'end': end_time.isoformat()}]
                }
            else:
                # Default: busy for other times
                return {'busy': [{'start': start_time.isoformat(), 'end': end_time.isoformat()}]}
        
        automation_service.calendar_service.get_availability.side_effect = mock_get_availability
        
        result = await automation_service._check_availability(
            mock_candidate, 
            mock_interviewer, 
            preferred_time,
            auto_find_alternatives=True,
            search_window_hours=8  # Extended search window to ensure we find the slot
        )
        
        logger.info(f"Test result: {result}")
        logger.info(f"Total calendar calls made: {call_count}")
        
        assert result['available'] is True
        assert result['is_preferred_time'] is False
        assert result['alternative_found'] is True
        assert result['time'] == alternative_time
        assert 'slots_checked' in result
        
        # Verify multiple calendar API calls were made
        assert automation_service.calendar_service.get_availability.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_availability_check_no_alternatives_within_window(self, automation_service, mock_candidate, mock_interviewer):
        """Test availability check when no alternatives found within search window"""
        
        # Use a specific weekday (Tuesday) in business hours 
        from datetime import date
        tuesday = date(2025, 8, 5)  # A Tuesday
        preferred_time = datetime.combine(tuesday, datetime.min.time().replace(hour=10))
        mock_candidate.interview_datetime = preferred_time
        
        # Mock calendar service to always return busy
        automation_service.calendar_service.get_availability.return_value = {
            'busy': [{'start': '2025-01-15T10:00:00', 'end': '2025-01-15T11:00:00'}],
            'free': []
        }
        
        result = await automation_service._check_availability(
            mock_candidate, 
            mock_interviewer, 
            preferred_time,
            auto_find_alternatives=True,
            search_window_hours=24
        )
        
        assert result['available'] is False
        assert result['alternative_search_attempted'] is True
        assert result['search_window_hours'] == 24
        assert 'conflicts' in result
        
        # Verify many calendar API calls were made (searching for 24 hours)
        # The algorithm checks 24 slots total but may batch some calls or hit delays
        assert automation_service.calendar_service.get_availability.call_count >= 8
    
    @pytest.mark.asyncio
    async def test_availability_check_calendar_api_error(self, automation_service, mock_candidate, mock_interviewer):
        """Test availability check when calendar API returns error"""
        
        # Mock calendar service to return error
        automation_service.calendar_service.get_availability.return_value = {
            'error': 'API rate limit exceeded'
        }
        
        result = await automation_service._check_availability(
            mock_candidate, 
            mock_interviewer, 
            mock_candidate.interview_datetime
        )
        
        assert result['available'] is False
        assert 'Calendar error' in result['reason']
    
    @pytest.mark.asyncio
    async def test_find_next_available_slot_within_business_hours(self, automation_service, mock_interviewer):
        """Test that alternative slot finding respects business hours"""
        
        # Start search from 6 PM (after business hours)
        start_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Mock calendar service - first call (at 7 PM) is busy, second call (next day 9 AM) is free
        call_count = 0
        def mock_get_availability(email, check_time, end_time):
            nonlocal call_count
            call_count += 1
            
            if check_time.hour == 9 and check_time.hour < 18:  # Business hours
                return {'busy': [], 'free': []}
            else:
                return {'busy': [{'start': check_time.isoformat(), 'end': end_time.isoformat()}]}
        
        automation_service.calendar_service.get_availability.side_effect = mock_get_availability
        
        result = await automation_service._find_next_available_slot(
            mock_interviewer, 
            start_time, 
            search_window_hours=48
        )
        
        assert result is not None
        assert result['time'].hour >= 9  # Should be in business hours
        assert result['time'].hour < 18
        assert result['time'].weekday() < 5  # Should be weekday

class TestEnhancedInterviewScheduling:
    """Test the enhanced _schedule_interview method"""
    
    @pytest.fixture
    def automation_service(self):
        """Create automation service with mocked dependencies"""
        with patch('automation_service.AIService') as mock_ai_service, \
             patch('automation_service.GoogleCalendarService') as mock_calendar_service:
            
            from automation_service import InterviewAutomationService
            service = InterviewAutomationService()
            
            # Ensure the mocked services are properly set
            service.calendar_service = Mock()
            service.ai_service = Mock()
            return service
    
    @pytest.fixture
    def mock_candidate(self):
        """Create a mock candidate for testing"""
        candidate = Mock()
        candidate.id = 1
        candidate.name = "John Doe"
        candidate.email = "john.doe@example.com"
        candidate.position = "Python Developer"
        candidate.interview_datetime = datetime.now() + timedelta(days=1, hours=10)
        candidate.interview_scheduled = False
        return candidate
    
    @pytest.fixture
    def mock_interviewer(self):
        """Create a mock interviewer for testing"""
        interviewer = Mock()
        interviewer.id = 1
        interviewer.name = "Jane Smith"
        interviewer.email = "jane.smith@company.com"
        return interviewer
    
    @pytest.fixture
    def mock_analysis(self):
        """Create mock AI analysis results"""
        analysis = Mock()
        analysis.overall_score = 85
        return analysis
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return MockDatabase()
    
    @pytest.mark.asyncio
    async def test_schedule_interview_success(self, automation_service, mock_candidate, mock_interviewer, mock_analysis, mock_db):
        """Test successful interview scheduling with calendar integration"""
        
        scheduled_time = datetime.now() + timedelta(days=1, hours=10)
        
        # Mock successful calendar event creation
        automation_service.calendar_service.create_interview_event.return_value = {
            'event_id': 'google_event_123',
            'meet_link': 'https://meet.google.com/test-meeting',
            'event_link': 'https://calendar.google.com/event/123'
        }
        
        # Mock the Interview class from the models import inside the function
        with patch('app.models.models.Interview') as mock_interview_class:
            mock_interview_instance = Mock()
            mock_interview_instance.id = 42  # Set a mock ID
            mock_interview_class.return_value = mock_interview_instance
            
            result = await automation_service._schedule_interview(
                mock_candidate, 
                mock_interviewer, 
                scheduled_time, 
                mock_analysis, 
                mock_db
            )
        
        assert result['success'] is True
        assert result['event_id'] == 'google_event_123'
        assert result['meet_link'] == 'https://meet.google.com/test-meeting'
        assert result['interview_id'] == 42  # Check for the mocked ID
        assert result['calendar_integration'] == 'success'
        
        # Verify candidate was updated
        assert mock_candidate.interview_datetime == scheduled_time
        assert mock_candidate.interview_scheduled is True
        
        # Verify database operations
        assert mock_db.committed is True
        
        # Verify calendar service was called
        automation_service.calendar_service.create_interview_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_schedule_interview_calendar_failure_with_retry(self, automation_service, mock_candidate, mock_interviewer, mock_analysis, mock_db):
        """Test interview scheduling with calendar API failure and retry logic"""
        
        scheduled_time = datetime.now() + timedelta(days=1, hours=10)
        
        # Mock calendar service to fail twice then succeed
        call_count = 0
        def mock_create_event(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:
                return None  # Failure
            else:
                return {  # Success on third try
                    'event_id': 'google_event_123',
                    'meet_link': 'https://meet.google.com/test-meeting',
                    'event_link': 'https://calendar.google.com/event/123'
                }
        
        automation_service.calendar_service.create_interview_event.side_effect = mock_create_event
        
        result = await automation_service._schedule_interview(
            mock_candidate, 
            mock_interviewer, 
            scheduled_time, 
            mock_analysis, 
            mock_db,
            retry_count=3
        )
        
        assert result['success'] is True
        assert result['retries_used'] > 0
        
        # Verify calendar service was called multiple times
        assert automation_service.calendar_service.create_interview_event.call_count == 3
    
    @pytest.mark.asyncio
    async def test_schedule_interview_calendar_complete_failure(self, automation_service, mock_candidate, mock_interviewer, mock_analysis, mock_db):
        """Test interview scheduling when calendar API completely fails"""
        
        scheduled_time = datetime.now() + timedelta(days=1, hours=10)
        
        # Mock calendar service to always fail
        automation_service.calendar_service.create_interview_event.return_value = None
        
        result = await automation_service._schedule_interview(
            mock_candidate, 
            mock_interviewer, 
            scheduled_time, 
            mock_analysis, 
            mock_db,
            retry_count=3
        )
        
        assert result['success'] is False
        assert 'Calendar integration failed' in result['error']
        assert result['calendar_integration'] == 'failed'
        assert result['retries_attempted'] == 3
        
        # Verify calendar service was called multiple times
        assert automation_service.calendar_service.create_interview_event.call_count == 3
    
    @pytest.mark.asyncio
    async def test_schedule_interview_database_failure_cleanup(self, automation_service, mock_candidate, mock_interviewer, mock_analysis):
        """Test that calendar events are cleaned up when database operations fail"""
        
        scheduled_time = datetime.now() + timedelta(days=1, hours=10)
        
        # Mock successful calendar event creation
        automation_service.calendar_service.create_interview_event.return_value = {
            'event_id': 'google_event_123',
            'meet_link': 'https://meet.google.com/test-meeting'
        }
        
        # Mock calendar deletion
        automation_service.calendar_service.delete_interview_event.return_value = True
        
        # Create a mock database that fails on commit
        mock_db = Mock()
        mock_db.add.return_value = None
        mock_db.commit.side_effect = Exception("Database connection error")
        mock_db.rollback.return_value = None
        
        result = await automation_service._schedule_interview(
            mock_candidate, 
            mock_interviewer, 
            scheduled_time, 
            mock_analysis, 
            mock_db
        )
        
        assert result['success'] is False
        assert 'Database error' in result['error']
        
        # Verify cleanup was attempted
        automation_service.calendar_service.delete_interview_event.assert_called_once_with('google_event_123')
        mock_db.rollback.assert_called_once()

class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def automation_service(self):
        """Create automation service with mocked dependencies"""
        with patch('automation_service.AIService') as mock_ai_service, \
             patch('automation_service.GoogleCalendarService') as mock_calendar_service:
            
            from automation_service import InterviewAutomationService
            service = InterviewAutomationService()
            
            # Ensure the mocked services are properly set
            service.calendar_service = Mock()
            service.ai_service = Mock()
            return service
    
    @pytest.mark.asyncio
    async def test_no_availability_within_24_hours(self, automation_service):
        """Test edge case: no availability within 24 hours"""
        
        mock_candidate = Mock()
        mock_candidate.interview_datetime = datetime.now() + timedelta(hours=1)
        
        mock_interviewer = Mock()
        mock_interviewer.name = "Jane Smith"
        mock_interviewer.email = "jane@company.com"
        
        # Mock calendar service to always return busy
        automation_service.calendar_service.get_availability.return_value = {
            'busy': [{'start': '2025-01-15T10:00:00', 'end': '2025-01-15T11:00:00'}],
            'free': []
        }
        
        result = await automation_service._check_availability(
            mock_candidate, 
            mock_interviewer, 
            mock_candidate.interview_datetime,
            auto_find_alternatives=True,
            search_window_hours=24
        )
        
        assert result['available'] is False
        assert result['alternative_search_attempted'] is True
        assert result['search_window_hours'] == 24
        assert 'no alternatives found' in result['reason']
    
    @pytest.mark.asyncio
    async def test_weekend_skip_logic(self, automation_service):
        """Test that weekend dates are properly skipped"""
        
        mock_interviewer = Mock()
        mock_interviewer.name = "Jane Smith"
        mock_interviewer.email = "jane@company.com"
        
        # Start search from a Friday evening
        friday_evening = datetime.now()
        friday_evening = friday_evening.replace(hour=17, minute=0, second=0, microsecond=0)
        # Adjust to ensure it's a Friday
        while friday_evening.weekday() != 4:  # 4 = Friday
            friday_evening += timedelta(days=1)
        
        # Mock calendar service - only Monday morning should be checked (not weekend)
        checked_times = []
        def mock_get_availability(email, start_time, end_time):
            checked_times.append((start_time.weekday(), start_time.hour))
            return {'busy': [], 'free': []}  # Return free for Monday
        
        automation_service.calendar_service.get_availability.side_effect = mock_get_availability
        
        result = await automation_service._find_next_available_slot(
            mock_interviewer, 
            friday_evening, 
            search_window_hours=72  # 3 days to include weekend
        )
        
        # Should find Monday morning and skip weekend
        assert result is not None
        
        # Check that no weekend times were checked
        for weekday, hour in checked_times:
            if weekday >= 5:  # Saturday=5, Sunday=6
                pytest.fail(f"Weekend day {weekday} was checked, should be skipped")

if __name__ == "__main__":
    # Run tests manually
    pytest.main([__file__, "-v", "--tb=short"])