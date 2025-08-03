"""
AI Integration Demo for Interview Scheduling System
Demonstrates how to use AI analysis for candidate evaluation and interviewer matching
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Import AI service components
from ai_service import (
    AIService, CandidateProfile, CandidateSkill, InterviewerProfile, 
    SkillLevel, InterviewType, create_sample_candidate, create_sample_interviewers
)
from ai_config import AIConfig, load_ai_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIInterviewScheduler:
    """
    Enhanced interview scheduler with AI-powered candidate analysis and interviewer matching
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize AI-enhanced interview scheduler
        
        Args:
            api_key: OpenRouter API key (or use OPENROUTER_API_KEY env var)
        """
        self.config = load_ai_config()
        self.ai_service = AIService(api_key=api_key, model=self.config["model"])
        
        # Sample data for demo
        self.interviewers = create_sample_interviewers()
        
        logger.info(f"🤖 AI Interview Scheduler initialized")
        logger.info(f"   Model: {self.ai_service.model}")
        logger.info(f"   Available Interviewers: {len(self.interviewers)}")
    
    def analyze_and_schedule_interview(
        self, 
        candidate_data: Dict,
        interview_type: str = "technical",
        auto_select_interviewer: bool = True
    ) -> Dict:
        """
        Complete AI-powered interview scheduling workflow
        
        Args:
            candidate_data: Dictionary with candidate information
            interview_type: Type of interview to conduct
            auto_select_interviewer: Whether to automatically select best interviewer
            
        Returns:
            Dictionary with complete scheduling results and AI insights
        """
        try:
            logger.info(f"🎯 Starting AI-powered interview scheduling for {candidate_data.get('name', 'Unknown')}")
            
            # Step 1: Create candidate profile
            candidate = self._create_candidate_profile(candidate_data)
            
            # Step 2: AI analysis of candidate
            logger.info("🔍 Step 1: Analyzing candidate with AI...")
            analysis = self.ai_service.analyze_candidate(candidate)
            
            if not analysis:
                return {
                    "success": False,
                    "error": "Failed to analyze candidate",
                    "candidate": candidate_data
                }
            
            # Step 3: Find best interviewer matches
            logger.info("🎯 Step 2: Finding optimal interviewer matches...")
            matches = self.ai_service.match_interviewer(
                candidate, analysis, self.interviewers, InterviewType(interview_type)
            )
            
            if not matches:
                return {
                    "success": False,
                    "error": "No suitable interviewers found",
                    "candidate": candidate_data,
                    "analysis": analysis.to_dict()
                }
            
            # Step 4: Generate interview questions
            best_match = matches[0]
            best_interviewer = next(
                (i for i in self.interviewers if i.email == best_match.interviewer_email),
                self.interviewers[0]
            )
            
            logger.info("📝 Step 3: Generating customized interview questions...")
            questions = self.ai_service.generate_interview_questions(
                candidate, best_interviewer, InterviewType(interview_type), analysis
            )
            
            # Step 5: Compile comprehensive results
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "candidate": {
                    "name": candidate.name,
                    "email": candidate.email,
                    "position": candidate.position,
                    "experience_years": candidate.experience_years,
                    "key_skills": [skill.name for skill in candidate.skills[:5]]
                },
                "ai_analysis": {
                    "overall_score": analysis.overall_score,
                    "technical_score": analysis.technical_score,
                    "experience_score": analysis.experience_score,
                    "skill_match_score": analysis.skill_match_score,
                    "estimated_level": analysis.estimated_level,
                    "strengths": analysis.strengths,
                    "weaknesses": analysis.weaknesses,
                    "skill_gaps": analysis.skill_gaps,
                    "recommendations": analysis.recommendations,
                    "red_flags": analysis.red_flags,
                    "next_steps": analysis.next_steps,
                    "confidence_score": analysis.confidence_score
                },
                "interviewer_matches": [
                    {
                        "rank": i + 1,
                        "name": match.interviewer_name,
                        "email": match.interviewer_email,
                        "match_score": match.match_score,
                        "expertise_match": match.expertise_match,
                        "matching_skills": match.matching_skills,
                        "why_matched": match.why_matched,
                        "potential_concerns": match.potential_concerns,
                        "interview_focus_areas": match.interview_focus_areas,
                        "estimated_duration": match.estimated_duration
                    }
                    for i, match in enumerate(matches[:3])  # Top 3 matches
                ],
                "selected_interviewer": {
                    "name": best_match.interviewer_name,
                    "email": best_match.interviewer_email,
                    "match_score": best_match.match_score,
                    "rationale": best_match.why_matched
                } if auto_select_interviewer else None,
                "interview_plan": {
                    "type": interview_type,
                    "estimated_duration": questions.get("estimated_duration", 60) if questions else 60,
                    "difficulty_level": questions.get("difficulty_level", "medium") if questions else "medium",
                    "focus_areas": best_match.interview_focus_areas,
                    "questions_generated": len(questions.get("questions", [])) if questions else 0,
                    "preparation_notes": questions.get("preparation_notes", []) if questions else []
                },
                "questions": questions.get("questions", []) if questions else [],
                "ai_model_used": self.ai_service.model,
                "cost_estimate": self._estimate_cost(candidate_data, len(matches))
            }
            
            logger.info(f"✅ AI interview scheduling completed successfully!")
            logger.info(f"   Candidate Score: {analysis.overall_score}/100")
            logger.info(f"   Best Interviewer: {best_match.interviewer_name} (Score: {best_match.match_score}/100)")
            logger.info(f"   Questions Generated: {len(questions.get('questions', []))}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in AI interview scheduling: {e}")
            return {
                "success": False,
                "error": str(e),
                "candidate": candidate_data
            }
    
    def _create_candidate_profile(self, candidate_data: Dict) -> CandidateProfile:
        """Convert dictionary to CandidateProfile object"""
        # Convert skills if they're in dict format
        skills = []
        for skill_data in candidate_data.get("skills", []):
            if isinstance(skill_data, dict):
                skills.append(CandidateSkill(
                    name=skill_data.get("name", ""),
                    level=SkillLevel(skill_data.get("level", "intermediate")),
                    years_experience=skill_data.get("years_experience", 0),
                    projects_count=skill_data.get("projects_count", 0),
                    certifications=skill_data.get("certifications", [])
                ))
            else:
                # Handle simple string skills
                skills.append(CandidateSkill(
                    name=str(skill_data),
                    level=SkillLevel.INTERMEDIATE,
                    years_experience=candidate_data.get("experience_years", 0) / 2,
                    projects_count=1
                ))
        
        return CandidateProfile(
            name=candidate_data.get("name", ""),
            email=candidate_data.get("email", ""),
            position=candidate_data.get("position", ""),
            experience_years=candidate_data.get("experience_years", 0),
            skills=skills,
            education=candidate_data.get("education", ""),
            previous_companies=candidate_data.get("previous_companies", []),
            github_url=candidate_data.get("github_url", ""),
            linkedin_url=candidate_data.get("linkedin_url", ""),
            portfolio_url=candidate_data.get("portfolio_url", ""),
            cover_letter=candidate_data.get("cover_letter", ""),
            resume_text=candidate_data.get("resume_text", ""),
            preferred_salary=candidate_data.get("preferred_salary", 0.0),
            availability=candidate_data.get("availability", "")
        )
    
    def _estimate_cost(self, candidate_data: Dict, num_interviewers: int) -> Dict:
        """Estimate AI API cost for the analysis"""
        # Rough token estimation
        candidate_tokens = len(str(candidate_data)) * 0.75  # Estimate based on text length
        analysis_tokens = 1000  # Typical response size
        matching_tokens = num_interviewers * 200  # Per interviewer analysis
        question_tokens = 800  # Question generation
        
        total_tokens = candidate_tokens + analysis_tokens + matching_tokens + question_tokens
        
        cost = AIConfig.get_cost_estimate(self.ai_service.model, total_tokens)
        
        return {
            "estimated_tokens": int(total_tokens),
            "estimated_cost_usd": round(cost, 6),
            "model": self.ai_service.model
        }
    
    def batch_analyze_candidates(self, candidates_data: List[Dict]) -> List[Dict]:
        """
        Analyze multiple candidates in batch
        
        Args:
            candidates_data: List of candidate dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        total_cost = 0
        
        logger.info(f"🔄 Starting batch analysis of {len(candidates_data)} candidates")
        
        for i, candidate_data in enumerate(candidates_data):
            logger.info(f"   Processing candidate {i+1}/{len(candidates_data)}: {candidate_data.get('name', 'Unknown')}")
            
            result = self.analyze_and_schedule_interview(candidate_data)
            results.append(result)
            
            if result.get("success"):
                total_cost += result.get("cost_estimate", {}).get("estimated_cost_usd", 0)
        
        logger.info(f"✅ Batch analysis completed")
        logger.info(f"   Total estimated cost: ${total_cost:.6f}")
        logger.info(f"   Successful analyses: {sum(1 for r in results if r.get('success'))}/{len(results)}")
        
        return results
    
    def get_interviewer_workload(self) -> Dict:
        """Get current interviewer workload analysis"""
        workload = {}
        
        for interviewer in self.interviewers:
            # Calculate success rate
            success_rate = (interviewer.successful_hires / max(interviewer.total_interviews, 1)) * 100
            
            workload[interviewer.email] = {
                "name": interviewer.name,
                "department": interviewer.department,
                "seniority": interviewer.seniority_level,
                "expertise_areas": interviewer.expertise_areas,
                "interview_types": [t.value for t in interviewer.interview_types],
                "rating": interviewer.rating,
                "total_interviews": interviewer.total_interviews,
                "successful_hires": interviewer.successful_hires,
                "success_rate": round(success_rate, 1),
                "max_weekly_capacity": interviewer.max_interviews_per_week,
                "preferred_technologies": interviewer.preferred_technologies
            }
        
        return workload

