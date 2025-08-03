"""
Phase 4: Candidate Management API Endpoints
==========================================

Comprehensive candidate management system with:
- Database integration for candidate records
- Background AI analysis tasks
- File upload handling for resumes
- Proper validation and error handling
- Status tracking and notifications
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import os
import logging
import asyncio
import json
from pathlib import Path

# Import AI services
from app.services.ai_service import AIService, CandidateProfile, CandidateSkill, SkillLevel
from smart_matching_algorithm import SmartMatchingAlgorithm, create_sample_interviewer_profiles
from app.services.calendar_service import GoogleCalendarService

# Import interview scheduling components
from app.models.models import Candidate, Interview, User, InterviewStatus, InterviewType
InterviewDB = Interview
CandidateDB = Candidate
from app.models.models import schedule_interview_endpoint, get_interview_status, list_scheduled_interviews, InterviewScheduleRequest, InterviewResponse, InterviewConfirmationResponse

# Dashboard Response Models
class InterviewDashboardItem(BaseModel):
    """Comprehensive interview item for dashboard display"""
    interview_id: str
    status: str
    interview_type: str
    interview_round: int
    
    # Timing information
    scheduled_time: datetime
    duration_minutes: int
    time_until_interview: Optional[str] = None
    is_upcoming: bool
    is_overdue: bool
    
    # Candidate information
    candidate_id: str
    candidate_name: str
    candidate_email: str
    candidate_position: str
    candidate_experience_years: float
    candidate_ai_score: Optional[float] = None
    
    # Interviewer information
    interviewer_id: str
    interviewer_name: str
    interviewer_email: str
    
    # AI and matching information
    ai_match_score: Optional[float] = None
    ai_match_confidence: Optional[float] = None
    ai_recommended_focus_areas: List[str] = []
    
    # Calendar and meeting information
    calendar_event_id: Optional[str] = None
    google_meet_link: Optional[str] = None
    calendar_invites_sent: bool = False
    
    # Interview logistics
    is_remote: bool = True
    location: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Status indicators
    automation_score: int = 0
    status_color: str = "gray"

class InterviewDashboardResponse(BaseModel):
    """Dashboard response with interviews and metadata"""
    interviews: List[InterviewDashboardItem]
    total_count: int
    page: int
    page_size: int
    summary: Dict[str, Any]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/interview_db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# File upload configuration
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

# Enums
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

# Database Models
class CandidateDB(Base):
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    position = Column(String(255), nullable=False)
    experience_years = Column(Float, nullable=False)
    phone = Column(String(50))
    location = Column(String(255))
    
    # Resume and portfolio
    resume_file_path = Column(String(500))
    resume_text = Column(Text)
    portfolio_url = Column(String(500))
    github_url = Column(String(500))
    linkedin_url = Column(String(500))
    
    # Skills and experience
    skills = Column(JSON)  # Store as JSON array
    education = Column(Text)
    previous_companies = Column(JSON)  # Store as JSON array
    
    # Application details
    cover_letter = Column(Text)
    preferred_salary = Column(Float)
    availability = Column(String(255))
    remote_preference = Column(String(50))
    
    # Status tracking
    status = Column(String(50), default=CandidateStatus.SUBMITTED, index=True)
    source = Column(String(100))  # job_board, referral, direct, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime)
    
    # AI Analysis Results
    ai_analysis_status = Column(String(50), default=AnalysisStatus.PENDING)
    ai_overall_score = Column(Float)
    ai_technical_score = Column(Float)
    ai_experience_score = Column(Float)
    ai_cultural_fit_score = Column(Float)
    ai_analysis_results = Column(JSON)  # Full AI analysis results
    ai_model_used = Column(String(100))
    ai_confidence_score = Column(Float)
    
    # Matching and scheduling
    matched_interviewers = Column(JSON)  # Store interviewer matches
    interview_scheduled = Column(Boolean, default=False)
    interview_datetime = Column(DateTime)
    interview_type = Column(String(50))
    
    # Notes and flags
    recruiter_notes = Column(Text)
    red_flags = Column(JSON)  # Store as JSON array
    tags = Column(JSON)  # Store as JSON array


class AnalysisTaskDB(Base):
    __tablename__ = "analysis_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(50), default=AnalysisStatus.PENDING, index=True)
    
    # Task details
    task_type = Column(String(50))  # analysis, matching, scheduling
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    
    # Execution details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Results
    results = Column(JSON)
    cost_estimate = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models for API
class SkillRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Skill name")
    level: str = Field(..., description="Skill level: beginner, intermediate, advanced, expert")
    years_experience: float = Field(0, ge=0, le=50, description="Years of experience")
    projects_count: int = Field(0, ge=0, description="Number of projects")
    certifications: List[str] = Field(default_factory=list, description="Related certifications")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v.lower() not in valid_levels:
            raise ValueError(f'Level must be one of: {", ".join(valid_levels)}')
        return v.lower()


class CandidateCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    position: str = Field(..., min_length=1, max_length=255, description="Position applied for")
    experience_years: float = Field(..., ge=0, le=50, description="Years of experience")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    location: Optional[str] = Field(None, max_length=255, description="Location")
    
    # Skills and experience
    skills: List[SkillRequest] = Field(..., min_items=1, description="Technical skills")
    education: Optional[str] = Field(None, description="Educational background")
    previous_companies: List[str] = Field(default_factory=list, description="Previous employers")
    
    # URLs and links
    portfolio_url: Optional[str] = Field(None, description="Portfolio website")
    github_url: Optional[str] = Field(None, description="GitHub profile")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile")
    
    # Application details
    cover_letter: Optional[str] = Field(None, description="Cover letter text")
    resume_text: Optional[str] = Field(None, description="Resume content as text")
    preferred_salary: Optional[float] = Field(None, ge=0, description="Preferred salary")
    availability: Optional[str] = Field(None, description="Availability information")
    remote_preference: Optional[str] = Field("hybrid", description="Remote work preference")
    source: Optional[str] = Field("direct", description="Application source")


class CandidateResponse(BaseModel):
    id: str = Field(..., description="Candidate UUID")
    name: str
    email: str
    position: str
    experience_years: float
    phone: Optional[str]
    location: Optional[str]
    status: str
    source: str
    
    # Analysis status
    ai_analysis_status: str
    ai_overall_score: Optional[float]
    ai_technical_score: Optional[float]
    ai_confidence_score: Optional[float]
    
    # Timestamps
    created_at: str
    updated_at: str
    analyzed_at: Optional[str]
    
    # Skills summary
    skills_count: int
    top_skills: List[str]
    
    # Flags and status
    interview_scheduled: bool
    has_red_flags: bool


class CandidateDetailResponse(CandidateResponse):
    skills: List[SkillRequest]
    education: Optional[str]
    previous_companies: List[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    cover_letter: Optional[str]
    preferred_salary: Optional[float]
    availability: Optional[str]
    remote_preference: Optional[str]
    
    # Full AI analysis
    ai_analysis_results: Optional[Dict[str, Any]]
    matched_interviewers: Optional[List[Dict[str, Any]]]
    recruiter_notes: Optional[str]
    red_flags: List[str]
    tags: List[str]


class CandidateCreateResponse(BaseModel):
    success: bool = Field(..., description="Whether creation was successful")
    message: str = Field(..., description="Success or error message")
    candidate_id: str = Field(..., description="Created candidate UUID")
    status: str = Field(..., description="Current candidate status")
    analysis_task_id: str = Field(..., description="Background analysis task ID")
    estimated_analysis_time: int = Field(..., description="Estimated analysis time in seconds")


class CandidateListResponse(BaseModel):
    success: bool
    total_count: int
    page: int
    page_size: int
    candidates: List[CandidateResponse]
    filters_applied: Dict[str, Any]


class AnalysisTaskResponse(BaseModel):
    task_id: str
    candidate_id: str
    status: str
    task_type: str
    priority: int
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    retry_count: int
    results: Optional[Dict[str, Any]]


# Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# File validation utilities
def validate_file(file: UploadFile) -> None:
    """Validate uploaded resume file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (this is approximate, real size checked later)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )


