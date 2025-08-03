"""
Smart Interviewer Matching Algorithm
====================================

Intelligent matching system that combines:
- AI-powered candidate analysis 
- Interviewer expertise assessment
- Google Calendar availability checking
- Confidence scoring with fallback logic
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict

# Import our existing services
from ai_service import AIService, CandidateAnalysis, CandidateProfile, InterviewerProfile as AIInterviewerProfile, InterviewType, CandidateSkill
from google_calendar_service import GoogleCalendarService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchConfidence(Enum):
    """Match confidence levels"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 75-89%
    FAIR = "fair"           # 60-74%
    POOR = "poor"           # 40-59%
    INSUFFICIENT = "insufficient"  # <40%


@dataclass
class AvailabilitySlot:
    """Represents an available time slot for an interviewer"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    is_preferred_time: bool = False  # Peak hours for interviewer
    
    def overlaps_with(self, other: 'AvailabilitySlot') -> bool:
        """Check if this slot overlaps with another"""
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)


@dataclass
class InterviewerProfile:
    """Enhanced interviewer profile with detailed expertise"""
    interviewer: Interviewer
    technical_expertise: Dict[str, int]  # skill -> proficiency (0-100)
    seniority_level: str  # junior, mid, senior, staff, principal
    interview_types_preferred: List[InterviewType]
    max_interviews_per_day: int = 4
    preferred_interview_duration: int = 60  # minutes
    time_zone: str = "UTC"
    languages_fluent: List[str] = field(default_factory=lambda: ["English"])
    specialization_areas: List[str] = field(default_factory=list)
    years_interviewing: int = 0
    success_rate: float = 0.85  # Historical interview success rate
    candidate_feedback_score: float = 4.2  # Out of 5.0
    
    def expertise_score_for_skills(self, skills: List[str]) -> float:
        """Calculate expertise score for given skills"""
        if not skills:
            return 0.0
            
        total_score = 0
        matched_skills = 0
        
        for skill in skills:
            skill_lower = skill.lower()
            # Check exact match first
            if skill_lower in self.technical_expertise:
                total_score += self.technical_expertise[skill_lower]
                matched_skills += 1
            else:
                # Check for partial matches (e.g., "react" in "reactjs")
                for expert_skill, score in self.technical_expertise.items():
                    if (skill_lower in expert_skill or 
                        expert_skill in skill_lower):
                        total_score += score * 0.8  # Partial match penalty
                        matched_skills += 1
                        break
        
        if matched_skills == 0:
            return 0.0
        
        # Calculate average and apply coverage bonus
        avg_score = total_score / matched_skills
        coverage_ratio = matched_skills / len(skills)
        
        return avg_score * (0.7 + 0.3 * coverage_ratio)


@dataclass
class MatchResult:
    """Result of interviewer matching with detailed scoring"""
    interviewer_profile: InterviewerProfile
    candidate: Candidate
    candidate_analysis: CandidateAnalysis
    
    # Scoring components
    technical_match_score: float  # 0-100
    seniority_match_score: float  # 0-100
    availability_score: float     # 0-100
    interview_type_score: float   # 0-100
    experience_match_score: float # 0-100
    
    # Composite scores
    overall_match_score: float    # 0-100
    confidence_level: MatchConfidence
    
    # Availability details
    available_slots: List[AvailabilitySlot]
    recommended_slot: Optional[AvailabilitySlot]
    
    # Match explanation
    match_reasons: List[str]
    potential_concerns: List[str]
    
    # Metadata
    calculated_at: datetime = field(default_factory=datetime.now)
    ai_model_used: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match result to dictionary for API responses"""
        return {
            "interviewer": {
                "name": self.interviewer_profile.interviewer.name,
                "email": self.interviewer_profile.interviewer.email,
                "seniority": self.interviewer_profile.seniority_level,
                "success_rate": self.interviewer_profile.success_rate
            },
            "scores": {
                "overall_match": round(self.overall_match_score, 1),
                "technical_match": round(self.technical_match_score, 1),
                "seniority_match": round(self.seniority_match_score, 1),
                "availability": round(self.availability_score, 1),
                "interview_type": round(self.interview_type_score, 1),
                "experience_match": round(self.experience_match_score, 1)
            },
            "confidence": self.confidence_level.value,
            "available_slots": len(self.available_slots),
            "recommended_time": (
                self.recommended_slot.start_time.isoformat() 
                if self.recommended_slot else None
            ),
            "match_reasons": self.match_reasons,
            "concerns": self.potential_concerns,
            "metadata": {
                "calculated_at": self.calculated_at.isoformat(),
                "ai_model": self.ai_model_used
            }
        }


