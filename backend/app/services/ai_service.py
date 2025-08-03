"""
AI Service for Interview Scheduling System using OpenRouter API
Provides candidate analysis and interviewer matching using Claude-3-Haiku
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class InterviewType(Enum):
    """Interview types"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CULTURAL_FIT = "cultural_fit"
    LEADERSHIP = "leadership"
    CODING = "coding"

@dataclass
class CandidateSkill:
    """Represents a candidate's skill"""
    name: str
    level: SkillLevel
    years_experience: float
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

@dataclass
class InterviewerProfile:
    """Interviewer profile for matching"""
    name: str
    email: str
    department: str
    expertise_areas: List[str]
    interview_types: List[InterviewType]
    seniority_level: str  # junior, mid, senior, staff, principal
    experience_years: float
    max_interviews_per_week: int
    preferred_technologies: List[str]
    rating: float = 4.5  # Average interviewer rating
    total_interviews: int = 0
    successful_hires: int = 0
    availability_hours: str = "9-17"  # Working hours
    timezone: str = "Asia/Kolkata"
    
    def __post_init__(self):
        if isinstance(self.interview_types, list) and self.interview_types and isinstance(self.interview_types[0], str):
            self.interview_types = [InterviewType(t) for t in self.interview_types]

@dataclass
class TechnicalSkills:
    """Technical skills assessment"""
    programming_languages: Dict[str, List[str]]
    frameworks_tools: Dict[str, List[str]]
    proficiency_score: float
    overall_toolset_score: float
    technical_depth_score: float
    technical_breadth_score: float
    learning_trajectory: str
    specialization_area: str

@dataclass
class ExperienceAnalysis:
    """Experience level analysis"""
    years_experience: float
    experience_level: str
    career_progression: str
    leadership_experience: Dict[str, Union[bool, int, float]]
    project_complexity: Dict[str, Union[str, float, List[str]]]
    industry_experience: List[str]
    experience_quality_score: float

@dataclass
class CompetencyScores:
    """Detailed competency scoring"""
    technical_skills: float
    problem_solving: float
    system_design: float
    communication: float
    leadership: float
    domain_knowledge: float
    learning_agility: float
    collaboration: float

@dataclass
class InterviewStrategy:
    """Interview approach recommendations"""
    primary_interview_type: str
    recommended_focus_areas: List[str]
    interview_duration: int
    interviewer_seniority: str
    assessment_priorities: List[str]

@dataclass
class HiringRecommendation:
    """Hiring decision support"""
    proceed_to_interview: bool
    recommended_role_level: str
    salary_expectation_assessment: str
    likelihood_of_success: str
    key_decision_factors: List[str]

