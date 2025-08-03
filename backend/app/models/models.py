from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import enum
import os

Base = declarative_base()

# Create engine for database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
engine = create_engine(DATABASE_URL, echo=False)

class UserRole(enum.Enum):
    ADMIN = "admin"
    INTERVIEWER = "interviewer"
    HR = "hr"
    CANDIDATE = "candidate"

class InterviewType(enum.Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURAL_FIT = "cultural_fit"
    FINAL = "final"
    PHONE_SCREENING = "phone_screening"

class InterviewStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

class User(Base):
    """
    User model for system users (interviewers, HR, admins)
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.INTERVIEWER)
    google_calendar_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    conducted_interviews = relationship("Interview", back_populates="interviewer", foreign_keys="Interview.interviewer_id")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}', role='{self.role.value}')>"

class Candidate(Base):
    """
    Candidate model for job applicants
    """
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    position = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    experience_years = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    resume_file_path = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    education = Column(Text, nullable=True)
    previous_companies = Column(Text, nullable=True)  # JSON string of previous companies
    cover_letter = Column(Text, nullable=True)
    
    # Missing fields for candidate creation
    skills = Column(Text, nullable=True)  # Skills as comma-separated string
    resume_text = Column(Text, nullable=True)  # Resume summary/content
    
    preferred_salary = Column(Float, nullable=True)
    availability = Column(String(255), nullable=True)
    remote_preference = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    ai_analysis_status = Column(String(50), nullable=True)
    ai_overall_score = Column(Float, nullable=True)
    ai_technical_score = Column(Float, nullable=True)
    ai_experience_score = Column(Float, nullable=True)
    ai_cultural_fit_score = Column(Float, nullable=True)
    ai_analysis_results = Column(Text, nullable=True)  # JSON string
    ai_model_used = Column(String(100), nullable=True)
    ai_confidence_score = Column(Float, nullable=True)
    matched_interviewers = Column(Text, nullable=True)  # JSON string
    interview_scheduled = Column(Integer, nullable=True, default=0)
    interview_datetime = Column(DateTime(timezone=True), nullable=True)
    interview_type = Column(String(50), nullable=True)
    recruiter_notes = Column(Text, nullable=True)
    red_flags = Column(Text, nullable=True)  # JSON string
    tags = Column(Text, nullable=True)  # JSON string
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', email='{self.email}', position='{self.position}')>"

class Interview(Base):
    """
    Interview model for scheduled interviews
    """
    __tablename__ = 'interviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False)
    interviewer_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, nullable=False, default=60)  # Duration in minutes
    type = Column(Enum(InterviewType), nullable=False, default=InterviewType.TECHNICAL)
    status = Column(Enum(InterviewStatus), nullable=False, default=InterviewStatus.SCHEDULED)
    google_event_id = Column(String(255), nullable=True)  # Google Calendar event ID
    notes = Column(Text, nullable=True)  # Interview notes
    feedback = Column(Text, nullable=True)  # Interview feedback
    score = Column(Float, nullable=True)  # Interview score (1-10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User", back_populates="conducted_interviews", foreign_keys=[interviewer_id])
    
    def __repr__(self):
        return f"<Interview(id={self.id}, candidate_id={self.candidate_id}, interviewer_id={self.interviewer_id}, scheduled_time='{self.scheduled_time}', status='{self.status.value}')>"

# Database configuration
class DatabaseConfig:
    """Database configuration and session management"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            # Default to SQLite for development
            database_url = "sqlite:///interview_system.db"
        
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

# Utility functions for common operations
def create_user(session, email: str, name: str, role: UserRole, google_calendar_id: str = None):
    """Create a new user"""
    user = User(
        email=email,
        name=name,
        role=role,
        google_calendar_id=google_calendar_id
    )
    session.add(user)
    session.commit()
    return user

def create_candidate(session, name: str, email: str, position: str, phone: str = None, 
                    resume_text: str = None, skills: str = None, ai_score: float = None):
    """Create a new candidate"""
    candidate = Candidate(
        name=name,
        email=email,
        phone=phone,
        position=position,
        resume_text=resume_text,
        skills=skills,
        ai_score=ai_score
    )
    session.add(candidate)
    session.commit()
    return candidate

def schedule_interview(session, candidate_id: int, interviewer_id: int, 
                      scheduled_time: datetime, duration: int = 60,
                      interview_type: InterviewType = InterviewType.TECHNICAL,
                      google_event_id: str = None):
    """Schedule a new interview"""
    interview = Interview(
        candidate_id=candidate_id,
        interviewer_id=interviewer_id,
        scheduled_time=scheduled_time,
        duration=duration,
        type=interview_type,
        google_event_id=google_event_id
    )
    session.add(interview)
    session.commit()
    return interview