class SmartMatchingAlgorithm:
    """
    Intelligent interviewer matching algorithm that combines:
    - AI candidate analysis
    - Technical expertise matching
    - Calendar availability checking
    - Confidence scoring with fallback logic
    """
    
    def __init__(self, 
                 ai_service: AIService,
                 calendar_service: GoogleCalendarService):
        self.ai_service = ai_service
        self.calendar_service = calendar_service
        
        # Matching weights (should sum to 1.0)
        self.weights = {
            'technical_match': 0.35,
            'seniority_match': 0.25,
            'availability': 0.20,
            'interview_type': 0.15,
            'experience_match': 0.05
        }
        
        # Fallback thresholds
        self.min_acceptable_score = 40.0
        self.preferred_score = 75.0
        self.excellent_score = 90.0
        
    async def find_best_matches(self,
                              candidate: Candidate,
                              interviewer_profiles: List[InterviewerProfile],
                              interview_date_range: Tuple[datetime, datetime],
                              required_interview_type: InterviewType,
                              max_results: int = 5) -> List[MatchResult]:
        """
        Find the best interviewer matches for a candidate
        
        Args:
            candidate: Candidate to match
            interviewer_profiles: Available interviewer profiles
            interview_date_range: (start_date, end_date) for scheduling
            required_interview_type: Type of interview needed
            max_results: Maximum number of results to return
            
        Returns:
            List of MatchResult objects sorted by overall score
        """
        logger.info(f"🔍 Finding matches for {candidate.name}")
        
        # Step 1: Analyze candidate with AI
        candidate_analysis = await self._analyze_candidate(candidate)
        
        # Step 2: Score all interviewers
        match_results = []
        
        for profile in interviewer_profiles:
            try:
                match_result = await self._calculate_match_score(
                    candidate=candidate,
                    candidate_analysis=candidate_analysis,
                    interviewer_profile=profile,
                    interview_date_range=interview_date_range,
                    required_interview_type=required_interview_type
                )
                
                if match_result:
                    match_results.append(match_result)
                    
            except Exception as e:
                logger.warning(f"Error matching with {profile.interviewer.name}: {e}")
                continue
        
        # Step 3: Sort by overall score and apply fallback logic
        sorted_matches = sorted(match_results, 
                              key=lambda x: x.overall_match_score, 
                              reverse=True)
        
        # Step 4: Apply fallback logic if needed
        final_matches = self._apply_fallback_logic(
            sorted_matches, 
            candidate_analysis, 
            required_interview_type
        )
        
        logger.info(f"✅ Found {len(final_matches)} suitable matches")
        return final_matches[:max_results]
    
    async def _analyze_candidate(self, candidate: Candidate) -> CandidateAnalysis:
        """Analyze candidate using AI service"""
        try:
            analysis = await asyncio.to_thread(
                self.ai_service.analyze_candidate, 
                candidate
            )
            logger.info(f"📊 AI Analysis complete - Score: {analysis.overall_score}/100")
            return analysis
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return basic analysis as fallback
            return self._create_basic_analysis(candidate)
    
    def _create_basic_analysis(self, candidate: Candidate) -> CandidateAnalysis:
        """Create basic analysis when AI fails"""
        from ai_service import CompetencyScores, TechnicalSkills, ExperienceAnalysis
        
        return CandidateAnalysis(
            overall_score=70.0,  # Default score
            technical_score=70.0,
            estimated_level=self._estimate_level_from_experience(candidate.experience_years),
            strengths=["Technical background", "Relevant experience"],
            areas_for_improvement=["Needs assessment"],
            competency_scores=CompetencyScores(
                technical_skills=70.0,
                problem_solving=70.0,
                system_design=65.0,
                communication=70.0,
                leadership=60.0,
                domain_knowledge=65.0,
                learning_agility=70.0,
                collaboration=70.0
            ),
            technical_skills=TechnicalSkills(
                programming_languages={"primary": [], "secondary": []},
                proficiency_score=70.0,
                technical_depth_score=65.0,
                technical_breadth_score=65.0,
                specialization_area="general"
            ),
            experience_analysis=ExperienceAnalysis(
                experience_level=self._estimate_level_from_experience(candidate.experience_years),
                career_progression="steady",
                leadership_experience={"has_leadership": False, "team_size_managed": 0, "leadership_score": 50.0},
                project_complexity={"scale": "medium", "complexity_score": 65.0}
            )
        )
    
    def _estimate_level_from_experience(self, years: int) -> str:
        """Estimate experience level from years"""
        if years <= 2:
            return "junior"
        elif years <= 5:
            return "mid"
        elif years <= 9:
            return "senior"
        else:
            return "staff"
    
    async def _calculate_match_score(self,
                                   candidate: Candidate,
                                   candidate_analysis: CandidateAnalysis,
                                   interviewer_profile: InterviewerProfile,
                                   interview_date_range: Tuple[datetime, datetime],
                                   required_interview_type: InterviewType) -> Optional[MatchResult]:
        """Calculate comprehensive match score for interviewer"""
        
        # 1. Technical Skills Match (35% weight)
        technical_score = self._calculate_technical_match(
            candidate, candidate_analysis, interviewer_profile
        )
        
        # 2. Seniority Level Match (25% weight)
        seniority_score = self._calculate_seniority_match(
            candidate_analysis, interviewer_profile
        )
        
        # 3. Availability Score (20% weight)
        availability_score, available_slots = await self._calculate_availability_score(
            interviewer_profile, interview_date_range
        )
        
        # 4. Interview Type Match (15% weight)
        interview_type_score = self._calculate_interview_type_match(
            required_interview_type, interviewer_profile
        )
        
        # 5. Experience Match (5% weight)
        experience_score = self._calculate_experience_match(
            candidate, interviewer_profile
        )
        
        # Calculate overall score
        overall_score = (
            technical_score * self.weights['technical_match'] +
            seniority_score * self.weights['seniority_match'] +
            availability_score * self.weights['availability'] +
            interview_type_score * self.weights['interview_type'] +
            experience_score * self.weights['experience_match']
        ) * 100
        
        # Determine confidence level
        confidence = self._determine_confidence(overall_score)
        
        # Generate match reasons and concerns
        match_reasons, concerns = self._generate_match_explanation(
            technical_score, seniority_score, availability_score,
            interview_type_score, experience_score, interviewer_profile
        )
        
        # Find recommended time slot
        recommended_slot = self._find_recommended_slot(
            available_slots, interviewer_profile
        )
        
        return MatchResult(
            interviewer_profile=interviewer_profile,
            candidate=candidate,
            candidate_analysis=candidate_analysis,
            technical_match_score=technical_score * 100,
            seniority_match_score=seniority_score * 100,
            availability_score=availability_score * 100,
            interview_type_score=interview_type_score * 100,
            experience_match_score=experience_score * 100,
            overall_match_score=overall_score,
            confidence_level=confidence,
            available_slots=available_slots,
            recommended_slot=recommended_slot,
            match_reasons=match_reasons,
            potential_concerns=concerns,
            ai_model_used=self.ai_service.model_name if hasattr(self.ai_service, 'model_name') else "claude-3-haiku"
        )
    
    def _calculate_technical_match(self, 
                                 candidate: Candidate,
                                 candidate_analysis: CandidateAnalysis,
                                 interviewer_profile: InterviewerProfile) -> float:
        """Calculate technical skills match score (0-1)"""
        
        # Extract candidate skills
        candidate_skills = []
        
        # From candidate skills list
        if hasattr(candidate, 'skills') and candidate.skills:
            candidate_skills.extend([skill.name for skill in candidate.skills])
        
        # From AI analysis
        if candidate_analysis.technical_skills:
            tech_skills = candidate_analysis.technical_skills
            if tech_skills.programming_languages:
                candidate_skills.extend(tech_skills.programming_languages.get("primary", []))
                candidate_skills.extend(tech_skills.programming_languages.get("secondary", []))
        
        # Remove duplicates and normalize
        candidate_skills = list(set([skill.lower().strip() for skill in candidate_skills if skill]))
        
        if not candidate_skills:
            return 0.3  # Low score if no skills identified
        
        # Calculate interviewer expertise for candidate skills
        expertise_score = interviewer_profile.expertise_score_for_skills(candidate_skills)
        
        # Normalize to 0-1 range
        normalized_score = min(expertise_score / 100.0, 1.0)
        
        # Apply candidate technical strength multiplier
        if candidate_analysis.technical_score:
            candidate_strength = candidate_analysis.technical_score / 100.0
            # Blend interviewer expertise with candidate strength
            final_score = 0.7 * normalized_score + 0.3 * candidate_strength
        else:
            final_score = normalized_score
        
        return max(final_score, 0.0)
    
    def _calculate_seniority_match(self,
                                 candidate_analysis: CandidateAnalysis,
                                 interviewer_profile: InterviewerProfile) -> float:
        """Calculate seniority level match score (0-1)"""
        
        candidate_level = candidate_analysis.estimated_level.lower()
        interviewer_level = interviewer_profile.seniority_level.lower()
        
        # Seniority compatibility matrix
        compatibility = {
            "junior": {"junior": 0.6, "mid": 0.9, "senior": 1.0, "staff": 0.8, "principal": 0.7},
            "mid": {"junior": 0.7, "mid": 0.8, "senior": 1.0, "staff": 0.9, "principal": 0.8},
            "senior": {"junior": 0.5, "mid": 0.7, "senior": 0.9, "staff": 1.0, "principal": 1.0},
            "staff": {"junior": 0.4, "mid": 0.6, "senior": 0.8, "staff": 0.9, "principal": 1.0}
        }
        
        # Handle variations in level naming
        level_mapping = {
            "junior": "junior",
            "mid": "mid", 
            "middle": "mid",
            "senior": "senior",
            "staff": "staff",
            "principal": "principal",
            "lead": "senior"
        }
        
        candidate_mapped = level_mapping.get(candidate_level, "mid")
        interviewer_mapped = level_mapping.get(interviewer_level, "senior")
        
        return compatibility.get(candidate_mapped, {}).get(interviewer_mapped, 0.5)
    
    async def _calculate_availability_score(self,
                                          interviewer_profile: InterviewerProfile,
                                          date_range: Tuple[datetime, datetime]) -> Tuple[float, List[AvailabilitySlot]]:
        """Calculate availability score and return available slots"""
        
        start_date, end_date = date_range
        
        try:
            # Get interviewer's calendar availability
            calendar_events = await asyncio.to_thread(
                self.calendar_service.get_events,
                interviewer_profile.interviewer.email,
                start_date,
                end_date
            )
            
            # Generate potential time slots (working hours)
            potential_slots = self._generate_working_hour_slots(start_date, end_date)
            
            # Filter out conflicting slots
            available_slots = []
            for slot in potential_slots:
                is_available = True
                for event in calendar_events:
                    event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                    event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                    
                    if slot.start_time < event_end and slot.end_time > event_start:
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(slot)
            
            # Calculate score based on availability
            total_potential_slots = len(potential_slots)
            if total_potential_slots == 0:
                return 0.0, []
            
            availability_ratio = len(available_slots) / total_potential_slots
            
            # Bonus for having slots in preferred times
            preferred_slots = [slot for slot in available_slots if slot.is_preferred_time]
            preferred_bonus = min(len(preferred_slots) * 0.1, 0.3)
            
            final_score = min(availability_ratio + preferred_bonus, 1.0)
            
            return final_score, available_slots
            
        except Exception as e:
            logger.warning(f"Calendar check failed for {interviewer_profile.interviewer.email}: {e}")
            # Fallback: assume moderate availability
            return 0.6, self._generate_working_hour_slots(start_date, end_date)[:3]
    
    def _generate_working_hour_slots(self, 
                                   start_date: datetime, 
                                   end_date: datetime) -> List[AvailabilitySlot]:
        """Generate potential interview slots during working hours"""
        slots = []
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            # Skip weekends
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            
            # Generate hourly slots from 9 AM to 5 PM
            for hour in range(9, 17):
                slot_start = current.replace(hour=hour)
                slot_end = slot_start + timedelta(hours=1)
                
                if slot_end <= end_date:
                    # Mark 10 AM - 3 PM as preferred times
                    is_preferred = 10 <= hour <= 15
                    
                    slots.append(AvailabilitySlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        duration_minutes=60,
                        is_preferred_time=is_preferred
                    ))
            
            current += timedelta(days=1)
        
        return slots
    
    def _calculate_interview_type_match(self,
                                      required_type: InterviewType,
                                      interviewer_profile: InterviewerProfile) -> float:
        """Calculate interview type match score (0-1)"""
        
        if required_type in interviewer_profile.interview_types_preferred:
            return 1.0
        
        # Partial matches based on interviewer flexibility
        type_compatibility = {
            InterviewType.TECHNICAL: {
                InterviewType.SYSTEM_DESIGN: 0.8,
                InterviewType.BEHAVIORAL: 0.4,
                InterviewType.CULTURAL: 0.3
            },
            InterviewType.SYSTEM_DESIGN: {
                InterviewType.TECHNICAL: 0.9,
                InterviewType.BEHAVIORAL: 0.5,
                InterviewType.CULTURAL: 0.3
            },
            InterviewType.BEHAVIORAL: {
                InterviewType.CULTURAL: 0.8,
                InterviewType.TECHNICAL: 0.3,
                InterviewType.SYSTEM_DESIGN: 0.4
            },
            InterviewType.CULTURAL: {
                InterviewType.BEHAVIORAL: 0.9,
                InterviewType.TECHNICAL: 0.2,
                InterviewType.SYSTEM_DESIGN: 0.2
            }
        }
        
        best_compatibility = 0.0
        for preferred_type in interviewer_profile.interview_types_preferred:
            compatibility = type_compatibility.get(required_type, {}).get(preferred_type, 0.0)
            best_compatibility = max(best_compatibility, compatibility)
        
        return best_compatibility
    
    def _calculate_experience_match(self,
                                  candidate: Candidate,
                                  interviewer_profile: InterviewerProfile) -> float:
        """Calculate experience domain match score (0-1)"""
        
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated domain matching
        
        score = 0.5  # Base score
        
        # Bonus for interviewer experience
        if interviewer_profile.years_interviewing > 2:
            score += 0.2
        
        # Bonus for high success rate
        if interviewer_profile.success_rate > 0.8:
            score += 0.2
        
        # Bonus for good candidate feedback
        if interviewer_profile.candidate_feedback_score > 4.0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_confidence(self, overall_score: float) -> MatchConfidence:
        """Determine confidence level based on overall score"""
        if overall_score >= self.excellent_score:
            return MatchConfidence.EXCELLENT
        elif overall_score >= self.preferred_score:
            return MatchConfidence.GOOD
        elif overall_score >= 60.0:
            return MatchConfidence.FAIR
        elif overall_score >= self.min_acceptable_score:
            return MatchConfidence.POOR
        else:
            return MatchConfidence.INSUFFICIENT
    
    def _generate_match_explanation(self,
                                  technical_score: float,
                                  seniority_score: float,
                                  availability_score: float,
                                  interview_type_score: float,
                                  experience_score: float,
                                  interviewer_profile: InterviewerProfile) -> Tuple[List[str], List[str]]:
        """Generate human-readable match reasons and concerns"""
        
        reasons = []
        concerns = []
        
        # Technical match analysis
        if technical_score > 0.8:
            reasons.append(f"Strong technical expertise match ({technical_score*100:.0f}%)")
        elif technical_score < 0.5:
            concerns.append(f"Limited technical expertise overlap ({technical_score*100:.0f}%)")
        
        # Seniority analysis
        if seniority_score > 0.8:
            reasons.append(f"Excellent seniority level match ({seniority_score*100:.0f}%)")
        elif seniority_score < 0.6:
            concerns.append(f"Seniority level mismatch ({seniority_score*100:.0f}%)")
        
        # Availability analysis
        if availability_score > 0.7:
            reasons.append(f"Good availability ({availability_score*100:.0f}%)")
        elif availability_score < 0.3:
            concerns.append(f"Limited availability ({availability_score*100:.0f}%)")
        
        # Interview type analysis
        if interview_type_score > 0.8:
            reasons.append("Preferred interview type match")
        elif interview_type_score < 0.5:
            concerns.append("Interview type not in preferred areas")
        
        # Experience analysis
        if interviewer_profile.success_rate > 0.85:
            reasons.append(f"High interview success rate ({interviewer_profile.success_rate:.1%})")
        
        if interviewer_profile.candidate_feedback_score > 4.0:
            reasons.append(f"Excellent candidate feedback ({interviewer_profile.candidate_feedback_score:.1f}/5.0)")
        
        return reasons, concerns
    
    def _find_recommended_slot(self,
                             available_slots: List[AvailabilitySlot],
                             interviewer_profile: InterviewerProfile) -> Optional[AvailabilitySlot]:
        """Find the best recommended time slot"""
        
        if not available_slots:
            return None
        
        # Prefer slots during preferred times
        preferred_slots = [slot for slot in available_slots if slot.is_preferred_time]
        if preferred_slots:
            return preferred_slots[0]
        
        # Otherwise return first available
        return available_slots[0]
    
    def _apply_fallback_logic(self,
                            sorted_matches: List[MatchResult],
                            candidate_analysis: CandidateAnalysis,
                            required_interview_type: InterviewType) -> List[MatchResult]:
        """Apply fallback logic when no excellent matches exist"""
        
        if not sorted_matches:
            logger.warning("⚠️ No matches found - fallback to emergency protocol")
            return []
        
        excellent_matches = [m for m in sorted_matches if m.overall_match_score >= self.excellent_score]
        good_matches = [m for m in sorted_matches if m.overall_match_score >= self.preferred_score]
        acceptable_matches = [m for m in sorted_matches if m.overall_match_score >= self.min_acceptable_score]
        
        if excellent_matches:
            logger.info(f"✅ Found {len(excellent_matches)} excellent matches")
            return excellent_matches
        
        elif good_matches:
            logger.info(f"✅ Found {len(good_matches)} good matches")
            return good_matches
        
        elif acceptable_matches:
            logger.warning(f"⚠️ Only {len(acceptable_matches)} acceptable matches found")
            # Add fallback recommendations to concerns
            for match in acceptable_matches:
                match.potential_concerns.append("Consider additional screening or pairing with senior interviewer")
            return acceptable_matches
        
        else:
            logger.warning("⚠️ No acceptable matches found - returning best available with warnings")
            # Return top 3 matches with strong warnings
            fallback_matches = sorted_matches[:3]
            for match in fallback_matches:
                match.confidence_level = MatchConfidence.INSUFFICIENT
                match.potential_concerns.extend([
                    "Below recommended match threshold",
                    "Consider rescheduling or finding additional interviewers",
                    "Require additional oversight during interview"
                ])
            return fallback_matches