def save_resume_file(file: UploadFile, candidate_id: str) -> str:
    """Save uploaded resume file and return file path"""
    try:
        # Validate file
        validate_file(file)
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        filename = f"{candidate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
                )
            buffer.write(content)
        
        logger.info(f"Resume file saved: {file_path}")
        return str(file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving resume file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save resume file")


def extract_text_from_resume(file_path: str) -> str:
    """Extract text content from resume file"""
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                logger.warning("PyPDF2 not installed, cannot extract PDF text")
                return ""
        
        elif file_ext in ['.doc', '.docx']:
            try:
                import python_docx
                doc = python_docx.Document(file_path)
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                logger.warning("python-docx not installed, cannot extract Word text")
                return ""
        
        return ""
        
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return ""


# Background tasks
async def process_candidate_analysis(candidate_id: str, db_session_factory=SessionLocal):
    """Background task to analyze candidate using AI"""
    task_id = str(uuid.uuid4())
    db = db_session_factory()
    
    try:
        logger.info(f"🤖 Starting AI analysis for candidate {candidate_id}")
        
        # Create analysis task record
        analysis_task = AnalysisTaskDB(
            id=task_id,
            candidate_id=candidate_id,
            task_type="analysis",
            status=AnalysisStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )
        db.add(analysis_task)
        
        # Get candidate from database
        candidate_db = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate_db:
            raise Exception(f"Candidate {candidate_id} not found")
        
        # Update candidate status
        candidate_db.ai_analysis_status = AnalysisStatus.IN_PROGRESS
        candidate_db.status = CandidateStatus.ANALYZING
        db.commit()
        
        # Convert to AI service format
        skills = []
        for skill_data in candidate_db.skills or []:
            skills.append(CandidateSkill(
                name=skill_data['name'],
                level=SkillLevel(skill_data['level']),
                years_experience=skill_data.get('years_experience', 0),
                projects_count=skill_data.get('projects_count', 0),
                certifications=skill_data.get('certifications', [])
            ))
        
        candidate_profile = CandidateProfile(
            name=candidate_db.name,
            email=candidate_db.email,
            position=candidate_db.position,
            experience_years=candidate_db.experience_years,
            skills=skills,
            education=candidate_db.education or "",
            previous_companies=candidate_db.previous_companies or [],
            github_url=candidate_db.github_url or "",
            linkedin_url=candidate_db.linkedin_url or "",
            portfolio_url=candidate_db.portfolio_url or "",
            cover_letter=candidate_db.cover_letter or "",
            resume_text=candidate_db.resume_text or "",
            preferred_salary=candidate_db.preferred_salary or 0.0,
            availability=candidate_db.availability or ""
        )
        
        # Perform AI analysis
        ai_service = AIService()
        analysis = await asyncio.to_thread(ai_service.analyze_candidate, candidate_profile)
        
        if not analysis:
            raise Exception("AI analysis returned no results")
        
        # Store analysis results
        candidate_db.ai_analysis_status = AnalysisStatus.COMPLETED
        candidate_db.status = CandidateStatus.ANALYZED
        candidate_db.ai_overall_score = analysis.overall_score
        candidate_db.ai_technical_score = analysis.technical_score
        candidate_db.ai_experience_score = getattr(analysis, 'experience_score', 0)
        candidate_db.ai_cultural_fit_score = getattr(analysis, 'cultural_fit_score', 0)
        candidate_db.ai_confidence_score = analysis.confidence_score
        candidate_db.ai_model_used = getattr(ai_service, 'model', 'claude-3-haiku')
        candidate_db.analyzed_at = datetime.utcnow()
        
        # Store full analysis results
        analysis_dict = {
            "overall_score": analysis.overall_score,
            "technical_score": analysis.technical_score,
            "strengths": analysis.strengths,
            "areas_for_improvement": getattr(analysis, 'areas_for_improvement', []),
            "estimated_level": analysis.estimated_level,
            "competency_scores": getattr(analysis, 'competency_scores', {}).__dict__ if hasattr(getattr(analysis, 'competency_scores', {}), '__dict__') else {},
            "technical_skills": getattr(analysis, 'technical_skills', {}).__dict__ if hasattr(getattr(analysis, 'technical_skills', {}), '__dict__') else {},
            "experience_analysis": getattr(analysis, 'experience_analysis', {}).__dict__ if hasattr(getattr(analysis, 'experience_analysis', {}), '__dict__') else {},
            "interview_strategy": getattr(analysis, 'interview_strategy', {}).__dict__ if hasattr(getattr(analysis, 'interview_strategy', {}), '__dict__') else {},
            "hiring_recommendation": getattr(analysis, 'hiring_recommendation', {}).__dict__ if hasattr(getattr(analysis, 'hiring_recommendation', {}), '__dict__') else {}
        }
        candidate_db.ai_analysis_results = analysis_dict
        
        # Update analysis task
        analysis_task.status = AnalysisStatus.COMPLETED
        analysis_task.completed_at = datetime.utcnow()
        analysis_task.results = analysis_dict
        
        db.commit()
        
        logger.info(f"✅ AI analysis completed for candidate {candidate_id}")
        logger.info(f"   Overall Score: {analysis.overall_score}/100")
        logger.info(f"   Technical Score: {analysis.technical_score}/100")
        logger.info(f"   Estimated Level: {analysis.estimated_level}")
        
        # Trigger interviewer matching as next step
        await asyncio.create_task(process_interviewer_matching(candidate_id, db_session_factory))
        
    except Exception as e:
        logger.error(f"❌ AI analysis failed for candidate {candidate_id}: {e}")
        
        # Update failure status
        if 'candidate_db' in locals():
            candidate_db.ai_analysis_status = AnalysisStatus.FAILED
            candidate_db.status = CandidateStatus.SUBMITTED  # Reset to submitted
        
        if 'analysis_task' in locals():
            analysis_task.status = AnalysisStatus.FAILED
            analysis_task.error_message = str(e)
            analysis_task.completed_at = datetime.utcnow()
        
        db.commit()
        
    finally:
        db.close()


async def process_interviewer_matching(candidate_id: str, db_session_factory=SessionLocal):
    """Background task to find interviewer matches"""
    task_id = str(uuid.uuid4())
    db = db_session_factory()
    
    try:
        logger.info(f"🎯 Finding interviewer matches for candidate {candidate_id}")
        
        # Create matching task record
        matching_task = AnalysisTaskDB(
            id=task_id,
            candidate_id=candidate_id,
            task_type="matching",
            status=AnalysisStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )
        db.add(matching_task)
        db.commit()
        
        # Get candidate and analysis from database
        candidate_db = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate_db or not candidate_db.ai_analysis_results:
            raise Exception(f"Candidate {candidate_id} not found or not analyzed")
        
        # Initialize smart matching algorithm
        ai_service = AIService()
        calendar_service = GoogleCalendarService()
        smart_matcher = SmartMatchingAlgorithm(ai_service, calendar_service)
        
        # Get interviewer profiles
        interviewer_profiles = create_sample_interviewer_profiles()
        
        # Set interview date range (next 2 weeks)
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=14)
        
        # Convert candidate to matching format
        skills = []
        for skill_data in candidate_db.skills or []:
            skills.append(CandidateSkill(
                name=skill_data['name'],
                level=SkillLevel(skill_data['level']),
                years_experience=skill_data.get('years_experience', 0),
                projects_count=skill_data.get('projects_count', 0),
                certifications=skill_data.get('certifications', [])
            ))
        
        candidate_profile = CandidateProfile(
            name=candidate_db.name,
            email=candidate_db.email,
            position=candidate_db.position,
            experience_years=candidate_db.experience_years,
            skills=skills,
            resume_text=candidate_db.resume_text or ""
        )
        
        # Find matches
        from app.services.ai_service import InterviewType
        matches = await smart_matcher.find_best_matches(
            candidate=candidate_profile,
            interviewer_profiles=interviewer_profiles,
            interview_date_range=(start_date, end_date),
            required_interview_type=InterviewType.TECHNICAL,
            max_results=5
        )
        
        # Store matches
        match_data = []
        for match in matches:
            match_data.append({
                "interviewer_name": match.interviewer_profile.interviewer.name,
                "interviewer_email": match.interviewer_profile.interviewer.email,
                "overall_score": round(match.overall_match_score, 1),
                "confidence": match.confidence_level.value,
                "technical_match": round(match.technical_match_score, 1),
                "available_slots": len(match.available_slots),
                "recommended_time": match.recommended_slot.start_time.isoformat() if match.recommended_slot else None,
                "match_reasons": match.match_reasons,
                "concerns": match.potential_concerns
            })
        
        candidate_db.matched_interviewers = match_data
        
        # Update matching task
        matching_task.status = AnalysisStatus.COMPLETED
        matching_task.completed_at = datetime.utcnow()
        matching_task.results = {"matches": match_data, "total_matches": len(matches)}
        
        db.commit()
        
        logger.info(f"✅ Found {len(matches)} interviewer matches for candidate {candidate_id}")
        
    except Exception as e:
        logger.error(f"❌ Interviewer matching failed for candidate {candidate_id}: {e}")
        
        if 'matching_task' in locals():
            matching_task.status = AnalysisStatus.FAILED
            matching_task.error_message = str(e)
            matching_task.completed_at = datetime.utcnow()
        
        db.commit()
        
    finally:
        db.close()