def create_sample_candidates() -> List[Dict]:
    """Create sample candidate data for testing"""
    return [
        {
            "name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "position": "Senior Python Developer",
            "experience_years": 6.0,
            "skills": [
                {"name": "Python", "level": "advanced", "years_experience": 6.0, "projects_count": 12},
                {"name": "Django", "level": "advanced", "years_experience": 5.0, "projects_count": 8},
                {"name": "React", "level": "intermediate", "years_experience": 3.0, "projects_count": 5},
                {"name": "PostgreSQL", "level": "advanced", "years_experience": 5.5, "projects_count": 10},
                {"name": "AWS", "level": "intermediate", "years_experience": 3.5, "projects_count": 6}
            ],
            "education": "MS Computer Science",
            "previous_companies": ["TechStartup", "BigCorp", "FinTech Inc"],
            "github_url": "https://github.com/alicejohnson",
            "linkedin_url": "https://linkedin.com/in/alicejohnson",
            "cover_letter": "Experienced Python developer with strong background in web applications and cloud deployment. Passionate about clean code and scalable architecture.",
            "resume_text": "Senior Python Developer with 6+ years experience building web applications using Django, React, and cloud technologies. Led multiple projects from conception to production deployment.",
            "preferred_salary": 130000.0,
            "availability": "Available in 2 weeks"
        },
        {
            "name": "Bob Chen",
            "email": "bob.chen@email.com", 
            "position": "Frontend Developer",
            "experience_years": 4.0,
            "skills": [
                {"name": "React", "level": "expert", "years_experience": 4.0, "projects_count": 15},
                {"name": "JavaScript", "level": "advanced", "years_experience": 4.5, "projects_count": 20},
                {"name": "TypeScript", "level": "advanced", "years_experience": 3.0, "projects_count": 12},
                {"name": "CSS", "level": "advanced", "years_experience": 4.0, "projects_count": 18},
                {"name": "Node.js", "level": "intermediate", "years_experience": 2.5, "projects_count": 6}
            ],
            "education": "BS Computer Engineering",
            "previous_companies": ["WebDesign Co", "E-commerce Startup"],
            "github_url": "https://github.com/bobchen",
            "portfolio_url": "https://bobchen.dev",
            "cover_letter": "Frontend specialist with deep React expertise and passion for user experience. Built responsive applications for various industries.",
            "resume_text": "Frontend Developer specializing in React ecosystem with 4 years of experience. Strong focus on performance optimization and modern development practices.",
            "preferred_salary": 95000.0,
            "availability": "Available immediately"
        },
        {
            "name": "Carol Martinez",
            "email": "carol.martinez@email.com",
            "position": "Full Stack Developer",
            "experience_years": 3.5,
            "skills": [
                {"name": "Python", "level": "intermediate", "years_experience": 3.5, "projects_count": 8},
                {"name": "JavaScript", "level": "intermediate", "years_experience": 3.5, "projects_count": 10},
                {"name": "React", "level": "intermediate", "years_experience": 2.5, "projects_count": 5},
                {"name": "Flask", "level": "intermediate", "years_experience": 3.0, "projects_count": 6},
                {"name": "MongoDB", "level": "intermediate", "years_experience": 2.0, "projects_count": 4}
            ],
            "education": "BS Information Technology",
            "previous_companies": ["Local Agency", "SaaS Startup"],
            "github_url": "https://github.com/carolmartinez",
            "cover_letter": "Full stack developer with balanced experience in frontend and backend technologies. Eager to grow and contribute to challenging projects.",
            "resume_text": "Full Stack Developer with 3.5 years experience in Python/JavaScript stack. Built complete web applications from database design to user interface.",
            "preferred_salary": 85000.0,
            "availability": "Available in 1 month"
        }
    ]

