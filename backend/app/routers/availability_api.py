"""
Interviewer Availability API
===========================

Provides real-time availability checking for interviewers by:
- Checking Google Calendar for busy times on specific dates
- Returning available time slots between 9 AM - 6 PM
- Considering existing interviews and calendar conflicts
- Formatting response as array of available time ranges
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta, date, time
from enum import Enum
import logging
import pytz
from dataclasses import dataclass

from app.models.models import Interview, Candidate, User, InterviewStatus
InterviewDB = Interview
CandidateDB = Candidate
from app.core.database import get_db, SessionLocal
from app.services.calendar_service import GoogleCalendarService
from app.services.smart_matching import create_sample_interviewer_profiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeSlotType(str, Enum):
    """Types of time slots"""
    AVAILABLE = "available"
    BUSY = "busy"
    TENTATIVE = "tentative"
    OUT_OF_OFFICE = "out_of_office"

@dataclass
class TimeSlot:
    """Represents a time slot with availability information"""
    start_time: datetime
    end_time: datetime
    slot_type: TimeSlotType
    duration_minutes: int
    reason: Optional[str] = None
    source: Optional[str] = None  # "calendar", "interview", "break"

class AvailabilityRequest(BaseModel):
    """Request model for availability checking"""
    interviewer_id: str = Field(..., description="Interviewer unique identifier")
    check_date: date = Field(..., description="Date to check availability for")
    start_hour: int = Field(9, ge=0, le=23, description="Start hour (24-hour format)")
    end_hour: int = Field(18, ge=0, le=23, description="End hour (24-hour format)")
    min_slot_duration: int = Field(30, ge=15, le=240, description="Minimum slot duration in minutes")
    timezone: str = Field("UTC", description="Timezone for the availability check")
    include_tentative: bool = Field(False, description="Include tentative slots as available")
    
    @validator('check_date')
    def validate_date_not_past(cls, v):
        if v < date.today():
            raise ValueError('Cannot check availability for past dates')
        return v
    
    @validator('end_hour')
    def validate_end_after_start(cls, v, values):
        if 'start_hour' in values and v <= values['start_hour']:
            raise ValueError('End hour must be after start hour')
        return v

class AvailableTimeSlot(BaseModel):
    """Available time slot response model"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    slot_id: str
    confidence_level: str  # "high", "medium", "low"
    notes: Optional[str] = None

class BusyTimeSlot(BaseModel):
    """Busy time slot information"""
    start_time: datetime
    end_time: datetime
    reason: str
    source: str  # "google_calendar", "existing_interview", "block"
    event_title: Optional[str] = None

class InterviewerInfo(BaseModel):
    """Interviewer information"""
    interviewer_id: str
    name: str
    email: str
    department: Optional[str] = None
    timezone: str
    working_hours: Dict[str, Any]
    last_calendar_sync: Optional[datetime] = None

class AvailabilityResponse(BaseModel):
    """Comprehensive availability response"""
    interviewer: InterviewerInfo
    check_date: date
    timezone: str
    
    # Available slots
    available_slots: List[AvailableTimeSlot]
    total_available_minutes: int
    
    # Busy periods
    busy_slots: List[BusyTimeSlot]
    total_busy_minutes: int
    
    # Summary statistics
    availability_percentage: float
    recommended_slots: List[AvailableTimeSlot]  # Best slots based on preferences
    
    # Metadata
    last_updated: datetime
    calendar_sync_status: str
    working_hours_start: time
    working_hours_end: time