# Factory function to create sample interviewer profiles
def create_sample_interviewer_profiles() -> List[InterviewerProfile]:
    """Create sample interviewer profiles for testing"""
    
    profiles = []
    
    # Senior Full Stack Engineer
    profiles.append(InterviewerProfile(
        interviewer=Interviewer(
            name="Alice Johnson",
            email="alice.johnson@company.com",
            skills=["Python", "JavaScript", "React", "Django", "PostgreSQL"],
            experience_years=8,
            available_time_slots=[],
            interview_types=[InterviewType.TECHNICAL, InterviewType.SYSTEM_DESIGN]
        ),
        technical_expertise={
            "python": 95, "javascript": 90, "react": 85, "django": 90,
            "postgresql": 80, "aws": 75, "docker": 70, "typescript": 80
        },
        seniority_level="senior",
        interview_types_preferred=[InterviewType.TECHNICAL, InterviewType.SYSTEM_DESIGN],
        max_interviews_per_day=3,
        preferred_interview_duration=75,
        specialization_areas=["Full Stack Development", "System Architecture"],
        years_interviewing=5,
        success_rate=0.92,
        candidate_feedback_score=4.6
    ))
    
    # DevOps Specialist
    profiles.append(InterviewerProfile(
        interviewer=Interviewer(
            name="Bob Chen",
            email="bob.chen@company.com", 
            skills=["AWS", "Kubernetes", "Python", "Terraform", "Docker"],
            experience_years=6,
            available_time_slots=[],
            interview_types=[InterviewType.TECHNICAL, InterviewType.SYSTEM_DESIGN]
        ),
        technical_expertise={
            "aws": 95, "kubernetes": 90, "docker": 95, "terraform": 85,
            "python": 75, "linux": 90, "monitoring": 80, "ci/cd": 90
        },
        seniority_level="senior",
        interview_types_preferred=[InterviewType.TECHNICAL, InterviewType.SYSTEM_DESIGN],
        specialization_areas=["DevOps", "Cloud Infrastructure", "Site Reliability"],
        years_interviewing=4,
        success_rate=0.88,
        candidate_feedback_score=4.3
    ))
    
    # Frontend Specialist
    profiles.append(InterviewerProfile(
        interviewer=Interviewer(
            name="Carol Martinez",
            email="carol.martinez@company.com",
            skills=["JavaScript", "React", "Vue.js", "CSS", "TypeScript"],
            experience_years=5,
            available_time_slots=[],
            interview_types=[InterviewType.TECHNICAL, InterviewType.BEHAVIORAL]
        ),
        technical_expertise={
            "javascript": 90, "react": 95, "vue": 85, "css": 90,
            "typescript": 85, "html": 85, "webpack": 75, "testing": 80
        },
        seniority_level="mid",
        interview_types_preferred=[InterviewType.TECHNICAL, InterviewType.BEHAVIORAL],
        specialization_areas=["Frontend Development", "UI/UX"],
        years_interviewing=3,
        success_rate=0.85,
        candidate_feedback_score=4.4
    ))
    
    # Engineering Manager
    profiles.append(InterviewerProfile(
        interviewer=Interviewer(
            name="David Kim",
            email="david.kim@company.com",
            skills=["Team Leadership", "System Design", "Python", "Architecture"],
            experience_years=12,
            available_time_slots=[],
            interview_types=[InterviewType.BEHAVIORAL, InterviewType.SYSTEM_DESIGN]
        ),
        technical_expertise={
            "leadership": 95, "system_design": 90, "architecture": 85,
            "python": 80, "team_management": 95, "product_strategy": 85
        },
        seniority_level="staff",
        interview_types_preferred=[InterviewType.BEHAVIORAL, InterviewType.SYSTEM_DESIGN],
        specialization_areas=["Engineering Leadership", "Team Management", "System Architecture"],
        years_interviewing=8,
        success_rate=0.90,
        candidate_feedback_score=4.5
    ))
    
    return profiles


