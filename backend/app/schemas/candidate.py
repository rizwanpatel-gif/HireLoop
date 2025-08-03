"""
Centralized Pydantic schemas for RHero Interview Management System
=================================================================

This file contains all API request/response models to ensure consistency
across the entire application.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


# Enums
class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
class CandidateStatus(str, Enum):
    SUBMITTED = "submitted"
    ANALYZING = "analyzing" 
    ANALYZED = "analyzed"
    SCHEDULED = "scheduled"
    INTERVIEWED = "interviewed"
    HIRED = "hired"
    REJECTED = "rejected"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURAL_FIT = "cultural_fit"
    FINAL = "final"
    PHONE_SCREENING = "phone_screening"


# AI Service Classes (for compatibility with automation)
@dataclass
class CandidateSkill:
    """Individual skill with level and experience"""
    name: str
    level: SkillLevel
    years_experience: float = 0
    projects_count: int = 0
    certifications: List[str] = None
    
    def __post_init__(self):
        if self.certifications is None:
            self.certifications = []

@dataclass
class CandidateProfile:
    """Complete candidate profile for AI analysis"""
    name: str
    email: str
    position: str
    experience_years: float
    skills: List[CandidateSkill]
    education: str
    previous_companies: List[str]
    github_url: str = ""
    linkedin_url: str = ""
    portfolio_url: str = ""
    cover_letter: str = ""
    resume_text: str = ""
    preferred_salary: float = 0.0
    availability: str = ""
    
    def __post_init__(self):
        if isinstance(self.skills, list) and self.skills and isinstance(self.skills[0], dict):
            # Convert dict skills to CandidateSkill objects
            self.skills = [
                CandidateSkill(
                    name=skill.get('name', ''),
                    level=SkillLevel(skill.get('level', 'intermediate')),
                    years_experience=skill.get('years_experience', 0),
                    projects_count=skill.get('projects_count', 0),
                    certifications=skill.get('certifications', [])
                ) for skill in self.skills
            ]


# Skills Schema
class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Skill name")
    level: str = Field(..., description="Skill level: beginner, intermediate, advanced, expert")
    years_experience: float = Field(0, ge=0, le=50, description="Years of experience with this skill")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v.lower() not in valid_levels:
            raise ValueError(f'Level must be one of: {", ".join(valid_levels)}')
        return v.lower()

class SkillResponse(SkillCreate):
    pass


# Candidate Schemas
class CandidateCreate(BaseModel):
    """
    Simple candidate creation schema matching your requirements:
    - Name, Email, Current Title, Skills, Resume Summary, Interview Date
    """
    name: str = Field(..., min_length=1, max_length=255, description="Candidate full name")
    email: EmailStr = Field(..., description="Candidate email address")
    current_title: str = Field(..., min_length=1, max_length=255, description="Current job title/position")
    skills: List[str] = Field(..., min_items=1, description="List of technical skills")
    resume_summary: str = Field(..., min_length=10, description="Resume summary or key highlights")
    preferred_interview_date: Optional[datetime] = Field(None, description="Preferred date for interview scheduling")
    
    # Optional fields
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    location: Optional[str] = Field(None, max_length=255, description="Current location")
    experience_years: Optional[float] = Field(None, ge=0, le=50, description="Total years of experience")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CandidateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    current_title: Optional[str] = Field(None, min_length=1, max_length=255)
    skills: Optional[List[str]] = None
    resume_summary: Optional[str] = None
    preferred_interview_date: Optional[datetime] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[float] = Field(None, ge=0, le=50)
    status: Optional[CandidateStatus] = None

class CandidateResponse(BaseModel):
    id: int = Field(..., description="Candidate ID")
    name: str
    email: str
    current_title: str = Field(alias="position")  # Map position to current_title
    skills: List[str]
    resume_summary: str = Field(alias="resume_text")  # Map resume_text to resume_summary
    status: CandidateStatus
    
    # Additional fields
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[float] = None
    preferred_interview_date: Optional[datetime] = Field(alias="interview_datetime")
    
    # Analysis results
    ai_analysis_status: Optional[str] = None
    ai_overall_score: Optional[float] = None
    ai_technical_score: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CandidateDetailResponse(CandidateResponse):
    """Extended candidate response with full details"""
    # Full AI analysis
    ai_experience_score: Optional[float] = None
    ai_cultural_fit_score: Optional[float] = None
    ai_analysis_results: Optional[Dict[str, Any]] = None
    ai_confidence_score: Optional[float] = None
    
    # Scheduling info
    interview_scheduled: bool = False
    interview_type: Optional[str] = None
    matched_interviewers: Optional[List[Dict[str, Any]]] = None
    
    # Notes and flags
    recruiter_notes: Optional[str] = None
    red_flags: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    analyzed_at: Optional[datetime] = None

class CandidateListResponse(BaseModel):
    """Response for listing candidates with pagination"""
    candidates: List[CandidateResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


# Interview Schemas
class InterviewCreate(BaseModel):
    candidate_id: int = Field(..., description="ID of the candidate")
    interviewer_id: Optional[int] = Field(None, description="ID of the interviewer")
    scheduled_time: datetime = Field(..., description="Interview date and time")
    duration: int = Field(60, ge=15, le=240, description="Duration in minutes")
    type: InterviewType = Field(InterviewType.TECHNICAL, description="Type of interview")
    notes: Optional[str] = Field(None, description="Additional notes")

class InterviewUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=15, le=240)
    type: Optional[InterviewType] = None
    status: Optional[InterviewStatus] = None
    notes: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=10)

class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    interviewer_id: Optional[int] = None
    scheduled_time: datetime
    duration: int
    type: InterviewType
    status: InterviewStatus
    notes: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    interviewer_name: Optional[str] = None

class InterviewScheduleRequest(BaseModel):
    """Request to schedule an interview"""
    candidate_id: int
    interviewer_id: Optional[int] = None
    scheduled_time: datetime
    duration: int = Field(60, ge=15, le=240)
    interview_type: InterviewType = InterviewType.TECHNICAL
    notes: Optional[str] = None

class InterviewConfirmationResponse(BaseModel):
    """Response after scheduling an interview"""
    success: bool
    message: str
    interview: InterviewResponse
    calendar_event_id: Optional[str] = None


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_candidates: int
    total_interviews: int
    interviews_today: int
    interviews_this_week: int
    pending_analysis: int
    success_rate: float

class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_candidates: List[CandidateResponse]
    upcoming_interviews: List[InterviewResponse]


# Error Responses
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ValidationErrorResponse(BaseModel):
    error: str = "validation_error"
    message: str
    field_errors: List[Dict[str, str]]


# Success Responses
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