class AvailabilityChecker:
    """Service class for checking interviewer availability"""
    
    def __init__(self):
        self.calendar_service = GoogleCalendarService()
        self.interviewer_profiles = create_sample_interviewer_profiles()
        
    async def check_availability(
        self,
        interviewer_id: str,
        check_date: date,
        start_hour: int = 9,
        end_hour: int = 18,
        min_slot_duration: int = 30,
        timezone: str = "UTC",
        include_tentative: bool = False,
        db: Session = None
    ) -> AvailabilityResponse:
        """
        Check comprehensive availability for an interviewer
        
        Args:
            interviewer_id: Unique interviewer identifier
            check_date: Date to check availability
            start_hour: Start of working hours (24-hour format)
            end_hour: End of working hours (24-hour format)
            min_slot_duration: Minimum duration for available slots
            timezone: Timezone for calculations
            include_tentative: Whether to include tentative calendar events
            db: Database session
            
        Returns:
            AvailabilityResponse with detailed availability information
        """
        
        try:
            logger.info(f"🗓️ Checking availability for interviewer {interviewer_id}")
            logger.info(f"   Date: {check_date}")
            logger.info(f"   Hours: {start_hour}:00 - {end_hour}:00")
            logger.info(f"   Min slot: {min_slot_duration} minutes")
            
            # Step 1: Get interviewer information
            interviewer = await self._get_interviewer_info(interviewer_id)
            if not interviewer:
                raise HTTPException(
                    status_code=404,
                    detail=f"Interviewer {interviewer_id} not found"
                )
            
            # Step 2: Set up timezone and time boundaries
            tz = pytz.timezone(timezone) if timezone != "UTC" else pytz.UTC
            
            check_start = datetime.combine(check_date, time(start_hour, 0))
            check_end = datetime.combine(check_date, time(end_hour, 0))
            
            # Localize to timezone
            check_start = tz.localize(check_start)
            check_end = tz.localize(check_end)
            
            logger.info(f"   Checking period: {check_start} to {check_end}")
            
            # Step 3: Get Google Calendar busy times
            calendar_busy_slots = await self._get_calendar_busy_times(
                interviewer['email'], check_start, check_end, include_tentative
            )
            
            # Step 4: Get existing interview conflicts
            interview_busy_slots = await self._get_interview_conflicts(
                interviewer_id, check_start, check_end, db
            )
            
            # Step 5: Combine all busy periods
            all_busy_slots = calendar_busy_slots + interview_busy_slots
            
            # Step 6: Calculate available time slots
            available_slots = await self._calculate_available_slots(
                check_start, check_end, all_busy_slots, min_slot_duration
            )
            
            # Step 7: Rank and recommend best slots
            recommended_slots = await self._recommend_best_slots(
                available_slots, interviewer
            )
            
            # Step 8: Calculate statistics
            total_working_minutes = (check_end - check_start).total_seconds() / 60
            total_available_minutes = sum(slot.duration_minutes for slot in available_slots)
            total_busy_minutes = sum(
                (slot.end_time - slot.start_time).total_seconds() / 60 
                for slot in all_busy_slots
            )
            
            availability_percentage = (total_available_minutes / total_working_minutes) * 100
            
            # Step 9: Build response
            response = AvailabilityResponse(
                interviewer=InterviewerInfo(
                    interviewer_id=interviewer_id,
                    name=interviewer['name'],
                    email=interviewer['email'],
                    department=interviewer.get('department', 'Engineering'),
                    timezone=timezone,
                    working_hours={
                        'start': f"{start_hour}:00",
                        'end': f"{end_hour}:00",
                        'timezone': timezone
                    },
                    last_calendar_sync=datetime.utcnow()
                ),
                check_date=check_date,
                timezone=timezone,
                available_slots=available_slots,
                total_available_minutes=int(total_available_minutes),
                busy_slots=[
                    BusyTimeSlot(
                        start_time=slot.start_time,
                        end_time=slot.end_time,
                        reason=slot.reason or "Busy",
                        source=slot.source or "unknown",
                        event_title=getattr(slot, 'title', None)
                    ) for slot in all_busy_slots
                ],
                total_busy_minutes=int(total_busy_minutes),
                availability_percentage=round(availability_percentage, 1),
                recommended_slots=recommended_slots[:3],  # Top 3 recommendations
                last_updated=datetime.utcnow(),
                calendar_sync_status="synced",
                working_hours_start=time(start_hour, 0),
                working_hours_end=time(end_hour, 0)
            )
            
            logger.info(f"✅ Availability check completed")
            logger.info(f"   Available slots: {len(available_slots)}")
            logger.info(f"   Total available: {total_available_minutes:.0f} minutes")
            logger.info(f"   Availability: {availability_percentage:.1f}%")
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Availability check failed: {e}")
            logger.exception("Availability check error details:")
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check availability: {str(e)}"
            )
    
    async def _get_interviewer_info(self, interviewer_id: str) -> Optional[Dict[str, Any]]:
        """Get interviewer information from profiles"""
        for profile in self.interviewer_profiles:
            if profile['id'] == interviewer_id:
                return profile
        return None
    
    async def _get_calendar_busy_times(
        self,
        interviewer_email: str,
        start_time: datetime,
        end_time: datetime,
        include_tentative: bool = False
    ) -> List[TimeSlot]:
        """Get busy times from Google Calendar"""
        
        busy_slots = []
        
        try:
            logger.info(f"   📅 Checking Google Calendar for {interviewer_email}")
            
            # For demo purposes, simulate calendar API call
            # In production, this would call actual Google Calendar API
            calendar_events = await self._simulate_calendar_events(
                start_time, end_time, interviewer_email
            )
            
            for event in calendar_events:
                # Skip tentative events if not included
                if not include_tentative and event.get('status') == 'tentative':
                    continue
                
                busy_slot = TimeSlot(
                    start_time=event['start'],
                    end_time=event['end'],
                    slot_type=TimeSlotType.BUSY,
                    duration_minutes=int((event['end'] - event['start']).total_seconds() / 60),
                    reason=event.get('title', 'Calendar Event'),
                    source="google_calendar"
                )
                busy_slots.append(busy_slot)
                
                logger.info(f"      📋 Calendar busy: {event['start'].strftime('%H:%M')}-{event['end'].strftime('%H:%M')} ({event.get('title', 'Event')})")
            
            logger.info(f"   📊 Found {len(busy_slots)} calendar conflicts")
            
        except Exception as e:
            logger.error(f"Error checking Google Calendar: {e}")
            # Continue without calendar data rather than failing
        
        return busy_slots
    
    async def _simulate_calendar_events(
        self,
        start_time: datetime,
        end_time: datetime,
        interviewer_email: str
    ) -> List[Dict[str, Any]]:
        """Simulate calendar events for demo purposes"""
        
        import random
        
        events = []
        current_time = start_time
        
        # Simulate some realistic calendar events
        sample_events = [
            {"title": "Team Standup", "duration": 30},
            {"title": "Client Meeting", "duration": 60},
            {"title": "Code Review", "duration": 45},
            {"title": "Planning Session", "duration": 90},
            {"title": "1:1 with Manager", "duration": 30},
            {"title": "Lunch Break", "duration": 60},
            {"title": "Project Sync", "duration": 45}
        ]
        
        # Generate 2-4 random events for the day
        num_events = random.randint(2, 4)
        
        for _ in range(num_events):
            # Random start time within the working hours
            hours_range = (end_time - start_time).total_seconds() / 3600
            random_hour_offset = random.uniform(0, hours_range - 2)  # Leave space for event
            
            event_start = start_time + timedelta(hours=random_hour_offset)
            event_data = random.choice(sample_events)
            event_end = event_start + timedelta(minutes=event_data['duration'])
            
            # Make sure event is within working hours
            if event_end <= end_time:
                events.append({
                    'start': event_start,
                    'end': event_end,
                    'title': event_data['title'],
                    'status': 'confirmed'
                })
        
        # Sort events by start time
        events.sort(key=lambda x: x['start'])
        
        return events
    
    async def _get_interview_conflicts(
        self,
        interviewer_id: str,
        start_time: datetime,
        end_time: datetime,
        db: Session
    ) -> List[TimeSlot]:
        """Get existing interview conflicts from database"""
        
        busy_slots = []
        
        try:
            if not db:
                logger.warning("No database session provided for interview conflicts")
                return busy_slots
            
            logger.info(f"   💼 Checking existing interviews for interviewer {interviewer_id}")
            
            # Query existing interviews for this interviewer in the time range
            existing_interviews = db.query(InterviewDB).filter(
                and_(
                    InterviewDB.interviewer_id == interviewer_id,
                    InterviewDB.scheduled_time >= start_time.replace(tzinfo=None),
                    InterviewDB.scheduled_time < end_time.replace(tzinfo=None),
                    InterviewDB.status.in_([
                        InterviewStatus.SCHEDULED,
                        InterviewStatus.CONFIRMED,
                        InterviewStatus.IN_PROGRESS
                    ])
                )
            ).all()
            
            for interview in existing_interviews:
                interview_end = interview.scheduled_time + timedelta(minutes=interview.duration_minutes)
                
                busy_slot = TimeSlot(
                    start_time=interview.scheduled_time.replace(tzinfo=start_time.tzinfo),
                    end_time=interview_end.replace(tzinfo=start_time.tzinfo),
                    slot_type=TimeSlotType.BUSY,
                    duration_minutes=interview.duration_minutes,
                    reason=f"Interview: {interview.interview_type}",
                    source="existing_interview"
                )
                busy_slots.append(busy_slot)
                
                logger.info(f"      💼 Interview conflict: {interview.scheduled_time.strftime('%H:%M')}-{interview_end.strftime('%H:%M')} ({interview.interview_type})")
            
            logger.info(f"   📊 Found {len(busy_slots)} interview conflicts")
            
        except Exception as e:
            logger.error(f"Error checking interview conflicts: {e}")
        
        return busy_slots
    
    async def _calculate_available_slots(
        self,
        start_time: datetime,
        end_time: datetime,
        busy_slots: List[TimeSlot],
        min_duration: int
    ) -> List[AvailableTimeSlot]:
        """Calculate available time slots from busy periods"""
        
        available_slots = []
        
        try:
            # Sort busy slots by start time
            busy_slots.sort(key=lambda x: x.start_time)
            
            # Merge overlapping busy slots
            merged_busy = []
            for busy_slot in busy_slots:
                if not merged_busy or merged_busy[-1].end_time < busy_slot.start_time:
                    merged_busy.append(busy_slot)
                else:
                    # Extend the last busy slot
                    merged_busy[-1].end_time = max(merged_busy[-1].end_time, busy_slot.end_time)
            
            # Find gaps between busy periods
            current_time = start_time
            slot_id = 1
            
            for busy_slot in merged_busy:
                # Check if there's a gap before this busy slot
                if current_time < busy_slot.start_time:
                    gap_duration = (busy_slot.start_time - current_time).total_seconds() / 60
                    
                    if gap_duration >= min_duration:
                        # Split large gaps into reasonable chunks
                        chunk_start = current_time
                        while (busy_slot.start_time - chunk_start).total_seconds() / 60 >= min_duration:
                            # Prefer 60-90 minute chunks for interviews
                            chunk_duration = min(90, gap_duration)
                            chunk_end = chunk_start + timedelta(minutes=chunk_duration)
                            
                            if chunk_end > busy_slot.start_time:
                                chunk_end = busy_slot.start_time
                                chunk_duration = (chunk_end - chunk_start).total_seconds() / 60
                            
                            if chunk_duration >= min_duration:
                                confidence = self._calculate_slot_confidence(chunk_start, chunk_duration)
                                
                                available_slot = AvailableTimeSlot(
                                    start_time=chunk_start,
                                    end_time=chunk_end,
                                    duration_minutes=int(chunk_duration),
                                    slot_id=f"slot_{slot_id}",
                                    confidence_level=confidence,
                                    notes=self._generate_slot_notes(chunk_start, chunk_duration)
                                )
                                available_slots.append(available_slot)
                                slot_id += 1
                            
                            chunk_start = chunk_end
                            gap_duration = (busy_slot.start_time - chunk_start).total_seconds() / 60
                
                current_time = max(current_time, busy_slot.end_time)
            
            # Check for availability after the last busy slot
            if current_time < end_time:
                final_gap_duration = (end_time - current_time).total_seconds() / 60
                
                if final_gap_duration >= min_duration:
                    confidence = self._calculate_slot_confidence(current_time, final_gap_duration)
                    
                    available_slot = AvailableTimeSlot(
                        start_time=current_time,
                        end_time=end_time,
                        duration_minutes=int(final_gap_duration),
                        slot_id=f"slot_{slot_id}",
                        confidence_level=confidence,
                        notes=self._generate_slot_notes(current_time, final_gap_duration)
                    )
                    available_slots.append(available_slot)
            
            logger.info(f"   ✅ Calculated {len(available_slots)} available slots")
            
        except Exception as e:
            logger.error(f"Error calculating available slots: {e}")
        
        return available_slots
    
    def _calculate_slot_confidence(self, start_time: datetime, duration: float) -> str:
        """Calculate confidence level for a time slot"""
        
        hour = start_time.hour
        
        # Morning slots (9-11 AM) are generally high confidence
        if 9 <= hour <= 11:
            return "high"
        
        # Lunch time (12-1 PM) might be lower confidence
        elif 12 <= hour <= 13:
            return "medium"
        
        # Afternoon slots (2-4 PM) are good
        elif 14 <= hour <= 16:
            return "high"
        
        # Late afternoon might be lower confidence
        elif 17 <= hour <= 18:
            return "medium"
        
        # Very long slots might have scheduling conflicts
        elif duration > 120:
            return "medium"
        
        else:
            return "high"
    
    def _generate_slot_notes(self, start_time: datetime, duration: float) -> str:
        """Generate helpful notes for a time slot"""
        
        hour = start_time.hour
        notes = []
        
        if 9 <= hour <= 10:
            notes.append("Good morning slot")
        elif 11 <= hour <= 12:
            notes.append("Late morning")
        elif 12 <= hour <= 13:
            notes.append("Lunch time - confirm availability")
        elif 14 <= hour <= 16:
            notes.append("Prime afternoon slot")
        elif 17 <= hour <= 18:
            notes.append("End of day - may run over")
        
        if duration >= 90:
            notes.append("Extended interview slot")
        elif duration <= 30:
            notes.append("Quick interview slot")
        
        return "; ".join(notes) if notes else None
    
    async def _recommend_best_slots(
        self,
        available_slots: List[AvailableTimeSlot],
        interviewer: Dict[str, Any]
    ) -> List[AvailableTimeSlot]:
        """Recommend the best available slots based on preferences"""
        
        # Score slots based on various factors
        scored_slots = []
        
        for slot in available_slots:
            score = 0
            
            # Time of day preference (higher score for better times)
            hour = slot.start_time.hour
            if 9 <= hour <= 11:  # Morning
                score += 10
            elif 14 <= hour <= 16:  # Afternoon
                score += 8
            elif 11 <= hour <= 12:  # Late morning
                score += 6
            elif 16 <= hour <= 17:  # Late afternoon
                score += 4
            
            # Duration preference (60-90 minutes is ideal)
            if 60 <= slot.duration_minutes <= 90:
                score += 8
            elif 45 <= slot.duration_minutes < 60:
                score += 6
            elif 30 <= slot.duration_minutes < 45:
                score += 4
            
            # Confidence level
            if slot.confidence_level == "high":
                score += 5
            elif slot.confidence_level == "medium":
                score += 3
            
            scored_slots.append((slot, score))
        
        # Sort by score (highest first)
        scored_slots.sort(key=lambda x: x[1], reverse=True)
        
        # Return top slots
        return [slot for slot, score in scored_slots]

