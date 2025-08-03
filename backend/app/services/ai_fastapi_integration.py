"""
FastAPI AI Integration for Interview Scheduling System
Adds AI-powered candidate analysis and interviewer matching to existing API endpoints
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import os
from enum import Enum

# AI service imports
from ai_service import AIService, CandidateProfile, InterviewerProfile, InterviewType
from ai_config import AIConfig, load_ai_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class SkillRequest(BaseModel):
    name: str = Field(..., description="Skill name")
    level: str = Field(..., description="Skill level: beginner, intermediate, advanced, expert")
    years_experience: float = Field(0, description="Years of experience with this skill")
    projects_count: int = Field(0, description="Number of projects using this skill")
    certifications: List[str] = Field(default_factory=list, description="Related certifications")

class CandidateAnalysisRequest(BaseModel):
    name: str = Field(..., description="Candidate full name")
    email: str = Field(..., description="Candidate email address")
    position: str = Field(..., description="Position applied for")
    experience_years: float = Field(..., description="Total years of experience")
    skills: List[SkillRequest] = Field(..., description="List of candidate skills")
    education: str = Field("", description="Educational background")
    previous_companies: List[str] = Field(default_factory=list, description="Previous employers")
    github_url: str = Field("", description="GitHub profile URL")
    linkedin_url: str = Field("", description="LinkedIn profile URL")
    portfolio_url: str = Field("", description="Portfolio website URL")
    cover_letter: str = Field("", description="Cover letter text")
    resume_text: str = Field("", description="Resume content text")
    preferred_salary: float = Field(0.0, description="Preferred salary")
    availability: str = Field("", description="Availability information")

class InterviewerMatchRequest(BaseModel):
    candidate: CandidateAnalysisRequest = Field(..., description="Candidate profile")
    interview_type: str = Field("technical", description="Type of interview")
    max_matches: int = Field(5, description="Maximum number of interviewer matches to return")

class CandidateAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether analysis was successful")
    candidate_name: str = Field(..., description="Candidate name")
    position: str = Field(..., description="Position applied for")
    overall_score: float = Field(..., description="Overall candidate score (0-100)")
    technical_score: float = Field(..., description="Technical skills score (0-100)")
    experience_score: float = Field(..., description="Experience level score (0-100)")
    skill_match_score: float = Field(..., description="Skill-position match score (0-100)")
    cultural_fit_score: float = Field(..., description="Cultural fit score (0-100)")
    strengths: List[str] = Field(..., description="Candidate strengths")
    weaknesses: List[str] = Field(..., description="Areas for improvement")
    skill_gaps: List[str] = Field(..., description="Skills missing for the position")
    recommended_interview_types: List[str] = Field(..., description="Recommended interview types")
    estimated_level: str = Field(..., description="Estimated experience level")
    summary: str = Field(..., description="AI-generated summary")
    recommendations: List[str] = Field(..., description="Hiring recommendations")
    red_flags: List[str] = Field(..., description="Potential concerns")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    confidence_score: float = Field(..., description="AI confidence in analysis (0-1)")
    analysis_timestamp: str = Field(..., description="When analysis was performed")
    ai_model_used: str = Field(..., description="AI model used for analysis")
    cost_estimate: Dict = Field(..., description="Estimated API cost for analysis")

class InterviewerMatchResponse(BaseModel):
    interviewer_name: str = Field(..., description="Interviewer name")
    interviewer_email: str = Field(..., description="Interviewer email")
    match_score: float = Field(..., description="Overall match score (0-100)")
    expertise_match: float = Field(..., description="Technical expertise match (0-100)")
    availability_match: float = Field(..., description="Availability match (0-100)")
    experience_match: float = Field(..., description="Experience level match (0-100)")
    matching_skills: List[str] = Field(..., description="Skills that match between candidate and interviewer")
    interview_type: str = Field(..., description="Interview type")
    estimated_duration: int = Field(..., description="Estimated interview duration in minutes")
    priority_level: str = Field(..., description="Priority level: high, medium, low")
    why_matched: str = Field(..., description="AI explanation for why this interviewer was matched")
    potential_concerns: List[str] = Field(..., description="Potential concerns about this match")
    interview_focus_areas: List[str] = Field(..., description="Areas to focus on during interview")
    suggested_questions: List[str] = Field(..., description="AI-suggested interview questions")

class InterviewerMatchingResponse(BaseModel):
    success: bool = Field(..., description="Whether matching was successful")
    candidate_name: str = Field(..., description="Candidate name")
    interview_type: str = Field(..., description="Interview type")
    matches: List[InterviewerMatchResponse] = Field(..., description="List of interviewer matches")
    ai_model_used: str = Field(..., description="AI model used for matching")
    cost_estimate: Dict = Field(..., description="Estimated API cost for matching")

class BatchAnalysisRequest(BaseModel):
    candidates: List[CandidateAnalysisRequest] = Field(..., description="List of candidates to analyze")
    interview_type: str = Field("technical", description="Default interview type")

class BatchAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether batch analysis was successful")
    total_candidates: int = Field(..., description="Total number of candidates processed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    results: List[Dict] = Field(..., description="Individual analysis results")
    total_cost_estimate: Dict = Field(..., description="Total estimated cost")
    processing_time_seconds: float = Field(..., description="Total processing time")

class AIStatusResponse(BaseModel):
    ai_service_available: bool = Field(..., description="Whether AI service is available")
    model: str = Field(..., description="Current AI model")
    model_info: Dict = Field(..., description="Model configuration and capabilities")
    api_key_configured: bool = Field(..., description="Whether API key is configured")
    cost_per_1k_tokens: float = Field(..., description="Cost per 1000 tokens")

# AI Service dependency
def get_ai_service() -> AIService:
    """Dependency to get AI service instance"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="AI service not configured. Please set OPENROUTER_API_KEY environment variable."
        )
    
    config = load_ai_config()
    return AIService(api_key=api_key, model=config["model"])

