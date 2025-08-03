"""
Interview Scheduling API Components
Basic implementation for interview scheduling functionality
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Enums
class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    HR = "hr"
    FINAL = "final"

# Pydantic Models
class InterviewScheduleRequest(BaseModel):
    candidate_id: str
    interviewer_id: str
    interview_type: InterviewType
    scheduled_time: datetime
    duration_minutes: int = 60
    notes: Optional[str] = None

class InterviewResponse(BaseModel):
    id: str
    candidate_id: str
    interviewer_id: str
    interview_type: InterviewType
    scheduled_time: datetime
    status: InterviewStatus
    duration_minutes: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class InterviewConfirmationResponse(BaseModel):
    interview_id: str
    status: InterviewStatus
    confirmed_at: datetime
    message: str

# Database Model (placeholder)
class InterviewDB:
    """Placeholder database model for interviews"""
    def __init__(self):
        self.interviews: Dict[str, Dict[str, Any]] = {}
    
    def create_interview(self, interview_data: dict) -> str:
        interview_id = f"int_{len(self.interviews) + 1}"
        self.interviews[interview_id] = interview_data
        return interview_id
    
    def get_interview(self, interview_id: str) -> Optional[dict]:
        return self.interviews.get(interview_id)
    
    def update_interview(self, interview_id: str, updates: dict):
        if interview_id in self.interviews:
            self.interviews[interview_id].update(updates)
    
    def list_interviews(self) -> List[dict]:
        return list(self.interviews.values())

# Global database instance
interview_db = InterviewDB()

# API Functions
def schedule_interview_endpoint(request: InterviewScheduleRequest) -> InterviewResponse:
    """Schedule a new interview"""
    interview_data = {
        "candidate_id": request.candidate_id,
        "interviewer_id": request.interviewer_id,
        "interview_type": request.interview_type,
        "scheduled_time": request.scheduled_time,
        "duration_minutes": request.duration_minutes,
        "notes": request.notes,
        "status": InterviewStatus.SCHEDULED,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    interview_id = interview_db.create_interview(interview_data)
    interview_data["id"] = interview_id
    
    return InterviewResponse(**interview_data)

def get_interview_status(interview_id: str) -> Optional[InterviewResponse]:
    """Get the status of a specific interview"""
    interview_data = interview_db.get_interview(interview_id)
    if interview_data:
        return InterviewResponse(**interview_data)
    return None

def list_scheduled_interviews() -> List[InterviewResponse]:
    """List all scheduled interviews"""
    interviews = interview_db.list_interviews()
    return [InterviewResponse(**interview) for interview in interviews]

def confirm_interview(interview_id: str) -> InterviewConfirmationResponse:
    """Confirm an interview"""
    interview = interview_db.get_interview(interview_id)
    if not interview:
        raise ValueError(f"Interview {interview_id} not found")
    
    interview_db.update_interview(interview_id, {
        "status": InterviewStatus.CONFIRMED,
        "updated_at": datetime.now()
    })
    
    return InterviewConfirmationResponse(
        interview_id=interview_id,
        status=InterviewStatus.CONFIRMED,
        confirmed_at=datetime.now(),
        message="Interview confirmed successfully"
    )

def cancel_interview(interview_id: str) -> InterviewConfirmationResponse:
    """Cancel an interview"""
    interview = interview_db.get_interview(interview_id)
    if not interview:
        raise ValueError(f"Interview {interview_id} not found")
    
    interview_db.update_interview(interview_id, {
        "status": InterviewStatus.CANCELLED,
        "updated_at": datetime.now()
    })
    
    return InterviewConfirmationResponse(
        interview_id=interview_id,
        status=InterviewStatus.CANCELLED,
        confirmed_at=datetime.now(),
        message="Interview cancelled successfully"
    )