# Initialize availability checker service
availability_checker = AvailabilityChecker()

async def get_interviewer_availability(
    interviewer_id: str,
    check_date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
    start_hour: int = Query(9, ge=0, le=23, description="Start hour (24-hour format)"),
    end_hour: int = Query(18, ge=0, le=23, description="End hour (24-hour format)"),
    min_slot_duration: int = Query(30, ge=15, le=240, description="Minimum slot duration in minutes"),
    timezone: str = Query("UTC", description="Timezone for the availability check"),
    include_tentative: bool = Query(False, description="Include tentative calendar events"),
    db: Session = Depends(get_db)
) -> AvailabilityResponse:
    """
    Check interviewer availability on a specific date
    
    This endpoint:
    - Checks Google Calendar for busy times on the specified date
    - Returns available time slots between working hours (default 9 AM - 6 PM)
    - Considers existing interviews and calendar conflicts
    - Formats response as array of available time ranges with confidence levels
    - Provides recommendations for optimal interview scheduling
    
    Args:
        interviewer_id: Unique identifier for the interviewer
        check_date: Date to check availability (must be today or future)
        start_hour: Start of working hours (0-23, default 9)
        end_hour: End of working hours (0-23, default 18)
        min_slot_duration: Minimum duration for available slots (15-240 minutes)
        timezone: Timezone for calculations (default UTC)
        include_tentative: Whether to consider tentative calendar events as busy
        
    Returns:
        AvailabilityResponse with:
        - List of available time slots with confidence levels
        - Busy periods from calendar and existing interviews
        - Availability statistics and recommendations
        - Interviewer information and working hours
    """
    
    try:
        logger.info(f"🔍 Availability request for interviewer {interviewer_id}")
        logger.info(f"   Date: {check_date}, Hours: {start_hour}-{end_hour}")
        
        # Validate request parameters
        if end_hour <= start_hour:
            raise HTTPException(
                status_code=400,
                detail="End hour must be after start hour"
            )
        
        if check_date < date.today():
            raise HTTPException(
                status_code=400,
                detail="Cannot check availability for past dates"
            )
        
        # Check availability using the service
        availability = await availability_checker.check_availability(
            interviewer_id=interviewer_id,
            check_date=check_date,
            start_hour=start_hour,
            end_hour=end_hour,
            min_slot_duration=min_slot_duration,
            timezone=timezone,
            include_tentative=include_tentative,
            db=db
        )
        
        return availability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Availability check failed: {e}")
        logger.exception("Availability error details:")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check availability: {str(e)}"
        )