# Sample interviewers for demo (in production, load from database)
SAMPLE_INTERVIEWERS = [
    {
        "name": "Alice Johnson",
        "email": "alice.johnson@company.com",
        "department": "Engineering",
        "expertise_areas": ["Python", "Django", "System Design", "Microservices"],
        "interview_types": ["technical", "system_design"],
        "seniority_level": "senior",
        "experience_years": 8.0,
        "max_interviews_per_week": 5,
        "preferred_technologies": ["Python", "Django", "PostgreSQL", "AWS"],
        "rating": 4.8,
        "total_interviews": 150,
        "successful_hires": 45
    },
    {
        "name": "Bob Chen",
        "email": "bob.chen@company.com",
        "department": "Engineering", 
        "expertise_areas": ["Frontend", "React", "JavaScript", "UI/UX"],
        "interview_types": ["technical", "coding"],
        "seniority_level": "mid",
        "experience_years": 5.0,
        "max_interviews_per_week": 6,
        "preferred_technologies": ["React", "JavaScript", "TypeScript", "CSS"],
        "rating": 4.6,
        "total_interviews": 85,
        "successful_hires": 28
    },
    {
        "name": "Carol Martinez",
        "email": "carol.martinez@company.com",
        "department": "HR",
        "expertise_areas": ["Cultural Fit", "Communication", "Leadership", "Team Dynamics"],
        "interview_types": ["behavioral", "cultural_fit"],
        "seniority_level": "senior",
        "experience_years": 10.0,
        "max_interviews_per_week": 8,
        "preferred_technologies": [],
        "rating": 4.9,
        "total_interviews": 200,
        "successful_hires": 75
    }
]