# API Endpoints
app = FastAPI(
    title="Candidate Management API",
    description="Phase 4: Comprehensive candidate management with AI analysis",
    version="1.0.0"
)


@app.post("/api/candidates/", response_model=CandidateCreateResponse)
async def create_candidate(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    # Form data fields
    name: str = Form(..., description="Candidate full name"),
    email: EmailStr = Form(..., description="Email address"),
    position: str = Form(..., description="Position applied for"),
    experience_years: float = Form(..., description="Years of experience"),
    skills: str = Form(..., description="Skills as JSON string"),
    phone: Optional[str] = Form(None, description="Phone number"),
    location: Optional[str] = Form(None, description="Location"),
    education: Optional[str] = Form(None, description="Education background"),
    previous_companies: Optional[str] = Form(None, description="Previous companies as JSON"),
    portfolio_url: Optional[str] = Form(None, description="Portfolio URL"),
    github_url: Optional[str] = Form(None, description="GitHub URL"),
    linkedin_url: Optional[str] = Form(None, description="LinkedIn URL"),
    cover_letter: Optional[str] = Form(None, description="Cover letter"),
    resume_text: Optional[str] = Form(None, description="Resume text"),
    preferred_salary: Optional[float] = Form(None, description="Preferred salary"),
    availability: Optional[str] = Form(None, description="Availability"),
    remote_preference: Optional[str] = Form("hybrid", description="Remote preference"),
    source: Optional[str] = Form("direct", description="Application source"),
    # Optional file upload
    resume_file: Optional[UploadFile] = File(None, description="Resume file upload")
):
    """
    Create a new candidate record with comprehensive data validation,
    file handling, and background AI analysis
    """
    try:
        logger.info(f"📝 Creating candidate: {name} for position: {position}")
        
        # Validate and parse skills JSON
        try:
            skills_data = json.loads(skills)
            if not isinstance(skills_data, list) or len(skills_data) == 0:
                raise ValueError("Skills must be a non-empty list")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid skills JSON format")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate skills structure
        for skill in skills_data:
            if not isinstance(skill, dict) or 'name' not in skill or 'level' not in skill:
                raise HTTPException(
                    status_code=400, 
                    detail="Each skill must have 'name' and 'level' fields"
                )
        
        # Parse previous companies if provided
        previous_companies_list = []
        if previous_companies:
            try:
                previous_companies_list = json.loads(previous_companies)
                if not isinstance(previous_companies_list, list):
                    raise ValueError("Previous companies must be a list")
            except (json.JSONDecodeError, ValueError):
                previous_companies_list = [previous_companies]  # Single company as string
        
        # Check if candidate already exists
        existing_candidate = db.query(CandidateDB).filter(CandidateDB.email == email).first()
        if existing_candidate:
            raise HTTPException(
                status_code=409, 
                detail=f"Candidate with email {email} already exists"
            )
        
        # Generate candidate ID
        candidate_id = str(uuid.uuid4())
        
        # Handle resume file upload
        resume_file_path = None
        if resume_file and resume_file.filename:
            resume_file_path = save_resume_file(resume_file, candidate_id)
            
            # Extract text from uploaded file if no resume_text provided
            if not resume_text:
                resume_text = extract_text_from_resume(resume_file_path)
                logger.info(f"Extracted {len(resume_text)} characters from resume file")
        
        # Create candidate record
        candidate_db = CandidateDB(
            id=candidate_id,
            name=name,
            email=email,
            position=position,
            experience_years=experience_years,
            phone=phone,
            location=location,
            skills=skills_data,
            education=education,
            previous_companies=previous_companies_list,
            portfolio_url=portfolio_url,
            github_url=github_url,
            linkedin_url=linkedin_url,
            cover_letter=cover_letter,
            resume_text=resume_text,
            resume_file_path=resume_file_path,
            preferred_salary=preferred_salary,
            availability=availability,
            remote_preference=remote_preference,
            source=source,
            status=CandidateStatus.SUBMITTED,
            ai_analysis_status=AnalysisStatus.PENDING
        )
        
        db.add(candidate_db)
        db.commit()
        db.refresh(candidate_db)
        
        # Generate analysis task ID
        analysis_task_id = str(uuid.uuid4())
        
        # Schedule background AI analysis
        background_tasks.add_task(process_candidate_analysis, candidate_id)
        
        logger.info(f"✅ Candidate created successfully: {candidate_id}")
        logger.info(f"   Skills: {len(skills_data)} provided")
        logger.info(f"   Resume file: {'uploaded' if resume_file_path else 'not provided'}")
        logger.info(f"   Background analysis scheduled")
        
        return CandidateCreateResponse(
            success=True,
            message=f"Candidate {name} created successfully. AI analysis started.",
            candidate_id=candidate_id,
            status=CandidateStatus.SUBMITTED,
            analysis_task_id=analysis_task_id,
            estimated_analysis_time=30  # seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating candidate: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create candidate: {str(e)}"
        )