def run_demo():
    """Run the AI integration demo"""
    print("🤖 AI Integration Demo - Interview Scheduling System")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        print("   Get your key from: https://openrouter.ai/keys")
        print("\n   For demo purposes, you can set a placeholder:")
        print("   export OPENROUTER_API_KEY='your-key-here'")
        return
    
    try:
        # Initialize AI scheduler
        scheduler = AIInterviewScheduler(api_key=api_key)
        
        # Display model information
        model_info = scheduler.ai_service.get_model_info()
        print(f"\n🔧 AI Configuration:")
        print(f"   Model: {model_info['model']}")
        print(f"   Cost per 1K tokens: ${model_info['cost_per_1k_tokens']}")
        print(f"   Max tokens: {model_info['max_tokens']}")
        
        # Get sample candidates
        sample_candidates = create_sample_candidates()
        print(f"\n📊 Sample Candidates: {len(sample_candidates)}")
        for i, candidate in enumerate(sample_candidates):
            print(f"   {i+1}. {candidate['name']} - {candidate['position']} ({candidate['experience_years']} years)")
        
        # Demo 1: Single candidate analysis
        print(f"\n🎯 Demo 1: Single Candidate Analysis")
        print("-" * 40)
        
        candidate = sample_candidates[0]  # Alice Johnson
        result = scheduler.analyze_and_schedule_interview(candidate, "technical")
        
        if result["success"]:
            analysis = result["ai_analysis"]
            print(f"✅ Analysis completed for {result['candidate']['name']}")
            print(f"   Overall Score: {analysis['overall_score']}/100")
            print(f"   Technical Score: {analysis['technical_score']}/100")
            print(f"   Estimated Level: {analysis['estimated_level']}")
            print(f"   Key Strengths: {', '.join(analysis['strengths'][:3])}")
            
            # Show interviewer matching
            matches = result["interviewer_matches"]
            print(f"\n   Top Interviewer Matches:")
            for match in matches[:2]:
                print(f"   {match['rank']}. {match['name']} - Score: {match['match_score']}/100")
                print(f"      Matching Skills: {', '.join(match['matching_skills'][:3])}")
            
            # Show questions
            questions = result["questions"]
            if questions:
                print(f"\n   Generated Questions: {len(questions)}")
                for i, q in enumerate(questions[:2]):
                    print(f"   {i+1}. [{q['category']}] {q['question'][:80]}...")
            
            # Show cost
            cost = result["cost_estimate"]
            print(f"\n   💰 Cost: ${cost['estimated_cost_usd']:.6f} ({cost['estimated_tokens']} tokens)")
        
        # Demo 2: Batch analysis
        print(f"\n🔄 Demo 2: Batch Candidate Analysis")
        print("-" * 40)
        
        print(f"Processing {len(sample_candidates)} candidates...")
        batch_results = scheduler.batch_analyze_candidates(sample_candidates)
        
        successful_results = [r for r in batch_results if r.get("success")]
        print(f"\n✅ Batch Analysis Results:")
        print(f"   Successful: {len(successful_results)}/{len(batch_results)}")
        
        if successful_results:
            # Show summary
            avg_score = sum(r["ai_analysis"]["overall_score"] for r in successful_results) / len(successful_results)
            total_cost = sum(r["cost_estimate"]["estimated_cost_usd"] for r in successful_results)
            
            print(f"   Average Score: {avg_score:.1f}/100")
            print(f"   Total Cost: ${total_cost:.6f}")
            
            # Show rankings
            ranked_candidates = sorted(
                successful_results, 
                key=lambda x: x["ai_analysis"]["overall_score"], 
                reverse=True
            )
            
            print(f"\n   📈 Candidate Rankings:")
            for i, result in enumerate(ranked_candidates):
                candidate = result["candidate"]
                analysis = result["ai_analysis"]
                print(f"   {i+1}. {candidate['name']} - {analysis['overall_score']}/100 ({analysis['estimated_level']})")
        
        # Demo 3: Interviewer workload
        print(f"\n👥 Demo 3: Interviewer Workload Analysis")
        print("-" * 40)
        
        workload = scheduler.get_interviewer_workload()
        for email, info in workload.items():
            print(f"\n{info['name']} ({info['department']}):")
            print(f"   Expertise: {', '.join(info['expertise_areas'][:3])}")
            print(f"   Rating: {info['rating']}/5.0")
            print(f"   Success Rate: {info['success_rate']}%")
            print(f"   Capacity: {info['max_weekly_capacity']} interviews/week")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\nNext steps:")
        print(f"   1. Integrate AI analysis into your interview scheduling API")
        print(f"   2. Set up proper cost monitoring and limits")
        print(f"   3. Customize interviewer profiles based on your team")
        print(f"   4. Add AI insights to your interview database")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo error details:")

if __name__ == "__main__":
    run_demo()