def add_ai_routes(app: FastAPI):
    """
    Add AI-powered routes to existing FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    
    @app.get("/api/ai/status", response_model=AIStatusResponse, tags=["AI"])
    async def get_ai_status():
        """
        Get AI service status and configuration
        """
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
            api_key_configured = bool(api_key and len(api_key) > 10)
            
            if api_key_configured:
                ai_service = get_ai_service()
                model_info = ai_service.get_model_info()
                
                return AIStatusResponse(
                    ai_service_available=True,
                    model=ai_service.model,
                    model_info=model_info,
                    api_key_configured=True,
                    cost_per_1k_tokens=model_info.get("cost_per_1k_tokens", 0)
                )
            else:
                return AIStatusResponse(
                    ai_service_available=False,
                    model="none",
                    model_info={},
                    api_key_configured=False,
                    cost_per_1k_tokens=0
                )
                
        except Exception as e:
            logger.error(f"Error getting AI status: {e}")
            raise HTTPException(status_code=500, detail=f"Error checking AI status: {str(e)}")
    
    @app.post("/api/ai/analyze-candidate", response_model=CandidateAnalysisResponse, tags=["AI"])
    async def analyze_candidate(
        request: CandidateAnalysisRequest,
        ai_service: AIService = Depends(get_ai_service)
    ):
        """
        Analyze candidate profile using AI to assess technical fit and interview readiness
        """
        try:
            logger.info(f"🤖 Analyzing candidate: {request.name} for {request.position}")
            
            # Convert request to CandidateProfile
            from ai_service import CandidateSkill, SkillLevel
            
            skills = []
            for skill_req in request.skills:
                skills.append(CandidateSkill(
                    name=skill_req.name,
                    level=SkillLevel(skill_req.level),
                    years_experience=skill_req.years_experience,
                    projects_count=skill_req.projects_count,
                    certifications=skill_req.certifications
                ))
            
            candidate = CandidateProfile(
                name=request.name,
                email=request.email,
                position=request.position,
                experience_years=request.experience_years,
                skills=skills,
                education=request.education,
                previous_companies=request.previous_companies,
                github_url=request.github_url,
                linkedin_url=request.linkedin_url,
                portfolio_url=request.portfolio_url,
                cover_letter=request.cover_letter,
                resume_text=request.resume_text,
                preferred_salary=request.preferred_salary,
                availability=request.availability
            )
            
            # Perform AI analysis
            analysis = ai_service.analyze_candidate(candidate)
            
            if not analysis:
                raise HTTPException(status_code=500, detail="AI analysis failed")
            
            # Estimate cost
            candidate_text_length = len(str(request.dict()))
            estimated_tokens = candidate_text_length * 0.75 + 1000  # Rough estimation
            cost_estimate = {
                "estimated_tokens": int(estimated_tokens),
                "estimated_cost_usd": AIConfig.get_cost_estimate(ai_service.model, estimated_tokens),
                "model": ai_service.model
            }
            
            return CandidateAnalysisResponse(
                success=True,
                candidate_name=analysis.candidate_name,
                position=analysis.position,
                overall_score=analysis.overall_score,
                technical_score=analysis.technical_score,
                experience_score=analysis.experience_score,
                skill_match_score=analysis.skill_match_score,
                cultural_fit_score=analysis.cultural_fit_score,
                strengths=analysis.strengths,
                weaknesses=analysis.weaknesses,
                skill_gaps=analysis.skill_gaps,
                recommended_interview_types=[t.value for t in analysis.recommended_interview_types],
                estimated_level=analysis.estimated_level,
                summary=analysis.summary,
                recommendations=analysis.recommendations,
                red_flags=analysis.red_flags,
                next_steps=analysis.next_steps,
                confidence_score=analysis.confidence_score,
                analysis_timestamp=analysis.analysis_timestamp,
                ai_model_used=ai_service.model,
                cost_estimate=cost_estimate
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in candidate analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    @app.post("/api/ai/match-interviewer", response_model=InterviewerMatchingResponse, tags=["AI"])
    async def match_interviewer(
        request: InterviewerMatchRequest,
        ai_service: AIService = Depends(get_ai_service)
    ):
        """
        Find best interviewer matches for a candidate using AI analysis
        """
        try:
            logger.info(f"🎯 Finding interviewer matches for {request.candidate.name}")
            
            # First analyze the candidate
            candidate_analysis_req = CandidateAnalysisRequest(**request.candidate.dict())
            analysis_response = await analyze_candidate(candidate_analysis_req, ai_service)
            
            if not analysis_response.success:
                raise HTTPException(status_code=500, detail="Candidate analysis failed")
            
            # Convert to objects for AI service
            from ai_service import CandidateSkill, SkillLevel, CandidateAnalysis
            
            skills = []
            for skill_req in request.candidate.skills:
                skills.append(CandidateSkill(
                    name=skill_req.name,
                    level=SkillLevel(skill_req.level),
                    years_experience=skill_req.years_experience,
                    projects_count=skill_req.projects_count,
                    certifications=skill_req.certifications
                ))
            
            candidate = CandidateProfile(
                name=request.candidate.name,
                email=request.candidate.email,
                position=request.candidate.position,
                experience_years=request.candidate.experience_years,
                skills=skills,
                education=request.candidate.education,
                previous_companies=request.candidate.previous_companies,
                github_url=request.candidate.github_url,
                linkedin_url=request.candidate.linkedin_url,
                portfolio_url=request.candidate.portfolio_url,
                cover_letter=request.candidate.cover_letter,
                resume_text=request.candidate.resume_text,
                preferred_salary=request.candidate.preferred_salary,
                availability=request.candidate.availability
            )
            
            # Create analysis object
            analysis = CandidateAnalysis(
                candidate_name=analysis_response.candidate_name,
                position=analysis_response.position,
                overall_score=analysis_response.overall_score,
                technical_score=analysis_response.technical_score,
                experience_score=analysis_response.experience_score,
                skill_match_score=analysis_response.skill_match_score,
                cultural_fit_score=analysis_response.cultural_fit_score,
                strengths=analysis_response.strengths,
                weaknesses=analysis_response.weaknesses,
                skill_gaps=analysis_response.skill_gaps,
                recommended_interview_types=[InterviewType(t) for t in analysis_response.recommended_interview_types],
                estimated_level=analysis_response.estimated_level,
                summary=analysis_response.summary,
                recommendations=analysis_response.recommendations,
                red_flags=analysis_response.red_flags,
                next_steps=analysis_response.next_steps,
                analysis_timestamp=analysis_response.analysis_timestamp,
                confidence_score=analysis_response.confidence_score
            )
            
            # Convert sample interviewers to InterviewerProfile objects
            available_interviewers = []
            for interviewer_data in SAMPLE_INTERVIEWERS:
                available_interviewers.append(InterviewerProfile(**interviewer_data))
            
            # Find matches
            matches = ai_service.match_interviewer(
                candidate, analysis, available_interviewers, InterviewType(request.interview_type)
            )
            
            if not matches:
                raise HTTPException(status_code=404, detail="No suitable interviewers found")
            
            # Limit results
            matches = matches[:request.max_matches]
            
            # Convert to response format
            match_responses = []
            for match in matches:
                match_responses.append(InterviewerMatchResponse(
                    interviewer_name=match.interviewer_name,
                    interviewer_email=match.interviewer_email,
                    match_score=match.match_score,
                    expertise_match=match.expertise_match,
                    availability_match=match.availability_match,
                    experience_match=match.experience_match,
                    matching_skills=match.matching_skills,
                    interview_type=match.interview_type.value,
                    estimated_duration=match.estimated_duration,
                    priority_level=match.priority_level,
                    why_matched=match.why_matched,
                    potential_concerns=match.potential_concerns,
                    interview_focus_areas=match.interview_focus_areas,
                    suggested_questions=match.suggested_questions
                ))
            
            # Estimate cost
            estimated_tokens = len(str(request.dict())) + len(matches) * 200
            cost_estimate = {
                "estimated_tokens": int(estimated_tokens),
                "estimated_cost_usd": AIConfig.get_cost_estimate(ai_service.model, estimated_tokens),
                "model": ai_service.model
            }
            
            return InterviewerMatchingResponse(
                success=True,
                candidate_name=request.candidate.name,
                interview_type=request.interview_type,
                matches=match_responses,
                ai_model_used=ai_service.model,
                cost_estimate=cost_estimate
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in interviewer matching: {e}")
            raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")
    
    @app.post("/api/ai/batch-analyze", response_model=BatchAnalysisResponse, tags=["AI"])
    async def batch_analyze_candidates(
        request: BatchAnalysisRequest,
        background_tasks: BackgroundTasks,
        ai_service: AIService = Depends(get_ai_service)
    ):
        """
        Analyze multiple candidates in batch for efficient processing
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"🔄 Starting batch analysis of {len(request.candidates)} candidates")
            
            results = []
            total_cost = 0.0
            successful_count = 0
            
            for i, candidate_req in enumerate(request.candidates):
                try:
                    logger.info(f"   Processing candidate {i+1}/{len(request.candidates)}: {candidate_req.name}")
                    
                    # Analyze individual candidate
                    analysis_response = await analyze_candidate(candidate_req, ai_service)
                    
                    if analysis_response.success:
                        successful_count += 1
                        total_cost += analysis_response.cost_estimate.get("estimated_cost_usd", 0)
                        
                        results.append({
                            "success": True,
                            "candidate_name": candidate_req.name,
                            "analysis": analysis_response.dict()
                        })
                    else:
                        results.append({
                            "success": False,
                            "candidate_name": candidate_req.name,
                            "error": "Analysis failed"
                        })
                
                except Exception as e:
                    logger.error(f"Error analyzing candidate {candidate_req.name}: {e}")
                    results.append({
                        "success": False,
                        "candidate_name": candidate_req.name,
                        "error": str(e)
                    })
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            total_cost_estimate = {
                "estimated_cost_usd": total_cost,
                "model": ai_service.model,
                "candidates_processed": len(request.candidates),
                "successful_analyses": successful_count
            }
            
            logger.info(f"✅ Batch analysis completed in {processing_time:.2f} seconds")
            logger.info(f"   Successful: {successful_count}/{len(request.candidates)}")
            logger.info(f"   Total cost: ${total_cost:.6f}")
            
            return BatchAnalysisResponse(
                success=True,
                total_candidates=len(request.candidates),
                successful_analyses=successful_count,
                results=results,
                total_cost_estimate=total_cost_estimate,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
    
    @app.get("/api/ai/models", tags=["AI"])
    async def get_available_models():
        """
        Get information about available AI models and their characteristics
        """
        try:
            models_info = AIConfig.get_all_models_info()
            
            return {
                "available_models": models_info,
                "current_model": load_ai_config()["model"],
                "recommended_models": {
                    "cost_effective": AIConfig.get_recommended_model("cost_effective"),
                    "high_quality": AIConfig.get_recommended_model("high_quality"),
                    "balanced": AIConfig.get_recommended_model("balanced")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting model information: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")
    
    @app.get("/api/ai/interviewers", tags=["AI"])
    async def get_available_interviewers():
        """
        Get list of available interviewers for matching
        """
        try:
            return {
                "interviewers": SAMPLE_INTERVIEWERS,
                "total_count": len(SAMPLE_INTERVIEWERS)
            }
        except Exception as e:
            logger.error(f"Error getting interviewers: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get interviewers: {str(e)}")

# Usage example for integrating with existing FastAPI app
def create_ai_enhanced_app() -> FastAPI:
    """
    Create a new FastAPI app with AI routes for demonstration
    """
    app = FastAPI(
        title="AI-Enhanced Interview Scheduling API",
        description="Interview scheduling system with AI-powered candidate analysis and interviewer matching",
        version="1.0.0"
    )
    
    # Add AI routes
    add_ai_routes(app)
    
    # Add a simple health check
    @app.get("/", tags=["Health"])
    async def root():
        return {
            "message": "AI-Enhanced Interview Scheduling System",
            "version": "1.0.0",
            "ai_features": [
                "candidate_analysis",
                "interviewer_matching", 
                "batch_processing",
                "cost_optimization"
            ],
            "docs_url": "/docs"
        }
    
    return app

if __name__ == "__main__":
    """
    Run the AI-enhanced FastAPI application
    """
    import uvicorn
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ Warning: OPENROUTER_API_KEY not set. AI features will not work.")
        print("   Get your key from: https://openrouter.ai/keys")
    
    app = create_ai_enhanced_app()
    
    print("🚀 Starting AI-Enhanced Interview Scheduling API")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   AI Status: http://localhost:8000/api/ai/status")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