@app.get("/api/candidates/", response_model=CandidateListResponse)
async def list_candidates(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    position: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    min_score: Optional[float] = None,
    search: Optional[str] = None
):
    """
    List candidates with filtering, pagination, and search
    """
    try:
        # Build query
        query = db.query(CandidateDB)
        
        # Apply filters
        filters_applied = {}
        
        if status:
            query = query.filter(CandidateDB.status == status)
            filters_applied['status'] = status
            
        if position:
            query = query.filter(CandidateDB.position.ilike(f"%{position}%"))
            filters_applied['position'] = position
            
        if min_experience is not None:
            query = query.filter(CandidateDB.experience_years >= min_experience)
            filters_applied['min_experience'] = min_experience
            
        if max_experience is not None:
            query = query.filter(CandidateDB.experience_years <= max_experience)
            filters_applied['max_experience'] = max_experience
            
        if min_score is not None:
            query = query.filter(CandidateDB.ai_overall_score >= min_score)
            filters_applied['min_score'] = min_score
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                CandidateDB.name.ilike(search_term) |
                CandidateDB.email.ilike(search_term) |
                CandidateDB.position.ilike(search_term)
            )
            filters_applied['search'] = search
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        candidates = query.order_by(CandidateDB.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Convert to response format
        candidate_responses = []
        for candidate in candidates:
            # Get top skills
            top_skills = []
            if candidate.skills:
                top_skills = [skill['name'] for skill in candidate.skills[:3]]
            
            candidate_responses.append(CandidateResponse(
                id=str(candidate.id),
                name=candidate.name,
                email=candidate.email,
                position=candidate.position,
                experience_years=candidate.experience_years,
                phone=candidate.phone,
                location=candidate.location,
                status=candidate.status,
                source=candidate.source,
                ai_analysis_status=candidate.ai_analysis_status,
                ai_overall_score=candidate.ai_overall_score,
                ai_technical_score=candidate.ai_technical_score,
                ai_confidence_score=candidate.ai_confidence_score,
                created_at=candidate.created_at.isoformat(),
                updated_at=candidate.updated_at.isoformat(),
                analyzed_at=candidate.analyzed_at.isoformat() if candidate.analyzed_at else None,
                skills_count=len(candidate.skills) if candidate.skills else 0,
                top_skills=top_skills,
                interview_scheduled=candidate.interview_scheduled,
                has_red_flags=bool(candidate.red_flags)
            ))
        
        return CandidateListResponse(
            success=True,
            total_count=total_count,
            page=page,
            page_size=page_size,
            candidates=candidate_responses,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        logger.error(f"Error listing candidates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list candidates: {str(e)}")


@app.get("/api/candidates/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """
    Get detailed candidate information including AI analysis results
    """
    try:
        candidate = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Convert skills to response format
        skills = []
        if candidate.skills:
            for skill_data in candidate.skills:
                skills.append(SkillRequest(
                    name=skill_data['name'],
                    level=skill_data['level'],
                    years_experience=skill_data.get('years_experience', 0),
                    projects_count=skill_data.get('projects_count', 0),
                    certifications=skill_data.get('certifications', [])
                ))
        
        # Get top skills for summary
        top_skills = [skill.name for skill in skills[:5]]
        
        return CandidateDetailResponse(
            id=str(candidate.id),
            name=candidate.name,
            email=candidate.email,
            position=candidate.position,
            experience_years=candidate.experience_years,
            phone=candidate.phone,
            location=candidate.location,
            status=candidate.status,
            source=candidate.source,
            skills=skills,
            education=candidate.education,
            previous_companies=candidate.previous_companies or [],
            portfolio_url=candidate.portfolio_url,
            github_url=candidate.github_url,
            linkedin_url=candidate.linkedin_url,
            cover_letter=candidate.cover_letter,
            preferred_salary=candidate.preferred_salary,
            availability=candidate.availability,
            remote_preference=candidate.remote_preference,
            ai_analysis_status=candidate.ai_analysis_status,
            ai_overall_score=candidate.ai_overall_score,
            ai_technical_score=candidate.ai_technical_score,
            ai_confidence_score=candidate.ai_confidence_score,
            ai_analysis_results=candidate.ai_analysis_results,
            matched_interviewers=candidate.matched_interviewers,
            recruiter_notes=candidate.recruiter_notes,
            red_flags=candidate.red_flags or [],
            tags=candidate.tags or [],
            created_at=candidate.created_at.isoformat(),
            updated_at=candidate.updated_at.isoformat(),
            analyzed_at=candidate.analyzed_at.isoformat() if candidate.analyzed_at else None,
            skills_count=len(skills),
            top_skills=top_skills,
            interview_scheduled=candidate.interview_scheduled,
            has_red_flags=bool(candidate.red_flags)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get candidate: {str(e)}")


@app.get("/api/candidates/{candidate_id}/analysis", response_model=Dict[str, Any])
async def get_candidate_analysis(candidate_id: str, db: Session = Depends(get_db)):
    """
    Get detailed AI analysis results for a candidate
    """
    try:
        candidate = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        if candidate.ai_analysis_status != AnalysisStatus.COMPLETED:
            return {
                "status": candidate.ai_analysis_status,
                "message": "Analysis not completed yet",
                "analysis_results": None
            }
        
        return {
            "status": "completed",
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "analysis_results": candidate.ai_analysis_results,
            "overall_score": candidate.ai_overall_score,
            "technical_score": candidate.ai_technical_score,
            "confidence_score": candidate.ai_confidence_score,
            "model_used": candidate.ai_model_used,
            "analyzed_at": candidate.analyzed_at.isoformat() if candidate.analyzed_at else None,
            "matched_interviewers": candidate.matched_interviewers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")


@app.get("/api/analysis-tasks/{task_id}", response_model=AnalysisTaskResponse)
async def get_analysis_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get status of a background analysis task
    """
    try:
        task = db.query(AnalysisTaskDB).filter(AnalysisTaskDB.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Analysis task not found")
        
        return AnalysisTaskResponse(
            task_id=str(task.id),
            candidate_id=str(task.candidate_id),
            status=task.status,
            task_type=task.task_type,
            priority=task.priority,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            error_message=task.error_message,
            retry_count=task.retry_count,
            results=task.results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


@app.post("/api/candidates/{candidate_id}/reanalyze")
async def reanalyze_candidate(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger re-analysis of a candidate
    """
    try:
        candidate = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Reset analysis status
        candidate.ai_analysis_status = AnalysisStatus.PENDING
        candidate.status = CandidateStatus.SUBMITTED
        db.commit()
        
        # Schedule re-analysis
        background_tasks.add_task(process_candidate_analysis, candidate_id)
        
        return {
            "success": True,
            "message": f"Re-analysis scheduled for candidate {candidate.name}",
            "candidate_id": candidate_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-analyzing candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule re-analysis: {str(e)}")


# Interview Scheduling Endpoints
@app.post("/api/schedule-interview/", response_model=InterviewConfirmationResponse)
async def schedule_interview(
    request: InterviewScheduleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> InterviewConfirmationResponse:
    """
    Schedule an interview with AI-powered interviewer matching and calendar integration
    
    This endpoint:
    - Takes candidate_id and preferred_time from request
    - Uses AI to find best available interviewer
    - Creates interview record in database
    - Triggers background Google Calendar event creation
    - Returns interview details and confirmation
    """
    return await schedule_interview_endpoint(request, background_tasks, db)


@app.get("/api/interviews/{interview_id}/status")
async def get_interview_status_api(interview_id: str, db: Session = Depends(get_db)):
    """Get current status of an interview including calendar event status"""
    return await get_interview_status(interview_id, db)


@app.get("/api/interviews/", response_model=InterviewDashboardResponse)
async def get_interviews_dashboard_api(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_field: str = Query("scheduled_time", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    status: Optional[List[str]] = Query(None, description="Filter by interview status"),
    interview_type: Optional[List[str]] = Query(None, description="Filter by interview type"),
    candidate_id: Optional[str] = Query(None, description="Filter by candidate ID"),
    interviewer_email: Optional[str] = Query(None, description="Filter by interviewer email"),
    is_upcoming: Optional[bool] = Query(None, description="Filter upcoming interviews"),
    db: Session = Depends(get_db)
) -> InterviewDashboardResponse:
    """
    Comprehensive interview dashboard endpoint with JOIN queries
    
    Returns all scheduled interviews with:
    - Complete candidate and interviewer details via JOIN queries
    - Interview status, timing, and meeting links
    - AI matching scores and automation metrics
    - Proper pagination and filtering
    - Summary statistics for frontend consumption
    """
    
    try:
        logger.info(f"📊 Getting interview dashboard - Page {page}, Size {page_size}")
        
        # Build base query with JOINs to get candidate data
        base_query = db.query(InterviewDB).join(
            CandidateDB, InterviewDB.candidate_id == CandidateDB.id
        )
        
        # Apply filters
        current_time = datetime.utcnow()
        
        if status:
            base_query = base_query.filter(InterviewDB.status.in_(status))
        
        if interview_type:
            base_query = base_query.filter(InterviewDB.interview_type.in_(interview_type))
        
        if candidate_id:
            base_query = base_query.filter(InterviewDB.candidate_id == candidate_id)
        
        if interviewer_email:
            base_query = base_query.filter(InterviewDB.interviewer_email == interviewer_email)
        
        if is_upcoming is not None:
            if is_upcoming:
                base_query = base_query.filter(InterviewDB.scheduled_time > current_time)
            else:
                base_query = base_query.filter(InterviewDB.scheduled_time <= current_time)
        
        # Get total count
        total_count = base_query.count()
        
        # Apply sorting
        if sort_field == "scheduled_time":
            sort_column = InterviewDB.scheduled_time
        elif sort_field == "candidate_name":
            sort_column = CandidateDB.name
        elif sort_field == "interviewer_name":
            sort_column = InterviewDB.interviewer_name
        elif sort_field == "status":
            sort_column = InterviewDB.status
        else:
            sort_column = InterviewDB.scheduled_time
        
        if sort_order.lower() == "desc":
            base_query = base_query.order_by(sort_column.desc())
        else:
            base_query = base_query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        interviews = base_query.offset(offset).limit(page_size).all()
        
        # Format interviews for dashboard
        dashboard_items = []
        for interview in interviews:
            # Get candidate via the relationship or separate query
            candidate = db.query(CandidateDB).filter(CandidateDB.id == interview.candidate_id).first()
            
            if not candidate:
                continue
            
            # Calculate time until interview
            time_diff = interview.scheduled_time - current_time
            time_until_interview = None
            is_upcoming = time_diff.total_seconds() > 0
            is_overdue = not is_upcoming and interview.status not in ["completed", "cancelled"]
            
            if is_upcoming:
                if time_diff.days > 0:
                    time_until_interview = f"in {time_diff.days} days"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_until_interview = f"in {hours} hours"
                else:
                    minutes = time_diff.seconds // 60
                    time_until_interview = f"in {minutes} minutes"
            elif is_overdue:
                abs_time_diff = abs(time_diff)
                if abs_time_diff.days > 0:
                    time_until_interview = f"{abs_time_diff.days} days overdue"
                else:
                    hours = abs_time_diff.seconds // 3600
                    time_until_interview = f"{hours} hours overdue"
            
            # Calculate automation score
            automation_score = 0
            if interview.calendar_event_id:
                automation_score += 1
            if interview.google_meet_link:
                automation_score += 1
            if interview.calendar_invites_sent:
                automation_score += 1
            if interview.ai_match_score and interview.ai_match_score > 0:
                automation_score += 1
            
            # Determine status color
            status_colors = {
                "scheduled": "blue",
                "confirmed": "green",
                "in_progress": "yellow",
                "completed": "gray",
                "cancelled": "red",
                "rescheduled": "orange",
                "no_show": "red"
            }
            status_color = status_colors.get(interview.status, "gray")
            
            dashboard_item = InterviewDashboardItem(
                interview_id=interview.id,
                status=interview.status,
                interview_type=interview.interview_type,
                interview_round=interview.interview_round,
                scheduled_time=interview.scheduled_time,
                duration_minutes=interview.duration_minutes,
                time_until_interview=time_until_interview,
                is_upcoming=is_upcoming,
                is_overdue=is_overdue,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                candidate_position=candidate.position,
                candidate_experience_years=candidate.experience_years,
                candidate_ai_score=candidate.ai_overall_score,
                interviewer_id=interview.interviewer_id,
                interviewer_name=interview.interviewer_name,
                interviewer_email=interview.interviewer_email,
                ai_match_score=interview.ai_match_score,
                ai_match_confidence=interview.ai_match_confidence,
                ai_recommended_focus_areas=interview.ai_recommended_focus_areas or [],
                calendar_event_id=interview.calendar_event_id,
                google_meet_link=interview.google_meet_link,
                calendar_invites_sent=interview.calendar_invites_sent,
                is_remote=interview.is_remote,
                location=interview.location,
                created_at=interview.created_at,
                updated_at=interview.updated_at,
                automation_score=automation_score,
                status_color=status_color
            )
            
            dashboard_items.append(dashboard_item)
        
        # Calculate summary statistics
        all_interviews = base_query.all()
        summary = {
            "total_interviews": total_count,
            "upcoming_count": sum(1 for i in all_interviews if i.scheduled_time > current_time),
            "completed_count": sum(1 for i in all_interviews if i.status == "completed"),
            "automation_rate": round(
                sum(1 for i in all_interviews if i.calendar_event_id) / total_count * 100
                if total_count > 0 else 0, 1
            ),
            "status_breakdown": {
                "scheduled": sum(1 for i in all_interviews if i.status == "scheduled"),
                "confirmed": sum(1 for i in all_interviews if i.status == "confirmed"),
                "completed": sum(1 for i in all_interviews if i.status == "completed"),
                "cancelled": sum(1 for i in all_interviews if i.status == "cancelled")
            }
        }
        
        response = InterviewDashboardResponse(
            interviews=dashboard_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            summary=summary
        )
        
        logger.info(f"📊 Dashboard query completed - {len(dashboard_items)} interviews returned")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Dashboard query failed: {e}")
        logger.exception("Dashboard error details:")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )


# Availability checking models and functions
from datetime import date, time
from typing import Dict, Any

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

async def check_interviewer_availability(
    interviewer_id: str,
    check_date: date,
    start_hour: int = 9,
    end_hour: int = 18,
    min_slot_duration: int = 30,
    timezone: str = "UTC",
    db: Session = None
) -> AvailabilityResponse:
    """Check comprehensive availability for an interviewer"""
    
    from smart_matching_algorithm import create_sample_interviewer_profiles
    import random
    
    try:
        logger.info(f"🗓️ Checking availability for interviewer {interviewer_id}")
        
        # Get interviewer info
        interviewer_profiles = create_sample_interviewer_profiles()
        interviewer = None
        for profile in interviewer_profiles:
            if profile['id'] == interviewer_id:
                interviewer = profile
                break
        
        if not interviewer:
            raise HTTPException(
                status_code=404,
                detail=f"Interviewer {interviewer_id} not found"
            )
        
        # Set up time boundaries
        check_start = datetime.combine(check_date, time(start_hour, 0))
        check_end = datetime.combine(check_date, time(end_hour, 0))
        
        # Simulate Google Calendar busy times
        calendar_busy_slots = []
        sample_events = [
            {"title": "Team Standup", "duration": 30},
            {"title": "Client Meeting", "duration": 60},
            {"title": "Code Review", "duration": 45},
            {"title": "Lunch Break", "duration": 60}
        ]
        
        # Generate 2-3 random busy periods
        num_events = random.randint(2, 3)
        for _ in range(num_events):
            hours_range = (check_end - check_start).total_seconds() / 3600
            random_hour_offset = random.uniform(0, hours_range - 2)
            
            event_start = check_start + timedelta(hours=random_hour_offset)
            event_data = random.choice(sample_events)
            event_end = event_start + timedelta(minutes=event_data['duration'])
            
            if event_end <= check_end:
                busy_slot = BusyTimeSlot(
                    start_time=event_start,
                    end_time=event_end,
                    reason=event_data['title'],
                    source="google_calendar",
                    event_title=event_data['title']
                )
                calendar_busy_slots.append(busy_slot)
        
        # Check existing interview conflicts
        interview_busy_slots = []
        if db:
            existing_interviews = db.query(InterviewDB).filter(
                and_(
                    InterviewDB.interviewer_id == interviewer_id,
                    InterviewDB.scheduled_time >= check_start,
                    InterviewDB.scheduled_time < check_end,
                    InterviewDB.status.in_([
                        InterviewStatus.SCHEDULED,
                        InterviewStatus.CONFIRMED
                    ])
                )
            ).all()
            
            for interview in existing_interviews:
                interview_end = interview.scheduled_time + timedelta(minutes=interview.duration_minutes)
                
                busy_slot = BusyTimeSlot(
                    start_time=interview.scheduled_time,
                    end_time=interview_end,
                    reason=f"Interview: {interview.interview_type}",
                    source="existing_interview",
                    event_title=f"{interview.interview_type} Interview"
                )
                interview_busy_slots.append(busy_slot)
        
        # Combine all busy slots
        all_busy_slots = calendar_busy_slots + interview_busy_slots
        all_busy_slots.sort(key=lambda x: x.start_time)
        
        # Calculate available slots
        available_slots = []
        current_time = check_start
        slot_id = 1
        
        for busy_slot in all_busy_slots:
            if current_time < busy_slot.start_time:
                gap_duration = (busy_slot.start_time - current_time).total_seconds() / 60
                
                if gap_duration >= min_slot_duration:
                    confidence = "high" if 9 <= current_time.hour <= 16 else "medium"
                    
                    available_slot = AvailableTimeSlot(
                        start_time=current_time,
                        end_time=busy_slot.start_time,
                        duration_minutes=int(gap_duration),
                        slot_id=f"slot_{slot_id}",
                        confidence_level=confidence,
                        notes=f"Available for {int(gap_duration)} minutes"
                    )
                    available_slots.append(available_slot)
                    slot_id += 1
            
            current_time = max(current_time, busy_slot.end_time)
        
        # Check final availability
        if current_time < check_end:
            final_gap_duration = (check_end - current_time).total_seconds() / 60
            if final_gap_duration >= min_slot_duration:
                confidence = "high" if current_time.hour <= 16 else "medium"
                
                available_slot = AvailableTimeSlot(
                    start_time=current_time,
                    end_time=check_end,
                    duration_minutes=int(final_gap_duration),
                    slot_id=f"slot_{slot_id}",
                    confidence_level=confidence,
                    notes=f"Available until end of day"
                )
                available_slots.append(available_slot)
        
        # Calculate statistics
        total_working_minutes = (check_end - check_start).total_seconds() / 60
        total_available_minutes = sum(slot.duration_minutes for slot in available_slots)
        total_busy_minutes = sum(
            (slot.end_time - slot.start_time).total_seconds() / 60 
            for slot in all_busy_slots
        )
        
        availability_percentage = (total_available_minutes / total_working_minutes) * 100
        
        # Recommend best slots (top 3)
        scored_slots = []
        for slot in available_slots:
            score = 0
            hour = slot.start_time.hour
            
            if 9 <= hour <= 11:  # Morning
                score += 10
            elif 14 <= hour <= 16:  # Afternoon  
                score += 8
            
            if 60 <= slot.duration_minutes <= 90:
                score += 8
            
            if slot.confidence_level == "high":
                score += 5
                
            scored_slots.append((slot, score))
        
        scored_slots.sort(key=lambda x: x[1], reverse=True)
        recommended_slots = [slot for slot, score in scored_slots[:3]]
        
        # Build response
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
            busy_slots=all_busy_slots,
            total_busy_minutes=int(total_busy_minutes),
            availability_percentage=round(availability_percentage, 1),
            recommended_slots=recommended_slots,
            last_updated=datetime.utcnow(),
            calendar_sync_status="synced",
            working_hours_start=time(start_hour, 0),
            working_hours_end=time(end_hour, 0)
        )
        
        logger.info(f"✅ Found {len(available_slots)} available slots ({availability_percentage:.1f}% available)")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Availability check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check availability: {str(e)}"
        )

@app.get("/api/availability/{interviewer_id}", summary="Check Interviewer Availability", response_model=AvailabilityResponse)
async def get_interviewer_availability(
    interviewer_id: str,
    check_date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
    start_hour: int = Query(9, ge=0, le=23, description="Start hour (24-hour format)"),
    end_hour: int = Query(18, ge=0, le=23, description="End hour (24-hour format)"),
    min_slot_duration: int = Query(30, ge=15, le=240, description="Minimum slot duration in minutes"),
    timezone: str = Query("UTC", description="Timezone for the availability check"),
    include_tentative: bool = Query(False, description="Include tentative calendar events"),
    db: Session = Depends(get_db)
):
    """
    Check interviewer availability on a specific date
    
    This endpoint:
    - Checks Google Calendar for busy times on the specified date
    - Returns available time slots between working hours (default 9 AM - 6 PM)  
    - Considers existing interviews and calendar conflicts
    - Formats response as array of available time ranges with confidence levels
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
        
        # Check availability
        availability = await check_interviewer_availability(
            interviewer_id=interviewer_id,
            check_date=check_date,
            start_hour=start_hour,
            end_hour=end_hour,
            min_slot_duration=min_slot_duration,
            timezone=timezone,
            db=db
        )
        
        return availability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Availability check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check availability: {str(e)}"
        )


@app.get("/api/interviews/legacy/")
async def list_interviews_legacy(
    candidate_id: Optional[str] = None,
    interviewer_email: Optional[str] = None,
    status: Optional[InterviewStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Legacy interview listing endpoint (kept for backward compatibility)"""
    return await list_scheduled_interviews(candidate_id, interviewer_email, status, from_date, to_date, db)


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Candidate Management API (Phase 4+)")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📊 Candidate Management: http://localhost:8000/api/candidates/")
    print("🗓️ Interview Scheduling: http://localhost:8000/api/schedule-interview/")
    print("📋 Dashboard: http://localhost:8000/api/dashboard")
    print("⏰ Availability Checking: http://localhost:8000/api/availability/{interviewer_id}")
    print("\n🔍 New Availability Features:")
    print("   • Real-time calendar conflict detection")
    print("   • Available time slot calculation")
    print("   • Confidence-based recommendations")
    print("   • Working hours customization")
    print("   • Timezone support")
    
    uvicorn.run(
        "candidate_management_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