# Additional helper endpoints

async def get_multiple_interviewer_availability(
    interviewer_ids: List[str],
    check_date: date,
    start_hour: int = 9,
    end_hour: int = 18,
    min_slot_duration: int = 60,
    timezone: str = "UTC",
    db: Session = Depends(get_db)
) -> Dict[str, AvailabilityResponse]:
    """
    Check availability for multiple interviewers at once
    
    Useful for finding optimal meeting times with multiple participants
    """
    
    results = {}
    
    for interviewer_id in interviewer_ids:
        try:
            availability = await availability_checker.check_availability(
                interviewer_id=interviewer_id,
                check_date=check_date,
                start_hour=start_hour,
                end_hour=end_hour,
                min_slot_duration=min_slot_duration,
                timezone=timezone,
                db=db
            )
            results[interviewer_id] = availability
            
        except Exception as e:
            logger.error(f"Failed to check availability for {interviewer_id}: {e}")
            results[interviewer_id] = None
    
    return results

async def find_common_availability(
    interviewer_ids: List[str],
    check_date: date,
    min_slot_duration: int = 60,
    timezone: str = "UTC",
    db: Session = Depends(get_db)
) -> List[AvailableTimeSlot]:
    """
    Find time slots when all specified interviewers are available
    
    Useful for panel interviews or multi-interviewer sessions
    """
    
    try:
        # Get availability for all interviewers
        all_availability = await get_multiple_interviewer_availability(
            interviewer_ids, check_date, 9, 18, min_slot_duration, timezone, db
        )
        
        # Find intersection of all available slots
        common_slots = []
        
        if all(av is not None for av in all_availability.values()):
            # Get all available slots from first interviewer
            base_slots = list(all_availability.values())[0].available_slots
            
            for slot in base_slots:
                # Check if this slot overlaps with all other interviewers' availability
                is_common = True
                
                for interviewer_id, availability in all_availability.items():
                    if availability is None:
                        is_common = False
                        break
                    
                    # Check if any of this interviewer's slots overlaps with the base slot
                    has_overlap = any(
                        (slot.start_time < other_slot.end_time and 
                         slot.end_time > other_slot.start_time)
                        for other_slot in availability.available_slots
                    )
                    
                    if not has_overlap:
                        is_common = False
                        break
                
                if is_common:
                    # Calculate the actual overlapping time
                    overlap_start = slot.start_time
                    overlap_end = slot.end_time
                    
                    # Narrow down to the actual common time
                    for availability in all_availability.values():
                        for other_slot in availability.available_slots:
                            if (slot.start_time < other_slot.end_time and 
                                slot.end_time > other_slot.start_time):
                                overlap_start = max(overlap_start, other_slot.start_time)
                                overlap_end = min(overlap_end, other_slot.end_time)
                    
                    # Check if the overlap is long enough
                    overlap_duration = (overlap_end - overlap_start).total_seconds() / 60
                    if overlap_duration >= min_slot_duration:
                        common_slot = AvailableTimeSlot(
                            start_time=overlap_start,
                            end_time=overlap_end,
                            duration_minutes=int(overlap_duration),
                            slot_id=f"common_{len(common_slots) + 1}",
                            confidence_level="high",
                            notes=f"Available for all {len(interviewer_ids)} interviewers"
                        )
                        common_slots.append(common_slot)
        
        return common_slots
        
    except Exception as e:
        logger.error(f"Error finding common availability: {e}")
        return []

# Export availability components
__all__ = [
    'get_interviewer_availability',
    'get_multiple_interviewer_availability', 
    'find_common_availability',
    'AvailabilityRequest',
    'AvailabilityResponse',
    'AvailableTimeSlot',
    'BusyTimeSlot',
    'AvailabilityChecker'
]