async def main():
    """Demo of the smart matching algorithm"""
    print("🤖 Smart Interviewer Matching Algorithm Demo")
    print("=" * 60)
    
    # Initialize services (mock for demo)
    ai_service = AIService()  # Assuming this exists
    calendar_service = GoogleCalendarService()  # Assuming this exists
    
    # Create matching algorithm
    matcher = SmartMatchingAlgorithm(ai_service, calendar_service)
    
    # Create sample data
    from ai_service import create_sample_candidate
    candidate = create_sample_candidate()
    interviewer_profiles = create_sample_interviewer_profiles()
    
    # Define interview parameters
    interview_start = datetime.now() + timedelta(days=1)
    interview_end = interview_start + timedelta(days=7)
    required_type = InterviewType.TECHNICAL
    
    print(f"🔍 Finding matches for: {candidate.name}")
    print(f"📅 Date range: {interview_start.strftime('%Y-%m-%d')} to {interview_end.strftime('%Y-%m-%d')}")
    print(f"🎯 Interview type: {required_type.value}")
    print()
    
    # Find matches
    try:
        matches = await matcher.find_best_matches(
            candidate=candidate,
            interviewer_profiles=interviewer_profiles,
            interview_date_range=(interview_start, interview_end),
            required_interview_type=required_type,
            max_results=3
        )
        
        # Display results
        print("📊 MATCH RESULTS")
        print("-" * 40)
        
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match.interviewer_profile.interviewer.name}")
            print(f"   Overall Score: {match.overall_match_score:.1f}/100")
            print(f"   Confidence: {match.confidence_level.value.upper()}")
            print(f"   Available Slots: {len(match.available_slots)}")
            
            print(f"   Score Breakdown:")
            print(f"     • Technical Match: {match.technical_match_score:.1f}/100")
            print(f"     • Seniority Match: {match.seniority_match_score:.1f}/100")
            print(f"     • Availability: {match.availability_score:.1f}/100")
            print(f"     • Interview Type: {match.interview_type_score:.1f}/100")
            
            if match.match_reasons:
                print(f"   ✅ Strengths: {'; '.join(match.match_reasons[:2])}")
            
            if match.potential_concerns:
                print(f"   ⚠️ Concerns: {'; '.join(match.potential_concerns[:2])}")
        
        print(f"\n✨ Found {len(matches)} suitable matches!")
        
    except Exception as e:
        print(f"❌ Error during matching: {e}")


if __name__ == "__main__":
    asyncio.run(main())