@dataclass
class CandidateAnalysis:
    """Enhanced AI analysis result for candidate with comprehensive assessment"""
    candidate_name: str
    position: str
    
    # Detailed technical assessment
    technical_skills: TechnicalSkills
    experience_analysis: ExperienceAnalysis
    competency_scores: CompetencyScores
    
    # Overall scores (backward compatibility)
    overall_score: float  # 0-100
    technical_score: float  # 0-100
    experience_score: float  # 0-100
    skill_match_score: float  # 0-100
    cultural_fit_score: float  # 0-100
    
    # Key insights
    strengths: List[str]
    areas_for_growth: List[str]
    interview_strategy: InterviewStrategy
    red_flags: List[str]
    hiring_recommendation: HiringRecommendation
    
    # Legacy fields (for compatibility)
    weaknesses: List[str]  # Maps to areas_for_growth
    skill_gaps: List[str]  # Extracted from areas_for_growth
    recommended_interview_types: List[InterviewType]
    estimated_level: str
    summary: str  # Generated from overall assessment
    recommendations: List[str]  # From hiring_recommendation
    next_steps: List[str]
    
    # Metadata
    analysis_timestamp: str
    confidence_score: float  # 0-1
    
    def __post_init__(self):
        """Generate legacy fields from new structure for backward compatibility"""
        if not hasattr(self, 'weaknesses') or not self.weaknesses:
            self.weaknesses = self.areas_for_growth[:3]  # Limit to top 3
        
        if not hasattr(self, 'skill_gaps') or not self.skill_gaps:
            # Extract skill-related items from areas_for_growth
            self.skill_gaps = [area for area in self.areas_for_growth if 'skill' in area.lower() or 'technology' in area.lower()][:3]
        
        if not hasattr(self, 'estimated_level') or not self.estimated_level:
            self.estimated_level = self.experience_analysis.experience_level
        
        if not hasattr(self, 'summary') or not self.summary:
            self.summary = f"Candidate assessed as {self.estimated_level} level with overall score of {self.overall_score}/100. Primary strengths: {', '.join(self.strengths[:2])}."
        
        if not hasattr(self, 'recommendations') or not self.recommendations:
            self.recommendations = [
                f"Proceed to {self.interview_strategy.primary_interview_type} interview" if self.hiring_recommendation.proceed_to_interview else "Further screening needed",
                f"Focus on {', '.join(self.interview_strategy.recommended_focus_areas[:2])}"
            ]
        
        if not hasattr(self, 'recommended_interview_types') or not self.recommended_interview_types:
            # Map primary interview type to InterviewType enum
            type_mapping = {
                "technical": InterviewType.TECHNICAL,
                "product": InterviewType.BEHAVIORAL,
                "leadership": InterviewType.LEADERSHIP,
                "cultural": InterviewType.CULTURAL_FIT
            }
            primary_type = type_mapping.get(self.interview_strategy.primary_interview_type, InterviewType.TECHNICAL)
            self.recommended_interview_types = [primary_type]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization with enhanced structure"""
        result = {
            "candidate_name": self.candidate_name,
            "position": self.position,
            "technical_skills": {
                "programming_languages": self.technical_skills.programming_languages,
                "frameworks_tools": self.technical_skills.frameworks_tools,
                "proficiency_score": self.technical_skills.proficiency_score,
                "overall_toolset_score": self.technical_skills.overall_toolset_score,
                "technical_depth_score": self.technical_skills.technical_depth_score,
                "technical_breadth_score": self.technical_skills.technical_breadth_score,
                "learning_trajectory": self.technical_skills.learning_trajectory,
                "specialization_area": self.technical_skills.specialization_area
            },
            "experience_analysis": {
                "years_experience": self.experience_analysis.years_experience,
                "experience_level": self.experience_analysis.experience_level,
                "career_progression": self.experience_analysis.career_progression,
                "leadership_experience": self.experience_analysis.leadership_experience,
                "project_complexity": self.experience_analysis.project_complexity,
                "industry_experience": self.experience_analysis.industry_experience,
                "experience_quality_score": self.experience_analysis.experience_quality_score
            },
            "competency_scores": {
                "technical_skills": self.competency_scores.technical_skills,
                "problem_solving": self.competency_scores.problem_solving,
                "system_design": self.competency_scores.system_design,
                "communication": self.competency_scores.communication,
                "leadership": self.competency_scores.leadership,
                "domain_knowledge": self.competency_scores.domain_knowledge,
                "learning_agility": self.competency_scores.learning_agility,
                "collaboration": self.competency_scores.collaboration
            },
            "overall_assessment": {
                "overall_score": self.overall_score,
                "technical_score": self.technical_score,
                "experience_score": self.experience_score,
                "skill_match_score": self.skill_match_score,
                "cultural_fit_score": self.cultural_fit_score,
                "estimated_level": self.estimated_level,
                "confidence_score": self.confidence_score
            },
            "strengths": self.strengths,
            "areas_for_growth": self.areas_for_growth,
            "interview_strategy": {
                "primary_interview_type": self.interview_strategy.primary_interview_type,
                "recommended_focus_areas": self.interview_strategy.recommended_focus_areas,
                "interview_duration": self.interview_strategy.interview_duration,
                "interviewer_seniority": self.interview_strategy.interviewer_seniority,
                "assessment_priorities": self.interview_strategy.assessment_priorities
            },
            "hiring_recommendation": {
                "proceed_to_interview": self.hiring_recommendation.proceed_to_interview,
                "recommended_role_level": self.hiring_recommendation.recommended_role_level,
                "salary_expectation_assessment": self.hiring_recommendation.salary_expectation_assessment,
                "likelihood_of_success": self.hiring_recommendation.likelihood_of_success,
                "key_decision_factors": self.hiring_recommendation.key_decision_factors
            },
            "red_flags": self.red_flags,
            "next_steps": self.next_steps,
            "analysis_timestamp": self.analysis_timestamp,
            # Legacy fields for backward compatibility
            "weaknesses": self.weaknesses,
            "skill_gaps": self.skill_gaps,
            "recommended_interview_types": [t.value for t in self.recommended_interview_types],
            "summary": self.summary,
            "recommendations": self.recommendations
        }
        return result

@dataclass
class InterviewerMatch:
    """Interviewer matching result"""
    interviewer_name: str
    interviewer_email: str
    match_score: float  # 0-100
    expertise_match: float  # 0-100
    availability_match: float  # 0-100
    experience_match: float  # 0-100
    
    # Detailed reasoning
    matching_skills: List[str]
    interview_type: InterviewType
    estimated_duration: int  # minutes
    priority_level: str  # high, medium, low
    
    # AI reasoning
    why_matched: str
    potential_concerns: List[str]
    interview_focus_areas: List[str]
    suggested_questions: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['interview_type'] = self.interview_type.value
        return result

class AIService:
    """
    AI-powered candidate analysis and interviewer matching service using OpenRouter
    """
    
    def __init__(self, api_key: str = None, model: str = "deepseek/deepseek-chat-v3-0324:free"):
        """
        Initialize AI Service with OpenRouter API
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: AI model to use (default: deepseek/deepseek-chat-v3-0324:free for cost-effectiveness)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter. Get your key from: https://openrouter.ai/keys"
            )
        
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-org/rhero",  # Replace with your actual URL
            "X-Title": "RHero Interview Scheduling System"
        }
        
        # Model configurations for cost optimization
        self.model_configs = {
            "deepseek/deepseek-chat-v3-0324:free": {
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_1k_tokens": 0.0  # Free model!
            },
            "anthropic/claude-3-haiku": {
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_1k_tokens": 0.00025  # Very cost-effective
            },
            "anthropic/claude-3-sonnet": {
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_1k_tokens": 0.003
            },
            "openai/gpt-3.5-turbo": {
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_1k_tokens": 0.0015
            }
        }
        
        logger.info(f"AI Service initialized with model: {self.model}")
    
    def _make_api_call(self, messages: List[Dict], system_prompt: str = "") -> Optional[str]:
        """
        Make API call to OpenRouter
        
        Args:
            messages: List of message dictionaries
            system_prompt: System prompt to guide AI behavior
            
        Returns:
            AI response text or None if failed
        """
        try:
            # Prepare messages with system prompt
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            # Get model configuration
            config = self.model_configs.get(self.model, self.model_configs["deepseek/deepseek-chat-v3-0324:free"])
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": config["max_tokens"],
                "temperature": config["temperature"],
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            logger.info(f"Making API call to {self.model}")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Log usage for cost tracking
                usage = data.get('usage', {})
                total_tokens = usage.get('total_tokens', 0)
                estimated_cost = total_tokens * config["cost_per_1k_tokens"] / 1000
                
                logger.info(f"✅ AI API call successful")
                logger.info(f"   Tokens used: {total_tokens}")
                logger.info(f"   Estimated cost: ${estimated_cost:.6f}")
                
                return content
            else:
                logger.error(f"API call failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in AI API call: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in AI API call: {e}")
            return None
    
    def analyze_candidate(self, candidate: Union[CandidateProfile, Dict]) -> Optional[CandidateAnalysis]:
        """
        Analyze candidate profile using AI to assess technical fit and readiness
        
        Args:
            candidate: CandidateProfile object or dictionary with candidate data
            
        Returns:
            CandidateAnalysis object with detailed assessment or None if failed
        """
        try:
            # Convert dict to CandidateProfile if needed
            if isinstance(candidate, dict):
                candidate = CandidateProfile(**candidate)
            
            logger.info(f"🤖 Analyzing candidate: {candidate.name} for {candidate.position}")
            
            # Prepare detailed candidate information for AI
            candidate_info = f"""
CANDIDATE PROFILE ANALYSIS REQUEST

Name: {candidate.name}
Position Applied: {candidate.position}
Total Experience: {candidate.experience_years} years
Education: {candidate.education}

TECHNICAL SKILLS:
"""
            
            for skill in candidate.skills:
                candidate_info += f"- {skill.name}: {skill.level.value} level, {skill.years_experience} years experience"
                if skill.projects_count > 0:
                    candidate_info += f", {skill.projects_count} projects"
                if skill.certifications:
                    candidate_info += f", Certifications: {', '.join(skill.certifications)}"
                candidate_info += "\n"
            
            candidate_info += f"""
BACKGROUND:
Previous Companies: {', '.join(candidate.previous_companies) if candidate.previous_companies else 'Not specified'}
GitHub: {candidate.github_url or 'Not provided'}
LinkedIn: {candidate.linkedin_url or 'Not provided'}
Portfolio: {candidate.portfolio_url or 'Not provided'}

ADDITIONAL INFORMATION:
Cover Letter: {candidate.cover_letter[:500] + '...' if len(candidate.cover_letter) > 500 else candidate.cover_letter}
Resume Text: {candidate.resume_text[:1000] + '...' if len(candidate.resume_text) > 1000 else candidate.resume_text}
Salary Expectations: ${candidate.preferred_salary:,.2f} {f'({candidate.preferred_salary:,.2f})' if candidate.preferred_salary > 0 else 'Not specified'}
Availability: {candidate.availability or 'Not specified'}
"""
            
            system_prompt = """You are an expert technical recruiter and senior hiring manager with 15+ years of experience in evaluating software engineering candidates. Your role is to provide comprehensive, data-driven assessments that help optimize interview processes and hiring decisions.

ANALYSIS FRAMEWORK:
1. TECHNICAL SKILLS ASSESSMENT (40% weight)
   - Parse resume text for technical keywords, frameworks, languages
   - Evaluate depth vs breadth of technology stack
   - Assess progression and learning trajectory
   - Identify specialized vs generalist skill patterns

2. EXPERIENCE LEVEL EVALUATION (30% weight)
   - Junior (0-2 years): Learning fundamentals, guided work
   - Mid-level (3-5 years): Independent contributor, some mentoring
   - Senior (6-9 years): Technical leadership, architecture decisions
   - Staff+ (10+ years): Strategic thinking, cross-team influence
   - Consider quality of experience, not just years

3. COMPETENCY SCORING (0-100 scale)
   - Technical Skills: Language proficiency, framework expertise, tools mastery
   - Problem Solving: Complexity of projects, innovation indicators
   - Leadership: Mentoring, team lead experience, initiative taking
   - Communication: Writing quality, presentation of experience
   - Domain Knowledge: Industry-specific expertise, business understanding

4. INTERVIEW STRATEGY OPTIMIZATION
   - Technical: For IC roles, deep technical assessment needed
   - Product: For product-focused roles, user empathy, business acumen
   - Leadership: For senior roles, people management, strategic thinking
   - Cultural: For team fit, values alignment, collaboration style

EVALUATION CRITERIA:
- Be objective and evidence-based, citing specific resume content
- Identify both strengths and improvement areas
- Consider role requirements and market standards
- Provide actionable interview recommendations
- Flag any red flags or inconsistencies

RESPONSE FORMAT: Return ONLY valid JSON with numerical scores and structured insights. No markdown, no additional text."""
            
            user_prompt = f"""CANDIDATE EVALUATION REQUEST

{candidate_info}

ANALYSIS INSTRUCTIONS:
1. Extract and evaluate technical skills from resume text and stated experience
2. Determine experience level based on years, responsibilities, and complexity of work
3. Identify key strengths that make this candidate valuable
4. Determine optimal interview approach based on role and candidate profile
5. Provide numerical assessments with supporting evidence

Respond with this EXACT JSON structure:

{{
    "technical_skills": {{
        "programming_languages": {{
            "primary": ["language1", "language2"],
            "secondary": ["language3"],
            "proficiency_score": <0-100>
        }},
        "frameworks_tools": {{
            "web_frameworks": ["framework1", "framework2"],
            "databases": ["db1", "db2"],
            "cloud_platforms": ["platform1"],
            "devops_tools": ["tool1", "tool2"],
            "overall_toolset_score": <0-100>
        }},
        "technical_depth_score": <0-100>,
        "technical_breadth_score": <0-100>,
        "learning_trajectory": "ascending|stable|declining",
        "specialization_area": "frontend|backend|fullstack|devops|data|mobile|other"
    }},
    "experience_analysis": {{
        "years_experience": <float>,
        "experience_level": "junior|mid|senior|staff|principal",
        "career_progression": "rapid|steady|slow|lateral",
        "leadership_experience": {{
            "has_leadership": <true/false>,
            "team_size_managed": <number>,
            "leadership_score": <0-100>
        }},
        "project_complexity": {{
            "scale": "small|medium|large|enterprise",
            "complexity_score": <0-100>,
            "innovation_indicators": ["indicator1", "indicator2"]
        }},
        "industry_experience": ["industry1", "industry2"],
        "experience_quality_score": <0-100>
    }},
    "competency_scores": {{
        "technical_skills": <0-100>,
        "problem_solving": <0-100>,
        "system_design": <0-100>,
        "communication": <0-100>,
        "leadership": <0-100>,
        "domain_knowledge": <0-100>,
        "learning_agility": <0-100>,
        "collaboration": <0-100>
    }},
    "overall_assessment": {{
        "overall_score": <0-100>,
        "technical_score": <0-100>,
        "experience_score": <0-100>,
        "skill_match_score": <0-100>,
        "cultural_fit_score": <0-100>,
        "estimated_level": "junior|mid|senior|staff|principal",
        "confidence_score": <0.0-1.0>
    }},
    "strengths": [
        "Specific strength with evidence from resume",
        "Another strength with measurable impact",
        "Third strength with technical detail"
    ],
    "areas_for_growth": [
        "Specific area needing development",
        "Skill gap relative to position requirements"
    ],
    "interview_strategy": {{
        "primary_interview_type": "technical|product|leadership|cultural",
        "recommended_focus_areas": [
            "System design and architecture",
            "Code quality and best practices",
            "Team collaboration experience"
        ],
        "interview_duration": <30|45|60|90>,
        "interviewer_seniority": "mid|senior|staff|principal",
        "assessment_priorities": [
            "Technical depth in core technologies",
            "Problem-solving approach",
            "Communication and collaboration style"
        ]
    }},
    "red_flags": [
        "Concern 1 if any",
        "Concern 2 if any"
    ],
    "hiring_recommendation": {{
        "proceed_to_interview": <true/false>,
        "recommended_role_level": "junior|mid|senior|staff",
        "salary_expectation_assessment": "below_market|market_rate|above_market",
        "likelihood_of_success": "low|medium|high",
        "key_decision_factors": [
            "Factor 1 to evaluate in interview",
            "Factor 2 to validate"
        ]
    }},
    "next_steps": [
        "Schedule technical interview focusing on X",
        "Prepare questions about Y experience",
        "Validate Z through practical assessment"
    ]
}}

IMPORTANT: Base your analysis on actual resume content and stated experience. Provide specific, evidence-based assessments with numerical scores that reflect candidate capabilities accurately."""
            
            messages = [{"role": "user", "content": user_prompt}]
            
            response = self._make_api_call(messages, system_prompt)
            
            if not response:
                logger.error("Failed to get AI response for candidate analysis")
                return None
            
            # Parse JSON response
            try:
                # Clean response to extract JSON
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:-3]
                elif response.startswith('```'):
                    response = response[3:-3]
                
                analysis_data = json.loads(response)
                
                # Extract the enhanced data structure
                tech_skills_data = analysis_data.get('technical_skills', {})
                exp_data = analysis_data.get('experience_analysis', {})
                competency_data = analysis_data.get('competency_scores', {})
                overall_data = analysis_data.get('overall_assessment', {})
                interview_strategy_data = analysis_data.get('interview_strategy', {})
                hiring_rec_data = analysis_data.get('hiring_recommendation', {})
                
                # Create technical skills object
                technical_skills = TechnicalSkills(
                    programming_languages=tech_skills_data.get('programming_languages', {}),
                    frameworks_tools=tech_skills_data.get('frameworks_tools', {}),
                    proficiency_score=tech_skills_data.get('proficiency_score', 0),
                    overall_toolset_score=tech_skills_data.get('overall_toolset_score', 0),
                    technical_depth_score=tech_skills_data.get('technical_depth_score', 0),
                    technical_breadth_score=tech_skills_data.get('technical_breadth_score', 0),
                    learning_trajectory=tech_skills_data.get('learning_trajectory', 'stable'),
                    specialization_area=tech_skills_data.get('specialization_area', 'fullstack')
                )
                
                # Create experience analysis object
                experience_analysis = ExperienceAnalysis(
                    years_experience=exp_data.get('years_experience', candidate.experience_years),
                    experience_level=exp_data.get('experience_level', 'mid'),
                    career_progression=exp_data.get('career_progression', 'steady'),
                    leadership_experience=exp_data.get('leadership_experience', {'has_leadership': False, 'team_size_managed': 0, 'leadership_score': 0}),
                    project_complexity=exp_data.get('project_complexity', {'scale': 'medium', 'complexity_score': 50, 'innovation_indicators': []}),
                    industry_experience=exp_data.get('industry_experience', []),
                    experience_quality_score=exp_data.get('experience_quality_score', 50)
                )
                
                # Create competency scores object
                competency_scores = CompetencyScores(
                    technical_skills=competency_data.get('technical_skills', 0),
                    problem_solving=competency_data.get('problem_solving', 0),
                    system_design=competency_data.get('system_design', 0),
                    communication=competency_data.get('communication', 0),
                    leadership=competency_data.get('leadership', 0),
                    domain_knowledge=competency_data.get('domain_knowledge', 0),
                    learning_agility=competency_data.get('learning_agility', 0),
                    collaboration=competency_data.get('collaboration', 0)
                )
                
                # Create interview strategy object
                interview_strategy = InterviewStrategy(
                    primary_interview_type=interview_strategy_data.get('primary_interview_type', 'technical'),
                    recommended_focus_areas=interview_strategy_data.get('recommended_focus_areas', []),
                    interview_duration=interview_strategy_data.get('interview_duration', 60),
                    interviewer_seniority=interview_strategy_data.get('interviewer_seniority', 'senior'),
                    assessment_priorities=interview_strategy_data.get('assessment_priorities', [])
                )
                
                # Create hiring recommendation object
                hiring_recommendation = HiringRecommendation(
                    proceed_to_interview=hiring_rec_data.get('proceed_to_interview', True),
                    recommended_role_level=hiring_rec_data.get('recommended_role_level', 'mid'),
                    salary_expectation_assessment=hiring_rec_data.get('salary_expectation_assessment', 'market_rate'),
                    likelihood_of_success=hiring_rec_data.get('likelihood_of_success', 'medium'),
                    key_decision_factors=hiring_rec_data.get('key_decision_factors', [])
                )
                
                # Convert to CandidateAnalysis object with enhanced structure
                analysis = CandidateAnalysis(
                    candidate_name=candidate.name,
                    position=candidate.position,
                    technical_skills=technical_skills,
                    experience_analysis=experience_analysis,
                    competency_scores=competency_scores,
                    overall_score=overall_data.get('overall_score', 0),
                    technical_score=overall_data.get('technical_score', 0),
                    experience_score=overall_data.get('experience_score', 0),
                    skill_match_score=overall_data.get('skill_match_score', 0),
                    cultural_fit_score=overall_data.get('cultural_fit_score', 0),
                    strengths=analysis_data.get('strengths', []),
                    areas_for_growth=analysis_data.get('areas_for_growth', []),
                    interview_strategy=interview_strategy,
                    red_flags=analysis_data.get('red_flags', []),
                    hiring_recommendation=hiring_recommendation,
                    weaknesses=analysis_data.get('areas_for_growth', [])[:3],  # Legacy compatibility
                    skill_gaps=[],  # Will be populated in __post_init__
                    recommended_interview_types=[],  # Will be populated in __post_init__
                    estimated_level=overall_data.get('estimated_level', exp_data.get('experience_level', 'mid')),
                    summary="",  # Will be generated in __post_init__
                    recommendations=[],  # Will be populated in __post_init__
                    next_steps=analysis_data.get('next_steps', []),
                    analysis_timestamp=datetime.now().isoformat(),
                    confidence_score=overall_data.get('confidence_score', 0.8)
                )
                
                logger.info(f"✅ Enhanced candidate analysis completed for {candidate.name}")
                logger.info(f"   Overall Score: {analysis.overall_score}/100")
                logger.info(f"   Technical Skills: {analysis.competency_scores.technical_skills}/100")
                logger.info(f"   Experience Level: {analysis.estimated_level} ({analysis.experience_analysis.years_experience} years)")
                logger.info(f"   Specialization: {analysis.technical_skills.specialization_area}")
                logger.info(f"   Primary Interview Type: {analysis.interview_strategy.primary_interview_type}")
                logger.info(f"   Proceed to Interview: {'Yes' if analysis.hiring_recommendation.proceed_to_interview else 'No'}")
                logger.info(f"   Key Strengths: {', '.join(analysis.strengths[:2])}")
                if analysis.red_flags:
                    logger.warning(f"   Red Flags: {', '.join(analysis.red_flags[:2])}")
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response JSON: {e}")
                logger.error(f"Response was: {response[:500]}...")
                return None
            
        except Exception as e:
            logger.error(f"Unexpected error in candidate analysis: {e}")
            return None
    
    def match_interviewer(
        self,
        candidate: Union[CandidateProfile, Dict],
        candidate_analysis: Union[CandidateAnalysis, Dict],
        available_interviewers: List[Union[InterviewerProfile, Dict]],
        interview_type: Union[InterviewType, str] = InterviewType.TECHNICAL
    ) -> List[InterviewerMatch]:
        """
        Find best interviewer matches for a candidate using AI analysis
        
        Args:
            candidate: Candidate profile
            candidate_analysis: AI analysis of candidate (from analyze_candidate)
            available_interviewers: List of available interviewer profiles
            interview_type: Type of interview to conduct
            
        Returns:
            List of InterviewerMatch objects sorted by match score (best first)
        """
        try:
            # Convert inputs to proper objects
            if isinstance(candidate, dict):
                candidate = CandidateProfile(**candidate)
            
            if isinstance(candidate_analysis, dict):
                candidate_analysis = CandidateAnalysis(**candidate_analysis)
            
            if isinstance(interview_type, str):
                interview_type = InterviewType(interview_type)
            
            # Convert interviewer dicts to objects
            interviewers = []
            for interviewer in available_interviewers:
                if isinstance(interviewer, dict):
                    interviewers.append(InterviewerProfile(**interviewer))
                else:
                    interviewers.append(interviewer)
            
            logger.info(f"🔍 Finding interviewer matches for {candidate.name}")
            logger.info(f"   Interview Type: {interview_type.value}")
            logger.info(f"   Available Interviewers: {len(interviewers)}")
            
            # Prepare candidate summary for AI
            candidate_summary = f"""
CANDIDATE: {candidate.name}
Position: {candidate.position}
Experience: {candidate.experience_years} years
Estimated Level: {candidate_analysis.estimated_level}

AI ANALYSIS SCORES:
- Overall: {candidate_analysis.overall_score}/100
- Technical: {candidate_analysis.technical_score}/100
- Experience: {candidate_analysis.experience_score}/100

KEY SKILLS:
{', '.join([f"{skill.name} ({skill.level.value})" for skill in candidate.skills[:5]])}

STRENGTHS: {', '.join(candidate_analysis.strengths[:3])}
SKILL GAPS: {', '.join(candidate_analysis.skill_gaps[:3])}
"""
            
            # Prepare interviewer information
            interviewer_info = "AVAILABLE INTERVIEWERS:\n"
            for i, interviewer in enumerate(interviewers):
                interviewer_info += f"""
{i+1}. {interviewer.name} ({interviewer.email})
   Department: {interviewer.department}
   Seniority: {interviewer.seniority_level}
   Experience: {interviewer.experience_years} years
   Expertise: {', '.join(interviewer.expertise_areas[:5])}
   Interview Types: {', '.join([t.value for t in interviewer.interview_types])}
   Technologies: {', '.join(interviewer.preferred_technologies[:5])}
   Rating: {interviewer.rating}/5.0
   Total Interviews: {interviewer.total_interviews}
   Success Rate: {(interviewer.successful_hires/max(interviewer.total_interviews,1)*100):.1f}%
"""
            
            system_prompt = f"""You are an expert interview coordinator. Match candidates with the most suitable interviewers based on:

1. Technical expertise alignment
2. Experience level compatibility  
3. Interview type specialization
4. Past performance metrics
5. Skill complementarity

For {interview_type.value} interviews, prioritize technical skill overlap and appropriate seniority levels.

Provide objective scoring and specific reasoning for each match.

IMPORTANT: Respond ONLY with a valid JSON array. No additional text."""
            
            user_prompt = f"""Match this candidate with the best interviewers for a {interview_type.value} interview:

{candidate_summary}

{interviewer_info}

Return a JSON array with ALL interviewers ranked by match quality:

[
  {{
    "interviewer_name": "Name",
    "interviewer_email": "email@company.com", 
    "match_score": <0-100>,
    "expertise_match": <0-100>,
    "availability_match": <0-100>,
    "experience_match": <0-100>,
    "matching_skills": ["skill1", "skill2"],
    "estimated_duration": <minutes>,
    "priority_level": "high|medium|low",
    "why_matched": "Detailed reasoning",
    "potential_concerns": ["concern1", "concern2"],
    "interview_focus_areas": ["area1", "area2"],
    "suggested_questions": ["question1", "question2"]
  }}
]

Rank by overall match quality. Include specific technical reasoning."""
            
            messages = [{"role": "user", "content": user_prompt}]
            
            response = self._make_api_call(messages, system_prompt)
            
            if not response:
                logger.error("Failed to get AI response for interviewer matching")
                return []
            
            # Parse JSON response
            try:
                # Clean response to extract JSON
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:-3]
                elif response.startswith('```'):
                    response = response[3:-3]
                
                matches_data = json.loads(response)
                
                # Convert to InterviewerMatch objects
                matches = []
                for match_data in matches_data:
                    match = InterviewerMatch(
                        interviewer_name=match_data.get('interviewer_name', ''),
                        interviewer_email=match_data.get('interviewer_email', ''),
                        match_score=match_data.get('match_score', 0),
                        expertise_match=match_data.get('expertise_match', 0),
                        availability_match=match_data.get('availability_match', 0),
                        experience_match=match_data.get('experience_match', 0),
                        matching_skills=match_data.get('matching_skills', []),
                        interview_type=interview_type,
                        estimated_duration=match_data.get('estimated_duration', 60),
                        priority_level=match_data.get('priority_level', 'medium'),
                        why_matched=match_data.get('why_matched', ''),
                        potential_concerns=match_data.get('potential_concerns', []),
                        interview_focus_areas=match_data.get('interview_focus_areas', []),
                        suggested_questions=match_data.get('suggested_questions', [])
                    )
                    matches.append(match)
                
                # Sort by match score (highest first)
                matches.sort(key=lambda x: x.match_score, reverse=True)
                
                logger.info(f"✅ Interviewer matching completed")
                logger.info(f"   Found {len(matches)} potential matches")
                if matches:
                    logger.info(f"   Best Match: {matches[0].interviewer_name} (Score: {matches[0].match_score}/100)")
                    logger.info(f"   Top 3 Matches: {[f'{m.interviewer_name}({m.match_score})' for m in matches[:3]]}")
                
                return matches
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse interviewer matching JSON: {e}")
                logger.error(f"Response was: {response[:500]}...")
                return []
            
        except Exception as e:
            logger.error(f"Unexpected error in interviewer matching: {e}")
            return []
    
    def generate_interview_questions(
        self,
        candidate: Union[CandidateProfile, Dict],
        interviewer: Union[InterviewerProfile, Dict],
        interview_type: Union[InterviewType, str],
        analysis: Union[CandidateAnalysis, Dict] = None,
        question_count: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Generate customized interview questions based on candidate profile and interviewer expertise
        
        Args:
            candidate: Candidate profile
            interviewer: Interviewer profile  
            interview_type: Type of interview
            analysis: Optional candidate analysis for context
            question_count: Number of questions to generate
            
        Returns:
            Dictionary with categorized questions and metadata
        """
        try:
            # Convert inputs to proper objects
            if isinstance(candidate, dict):
                candidate = CandidateProfile(**candidate)
            if isinstance(interviewer, dict):
                interviewer = InterviewerProfile(**interviewer)
            if isinstance(interview_type, str):
                interview_type = InterviewType(interview_type)
            if isinstance(analysis, dict):
                analysis = CandidateAnalysis(**analysis)
            
            logger.info(f"🎯 Generating {interview_type.value} questions for {candidate.name}")
            
            context = f"""
INTERVIEW CONTEXT:
Candidate: {candidate.name} - {candidate.position}
Experience: {candidate.experience_years} years
Key Skills: {', '.join([skill.name for skill in candidate.skills[:5]])}

Interviewer: {interviewer.name} - {interviewer.department}
Expertise: {', '.join(interviewer.expertise_areas[:3])}
Seniority: {interviewer.seniority_level}

Interview Type: {interview_type.value}
"""
            
            if analysis:
                context += f"""
AI ANALYSIS:
Estimated Level: {analysis.estimated_level}
Technical Score: {analysis.technical_score}/100
Strengths: {', '.join(analysis.strengths[:3])}
Areas to Assess: {', '.join(analysis.skill_gaps[:3])}
"""
            
            system_prompt = """You are an expert interview designer. Create targeted, high-quality interview questions that:

1. Assess candidate skills relevant to the position
2. Match the interviewer's expertise areas
3. Are appropriate for the interview type and candidate level
4. Include follow-up questions and evaluation criteria
5. Cover both technical depth and practical application

Provide questions with difficulty levels and clear assessment guidelines."""
            
            user_prompt = f"""Generate {question_count} targeted interview questions for this scenario:

{context}

Return a JSON object in this format:
{{
    "interview_type": "{interview_type.value}",
    "estimated_duration": <minutes>,
    "difficulty_level": "junior|mid|senior|expert",
    "questions": [
        {{
            "id": 1,
            "category": "technical|behavioral|problem_solving|system_design",
            "difficulty": "easy|medium|hard",
            "question": "Question text",
            "follow_up_questions": ["follow-up 1", "follow-up 2"],
            "evaluation_criteria": ["criteria 1", "criteria 2"],
            "expected_answer_points": ["point 1", "point 2"],
            "time_allocation": <minutes>
        }}
    ],
    "assessment_focus": ["area1", "area2"],
    "interview_flow": ["phase1", "phase2", "phase3"],
    "preparation_notes": ["note1", "note2"]
}}

Focus on practical, role-relevant questions that help assess candidate fit."""
            
            messages = [{"role": "user", "content": user_prompt}]
            
            response = self._make_api_call(messages, system_prompt)
            
            if not response:
                logger.error("Failed to generate interview questions")
                return None
            
            # Parse JSON response
            try:
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:-3]
                elif response.startswith('```'):
                    response = response[3:-3]
                
                questions_data = json.loads(response)
                
                logger.info(f"✅ Generated {len(questions_data.get('questions', []))} interview questions")
                logger.info(f"   Difficulty Level: {questions_data.get('difficulty_level', 'N/A')}")
                logger.info(f"   Estimated Duration: {questions_data.get('estimated_duration', 'N/A')} minutes")
                
                return questions_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse interview questions JSON: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current AI model and configuration
        
        Returns:
            Dictionary with model details and cost information
        """
        config = self.model_configs.get(self.model, {})
        
        return {
            "model": self.model,
            "max_tokens": config.get("max_tokens", 4000),
            "temperature": config.get("temperature", 0.3),
            "cost_per_1k_tokens": config.get("cost_per_1k_tokens", 0.0),
            "provider": self.model.split('/')[0] if '/' in self.model else "unknown",
            "features": [
                "candidate_analysis",
                "interviewer_matching", 
                "question_generation",
                "structured_json_output",
                "cost_optimization"
            ],
            "api_endpoint": self.base_url,
            "recommended_for": "cost-effective candidate screening and interview planning"
        }

# Utility functions for easy integration

def create_sample_candidate() -> CandidateProfile:
    """Create a sample candidate profile for testing"""
    return CandidateProfile(
        name="John Doe",
        email="john.doe@email.com",
        position="Senior Python Developer",
        experience_years=5.5,
        skills=[
            CandidateSkill("Python", SkillLevel.ADVANCED, 5.0, 8, ["AWS Certified"]),
            CandidateSkill("Django", SkillLevel.ADVANCED, 4.0, 6),
            CandidateSkill("React", SkillLevel.INTERMEDIATE, 2.0, 3),
            CandidateSkill("PostgreSQL", SkillLevel.ADVANCED, 4.5, 5),
            CandidateSkill("Docker", SkillLevel.INTERMEDIATE, 2.5, 4)
        ],
        education="BS Computer Science",
        previous_companies=["TechCorp", "StartupXYZ", "BigTech Inc"],
        github_url="https://github.com/johndoe",
        linkedin_url="https://linkedin.com/in/johndoe",
        cover_letter="Passionate Python developer with 5+ years building scalable web applications...",
        resume_text="Senior Python Developer with expertise in Django, React, and cloud deployment...",
        preferred_salary=120000.0,
        availability="Available immediately"
    )

def create_sample_interviewers() -> List[InterviewerProfile]:
    """Create sample interviewer profiles for testing"""
    return [
        InterviewerProfile(
            name="Alice Johnson",
            email="alice.johnson@company.com",
            department="Engineering",
            expertise_areas=["Python", "Django", "System Design", "Microservices"],
            interview_types=[InterviewType.TECHNICAL, InterviewType.SYSTEM_DESIGN],
            seniority_level="senior",
            experience_years=8.0,
            max_interviews_per_week=5,
            preferred_technologies=["Python", "Django", "PostgreSQL", "AWS"],
            rating=4.8,
            total_interviews=150,
            successful_hires=45
        ),
        InterviewerProfile(
            name="Bob Chen",
            email="bob.chen@company.com", 
            department="Engineering",
            expertise_areas=["Frontend", "React", "JavaScript", "UI/UX"],
            interview_types=[InterviewType.TECHNICAL, InterviewType.CODING],
            seniority_level="mid",
            experience_years=5.0,
            max_interviews_per_week=6,
            preferred_technologies=["React", "JavaScript", "TypeScript", "CSS"],
            rating=4.6,
            total_interviews=85,
            successful_hires=28
        ),
        InterviewerProfile(
            name="Carol Martinez",
            email="carol.martinez@company.com",
            department="HR",
            expertise_areas=["Cultural Fit", "Communication", "Leadership", "Team Dynamics"],
            interview_types=[InterviewType.BEHAVIORAL, InterviewType.CULTURAL_FIT],
            seniority_level="senior",
            experience_years=10.0,
            max_interviews_per_week=8,
            preferred_technologies=[],
            rating=4.9,
            total_interviews=200,
            successful_hires=75
        )
    ]

# Example usage demonstration
if __name__ == "__main__":
    """
    Example usage of the AI Service
    """
    print("🤖 AI Service for Interview Scheduling - Demo")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        print("   Get your key from: https://openrouter.ai/keys")
        exit(1)
    
    # Initialize AI service
    ai_service = AIService()
    
    print(f"✅ AI Service initialized with model: {ai_service.model}")
    print(f"   Cost per 1K tokens: ${ai_service.model_configs[ai_service.model]['cost_per_1k_tokens']}")
    
    # Create sample data
    candidate = create_sample_candidate()
    interviewers = create_sample_interviewers()
    
    print(f"\n📊 Sample Data Created:")
    print(f"   Candidate: {candidate.name} - {candidate.position}")
    print(f"   Skills: {', '.join([skill.name for skill in candidate.skills])}")
    print(f"   Interviewers: {len(interviewers)} available")
    
    print(f"\n🔍 Running AI Analysis...")
    
    try:
        # Analyze candidate
        analysis = ai_service.analyze_candidate(candidate)
        if analysis:
            print(f"✅ Candidate Analysis Complete:")
            print(f"   Overall Score: {analysis.overall_score}/100")
            print(f"   Technical Score: {analysis.technical_score}/100")
            print(f"   Estimated Level: {analysis.estimated_level}")
            print(f"   Strengths: {', '.join(analysis.strengths[:3])}")
            
            # Find interviewer matches
            matches = ai_service.match_interviewer(candidate, analysis, interviewers)
            if matches:
                print(f"\n✅ Interviewer Matching Complete:")
                print(f"   Found {len(matches)} potential matches")
                for i, match in enumerate(matches[:3]):
                    print(f"   {i+1}. {match.interviewer_name} - Score: {match.match_score}/100")
                    print(f"      Expertise Match: {match.expertise_match}/100")
                    print(f"      Why: {match.why_matched[:100]}...")
                
                # Generate questions for best match
                if matches:
                    best_match = matches[0]
                    best_interviewer = next(
                        (i for i in interviewers if i.email == best_match.interviewer_email), 
                        interviewers[0]
                    )
                    
                    questions = ai_service.generate_interview_questions(
                        candidate, best_interviewer, InterviewType.TECHNICAL, analysis, 5
                    )
                    
                    if questions:
                        print(f"\n✅ Interview Questions Generated:")
                        print(f"   Type: {questions['interview_type']}")
                        print(f"   Duration: {questions['estimated_duration']} minutes") 
                        print(f"   Questions: {len(questions['questions'])}")
                        
                        for i, q in enumerate(questions['questions'][:2]):
                            print(f"   {i+1}. [{q['category']}] {q['question'][:80]}...")
            
            print(f"\n🎯 Demo completed successfully!")
            
        else:
            print("❌ Candidate analysis failed")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
