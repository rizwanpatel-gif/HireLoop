"""
FastAPI Integration for Smart Matching Algorithm
==============================================

REST API endpoints for the intelligent interviewer matching system.
Provides comprehensive matching with AI analysis and calendar integration.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

from app.services.smart_matching import (
    SmartMatchingAlgorithm, 
    InterviewerProfile, 
    MatchResult,
    MatchConfidence,
    create_sample_interviewer_profiles
)
from app.services.ai_service import AIService, Candidate, Skill, InterviewType
from app.services.calendar_service import GoogleCalendarService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class SkillRequest(BaseModel):
    name: str = Field(..., description="Skill name (e.g., 'Python', 'React')")
    level: str = Field(..., description="Skill level: beginner, intermediate, advanced, expert")
    years_experience: int = Field(..., ge=0, le=50, description="Years of experience with this skill")
    projects_count: int = Field(0, ge=0, description="Number of projects using this skill")


class CandidateRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Candidate full name")
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$', description="Valid email address")
    position: str = Field(..., description="Position applying for")
    experience_years: int = Field(..., ge=0, le=50, description="Total years of professional experience")
    skills: List[SkillRequest] = Field(..., min_items=1, description="List of candidate skills")
    resume_text: Optional[str] = Field(None, description="Full resume text for AI analysis")


class InterviewTypeEnum(str, Enum):
    technical = "technical"
    system_design = "system_design" 
    behavioral = "behavioral"
    cultural = "cultural"


class MatchingRequest(BaseModel):
    candidate: CandidateRequest
    interview_type: InterviewTypeEnum = Field(..., description="Type of interview required")
    interview_start_date: datetime = Field(..., description="Earliest interview date (ISO format)")
    interview_end_date: datetime = Field(..., description="Latest interview date (ISO format)")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of matches to return")
    
    @validator('interview_end_date')
    def end_date_after_start_date(cls, v, values):
        if 'interview_start_date' in values and v <= values['interview_start_date']:
            raise ValueError('interview_end_date must be after interview_start_date')
        return v
    
    @validator('interview_start_date')
    def start_date_not_in_past(cls, v):
        if v < datetime.now():
            raise ValueError('interview_start_date cannot be in the past')
        return v


class MatchScoreResponse(BaseModel):
    overall_match: float = Field(..., description="Overall match score (0-100)")
    technical_match: float = Field(..., description="Technical skills match score")
    seniority_match: float = Field(..., description="Seniority level match score")
    availability: float = Field(..., description="Calendar availability score")
    interview_type: float = Field(..., description="Interview type preference match")
    experience_match: float = Field(..., description="Experience domain match score")


class InterviewerResponse(BaseModel):
    name: str
    email: str
    seniority: str
    success_rate: float = Field(..., description="Historical interview success rate")


class MatchResponse(BaseModel):
    interviewer: InterviewerResponse
    scores: MatchScoreResponse
    confidence: str = Field(..., description="Match confidence level")
    available_slots: int = Field(..., description="Number of available time slots")
    recommended_time: Optional[str] = Field(None, description="Recommended interview time (ISO format)")
    match_reasons: List[str] = Field(..., description="Reasons why this is a good match")
    concerns: List[str] = Field(..., description="Potential concerns or considerations")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class MatchingResponse(BaseModel):
    success: bool
    message: str
    candidate_name: str
    interview_type: str
    matches: List[MatchResponse]
    total_matches_found: int
    analysis_metadata: Dict[str, Any]


class QuickMatchRequest(BaseModel):
    candidate_name: str = Field(..., description="Candidate name")
    position: str = Field(..., description="Position title")
    experience_years: int = Field(..., ge=0, le=50)
    primary_skills: List[str] = Field(..., min_items=1, description="Primary technical skills")
    interview_type: InterviewTypeEnum = InterviewTypeEnum.technical


class BatchMatchingRequest(BaseModel):
    candidates: List[CandidateRequest] = Field(..., min_items=1, max_items=10)
    interview_type: InterviewTypeEnum = InterviewTypeEnum.technical
    interview_start_date: datetime
    interview_end_date: datetime


class HealthResponse(BaseModel):
    status: str
    ai_service_available: bool
    calendar_service_available: bool
    total_interviewers: int
    last_updated: str


# Dependency injection
async def get_smart_matcher() -> SmartMatchingAlgorithm:
    """Dependency to get smart matching algorithm instance"""
    try:
        ai_service = AIService()
        calendar_service = GoogleCalendarService()
        return SmartMatchingAlgorithm(ai_service, calendar_service)
    except Exception as e:
        logger.error(f"Failed to initialize smart matcher: {e}")
        raise HTTPException(status_code=503, detail="Smart matching service unavailable")


async def get_interviewer_profiles() -> List[InterviewerProfile]:
    """Dependency to get available interviewer profiles"""
    # In production, this would load from a database
    return create_sample_interviewer_profiles()


# Create FastAPI app
app = FastAPI(
    title="Smart Interviewer Matching API",
    description="Intelligent interviewer matching system with AI analysis and calendar integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test AI service
        ai_available = True
        try:
            ai_service = AIService()
        except:
            ai_available = False
        
        # Test calendar service  
        calendar_available = True
        try:
            calendar_service = GoogleCalendarService()
        except:
            calendar_available = False
        
        # Get interviewer count
        interviewers = await get_interviewer_profiles()
        
        return HealthResponse(
            status="healthy" if ai_available and calendar_available else "degraded",
            ai_service_available=ai_available,
            calendar_service_available=calendar_available,
            total_interviewers=len(interviewers),
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.post("/api/smart-match", response_model=MatchingResponse)
async def find_smart_matches(
    request: MatchingRequest,
    matcher: SmartMatchingAlgorithm = Depends(get_smart_matcher),
    interviewer_profiles: List[InterviewerProfile] = Depends(get_interviewer_profiles)
):
    """
    Find the best interviewer matches for a candidate using intelligent matching
    
    This endpoint combines:
    - AI-powered candidate analysis
    - Technical expertise matching
    - Calendar availability checking
    - Multi-dimensional scoring
    - Confidence assessment with fallback logic
    """
    try:
        logger.info(f"Processing smart match request for {request.candidate.name}")
        
        # Convert request to internal models
        candidate_skills = [
            Skill(
                name=skill.name,
                level=skill.level,
                years_experience=skill.years_experience,
                projects_count=skill.projects_count
            )
            for skill in request.candidate.skills
        ]
        
        candidate = Candidate(
            name=request.candidate.name,
            email=request.candidate.email,
            position=request.candidate.position,
            experience_years=request.candidate.experience_years,
            skills=candidate_skills,
            resume_text=request.candidate.resume_text or ""
        )
        
        # Convert interview type
        interview_type_map = {
            InterviewTypeEnum.technical: InterviewType.TECHNICAL,
            InterviewTypeEnum.system_design: InterviewType.SYSTEM_DESIGN,
            InterviewTypeEnum.behavioral: InterviewType.BEHAVIORAL,
            InterviewTypeEnum.cultural: InterviewType.CULTURAL
        }
        interview_type = interview_type_map[request.interview_type]
        
        # Find matches
        matches = await matcher.find_best_matches(
            candidate=candidate,
            interviewer_profiles=interviewer_profiles,
            interview_date_range=(request.interview_start_date, request.interview_end_date),
            required_interview_type=interview_type,
            max_results=request.max_results
        )
        
        # Convert matches to response format
        match_responses = [
            MatchResponse(
                interviewer=InterviewerResponse(
                    name=match.interviewer_profile.interviewer.name,
                    email=match.interviewer_profile.interviewer.email,
                    seniority=match.interviewer_profile.seniority_level,
                    success_rate=match.interviewer_profile.success_rate
                ),
                scores=MatchScoreResponse(
                    overall_match=round(match.overall_match_score, 1),
                    technical_match=round(match.technical_match_score, 1),
                    seniority_match=round(match.seniority_match_score, 1),
                    availability=round(match.availability_score, 1),
                    interview_type=round(match.interview_type_score, 1),
                    experience_match=round(match.experience_match_score, 1)
                ),
                confidence=match.confidence_level.value,
                available_slots=len(match.available_slots),
                recommended_time=(
                    match.recommended_slot.start_time.isoformat() 
                    if match.recommended_slot else None
                ),
                match_reasons=match.match_reasons,
                concerns=match.potential_concerns,
                metadata={
                    "calculated_at": match.calculated_at.isoformat(),
                    "ai_model": match.ai_model_used,
                    "interviewer_specializations": match.interviewer_profile.specialization_areas
                }
            )
            for match in matches
        ]
        
        return MatchingResponse(
            success=True,
            message=f"Found {len(matches)} suitable matches",
            candidate_name=request.candidate.name,
            interview_type=request.interview_type.value,
            matches=match_responses,
            total_matches_found=len(matches),
            analysis_metadata={
                "processing_time_ms": 0,  # Could add timing
                "ai_confidence": matches[0].candidate_analysis.confidence_score if matches else 0,
                "fallback_used": any(m.confidence_level == MatchConfidence.INSUFFICIENT for m in matches)
            }
        )
        
    except Exception as e:
        logger.error(f"Smart matching failed: {e}")
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


@app.post("/api/quick-match")
async def quick_match(
    request: QuickMatchRequest,
    matcher: SmartMatchingAlgorithm = Depends(get_smart_matcher),
    interviewer_profiles: List[InterviewerProfile] = Depends(get_interviewer_profiles)
):
    """
    Quick matching for simple candidate profiles
    
    Simplified endpoint for basic matching without detailed candidate information.
    """
    try:
        # Create basic candidate from quick request
        candidate_skills = [
            Skill(name=skill, level="intermediate", years_experience=2, projects_count=3)
            for skill in request.primary_skills
        ]
        
        candidate = Candidate(
            name=request.candidate_name,
            email=f"{request.candidate_name.lower().replace(' ', '.')}@example.com",
            position=request.position,
            experience_years=request.experience_years,
            skills=candidate_skills,
            resume_text=f"Experienced {request.position} with {request.experience_years} years of experience in {', '.join(request.primary_skills)}"
        )
        
        # Use next week for interview window
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=7)
        
        interview_type_map = {
            InterviewTypeEnum.technical: InterviewType.TECHNICAL,
            InterviewTypeEnum.system_design: InterviewType.SYSTEM_DESIGN,
            InterviewTypeEnum.behavioral: InterviewType.BEHAVIORAL,
            InterviewTypeEnum.cultural: InterviewType.CULTURAL
        }
        
        matches = await matcher.find_best_matches(
            candidate=candidate,
            interviewer_profiles=interviewer_profiles,
            interview_date_range=(start_date, end_date),
            required_interview_type=interview_type_map[request.interview_type],
            max_results=3
        )
        
        if not matches:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "No suitable matches found",
                    "suggestions": ["Try different interview type", "Expand date range", "Add more interviewers"]
                }
            )
        
        best_match = matches[0]
        return {
            "success": True,
            "message": "Quick match found",
            "best_match": {
                "interviewer_name": best_match.interviewer_profile.interviewer.name,
                "match_score": round(best_match.overall_match_score, 1),
                "confidence": best_match.confidence_level.value,
                "recommended_time": (
                    best_match.recommended_slot.start_time.isoformat()
                    if best_match.recommended_slot else None
                ),
                "why_matched": best_match.match_reasons[:2]
            },
            "all_matches": len(matches)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick matching failed: {str(e)}")


@app.post("/api/batch-match")
async def batch_match(
    request: BatchMatchingRequest,
    background_tasks: BackgroundTasks,
    matcher: SmartMatchingAlgorithm = Depends(get_smart_matcher),
    interviewer_profiles: List[InterviewerProfile] = Depends(get_interviewer_profiles)
):
    """
    Batch matching for multiple candidates
    
    Process multiple candidates and return optimal interviewer assignments.
    """
    try:
        if len(request.candidates) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 candidates per batch")
        
        # Process each candidate
        batch_results = []
        
        for candidate_req in request.candidates:
            candidate_skills = [
                Skill(
                    name=skill.name,
                    level=skill.level, 
                    years_experience=skill.years_experience,
                    projects_count=skill.projects_count
                )
                for skill in candidate_req.skills
            ]
            
            candidate = Candidate(
                name=candidate_req.name,
                email=candidate_req.email,
                position=candidate_req.position,
                experience_years=candidate_req.experience_years,
                skills=candidate_skills,
                resume_text=candidate_req.resume_text or ""
            )
            
            interview_type_map = {
                InterviewTypeEnum.technical: InterviewType.TECHNICAL,
                InterviewTypeEnum.system_design: InterviewType.SYSTEM_DESIGN,
                InterviewTypeEnum.behavioral: InterviewType.BEHAVIORAL,
                InterviewTypeEnum.cultural: InterviewType.CULTURAL
            }
            
            matches = await matcher.find_best_matches(
                candidate=candidate,
                interviewer_profiles=interviewer_profiles,
                interview_date_range=(request.interview_start_date, request.interview_end_date),
                required_interview_type=interview_type_map[request.interview_type],
                max_results=1  # Only best match for batch processing
            )
            
            batch_results.append({
                "candidate_name": candidate.name,
                "best_match": matches[0].to_dict() if matches else None,
                "match_found": len(matches) > 0
            })
        
        return {
            "success": True,
            "message": f"Batch processing complete for {len(request.candidates)} candidates",
            "results": batch_results,
            "summary": {
                "total_candidates": len(request.candidates),
                "matches_found": sum(1 for r in batch_results if r["match_found"]),
                "unmatched": sum(1 for r in batch_results if not r["match_found"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch matching failed: {str(e)}")


@app.get("/api/interviewers")
async def list_interviewers(
    interviewer_profiles: List[InterviewerProfile] = Depends(get_interviewer_profiles)
):
    """List all available interviewers with their expertise"""
    
    interviewers = []
    for profile in interviewer_profiles:
        top_skills = sorted(profile.technical_expertise.items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        
        interviewers.append({
            "name": profile.interviewer.name,
            "email": profile.interviewer.email,
            "seniority": profile.seniority_level,
            "specializations": profile.specialization_areas,
            "top_skills": [{"skill": skill, "score": score} for skill, score in top_skills],
            "interview_types": [t.value for t in profile.interview_types_preferred],
            "success_rate": profile.success_rate,
            "feedback_score": profile.candidate_feedback_score,
            "years_interviewing": profile.years_interviewing
        })
    
    return {
        "success": True,
        "total_interviewers": len(interviewers),
        "interviewers": interviewers
    }


@app.get("/api/matching-stats")
async def matching_statistics():
    """Get matching algorithm statistics and configuration"""
    
    matcher = SmartMatchingAlgorithm(None, None)  # Just for weights
    
    return {
        "algorithm_version": "1.0.0",
        "scoring_weights": matcher.weights,
        "confidence_thresholds": {
            "excellent": matcher.excellent_score,
            "preferred": matcher.preferred_score,
            "minimum_acceptable": matcher.min_acceptable_score
        },
        "features": [
            "AI-powered candidate analysis",
            "Technical expertise matching", 
            "Calendar availability integration",
            "Multi-dimensional scoring",
            "Confidence assessment",
            "Fallback logic",
            "Batch processing"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Smart Matching API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 Alternative docs: http://localhost:8000/redoc")
    
    uvicorn.run(
        "smart_matching_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
