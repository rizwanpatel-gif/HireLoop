"""
Smart Matching Algorithm Demo
============================

Comprehensive demonstration of the intelligent interviewer matching system
combining AI analysis, calendar availability, and confidence scoring.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List

# Set up environment for demo
os.environ.setdefault('OPENROUTER_API_KEY', 'demo_key_replace_with_real')

from smart_matching_algorithm import (
    SmartMatchingAlgorithm, 
    InterviewerProfile, 
    MatchConfidence,
    create_sample_interviewer_profiles
)
from ai_service import AIService, create_sample_candidate, InterviewType
from google_calendar_service import GoogleCalendarService


class MockCalendarService:
    """Mock calendar service for demo purposes"""
    
    def get_events(self, email: str, start_date: datetime, end_date: datetime):
        """Return mock calendar events"""
        # Simulate some busy times
        events = []
        
        # Alice has meetings on Tuesday morning
        if "alice" in email.lower():
            tuesday = start_date + timedelta(days=1)
            events.append({
                'start': {'dateTime': tuesday.replace(hour=9).isoformat()},
                'end': {'dateTime': tuesday.replace(hour=11).isoformat()},
                'summary': 'Team Meeting'
            })
        
        # Bob has meetings on Wednesday afternoon
        elif "bob" in email.lower():
            wednesday = start_date + timedelta(days=2) 
            events.append({
                'start': {'dateTime': wednesday.replace(hour=14).isoformat()},
                'end': {'dateTime': wednesday.replace(hour=16).isoformat()},
                'summary': 'Infrastructure Review'
            })
        
        return events


async def run_comprehensive_demo():
    """Run comprehensive smart matching demo"""
    
    print("🤖 Smart Interviewer Matching Algorithm - Comprehensive Demo")
    print("=" * 70)
    print("Features:")
    print("• AI-powered candidate analysis with technical skill assessment")
    print("• Intelligent interviewer matching based on expertise overlap")
    print("• Real-time calendar availability checking")
    print("• Confidence scoring with fallback logic")
    print("• Comprehensive match explanations and recommendations")
    print("=" * 70)
    
    # Initialize services
    print("🔧 Initializing services...")
    ai_service = AIService()
    calendar_service = MockCalendarService()  # Using mock for demo
    
    # Create smart matching algorithm
    matcher = SmartMatchingAlgorithm(ai_service, calendar_service)
    
    print("✅ Services initialized")
    print(f"   AI Model: {getattr(ai_service, 'model_name', 'claude-3-haiku')}")
    print(f"   Calendar: Mock service (simulating Google Calendar)")
    print()
    
    # Create test scenarios
    test_scenarios = await create_test_scenarios()
    
    # Run each scenario
    for scenario_num, scenario in enumerate(test_scenarios, 1):
        await run_scenario(matcher, scenario_num, scenario)
        print()
    
    print("📊 DEMO SUMMARY")
    print("=" * 50)
    print("✅ Smart matching algorithm successfully demonstrated:")
    print("   • Technical expertise matching with confidence scoring")
    print("   • Calendar availability integration")
    print("   • Multi-dimensional scoring (technical, seniority, availability)")
    print("   • Intelligent fallback logic for edge cases")
    print("   • Detailed match explanations and recommendations")
    print()
    print("🚀 Next steps:")
    print("   • Integrate with real Google Calendar API")
    print("   • Add more sophisticated domain matching")
    print("   • Implement machine learning for improved accuracy")
    print("   • Add batch processing for multiple candidates")


async def create_test_scenarios():
    """Create different test scenarios"""
    
    scenarios = []
    
    # Scenario 1: Senior Python Developer
    scenarios.append({
        'name': 'Senior Python Backend Developer',
        'candidate': create_sample_candidate(),  # Default senior Python dev
        'interview_type': InterviewType.TECHNICAL,
        'description': 'Experienced backend developer with Python/Django expertise'
    })
    
    # Scenario 2: DevOps Engineer  
    from ai_service import Candidate, Skill
    devops_candidate = Candidate(
        name="Michael Rodriguez",
        email="michael.r@email.com",
        position="DevOps Engineer",
        experience_years=4,
        skills=[
            Skill(name="AWS", level="advanced", years_experience=3, projects_count=8),
            Skill(name="Kubernetes", level="intermediate", years_experience=2, projects_count=5),
            Skill(name="Docker", level="advanced", years_experience=4, projects_count=12),
            Skill(name="Python", level="intermediate", years_experience=3, projects_count=6),
            Skill(name="Terraform", level="intermediate", years_experience=2, projects_count=4),
        ],
        resume_text="""
        DevOps Engineer with 4 years of experience in cloud infrastructure and automation.
        
        Experience:
        • Netflix (2022-2024) - Senior DevOps Engineer
          - Managed Kubernetes clusters serving 200M+ users
          - Implemented CI/CD pipelines reducing deployment time by 60%
          - Led migration of 50+ microservices to containerized architecture
        
        • Uber (2020-2022) - DevOps Engineer
          - Automated infrastructure provisioning using Terraform
          - Maintained 99.9% uptime for critical payment systems
          - Implemented monitoring and alerting for 100+ services
        
        Technical Skills:
        • Cloud: AWS (EC2, S3, RDS, Lambda), GCP
        • Containers: Docker, Kubernetes, Helm
        • Infrastructure as Code: Terraform, CloudFormation
        • CI/CD: Jenkins, GitLab CI, GitHub Actions
        • Monitoring: Prometheus, Grafana, ELK Stack
        • Languages: Python, Bash, Go
        """
    )
    
    scenarios.append({
        'name': 'DevOps Engineer',
        'candidate': devops_candidate,
        'interview_type': InterviewType.SYSTEM_DESIGN,
        'description': 'Mid-level DevOps engineer with strong AWS/Kubernetes background'
    })
    
    # Scenario 3: Junior Frontend Developer
    junior_candidate = Candidate(
        name="Emily Johnson", 
        email="emily.j@email.com",
        position="Junior Frontend Developer",
        experience_years=1,
        skills=[
            Skill(name="JavaScript", level="intermediate", years_experience=1, projects_count=3),
            Skill(name="React", level="beginner", years_experience=1, projects_count=2),
            Skill(name="CSS", level="intermediate", years_experience=2, projects_count=4),
            Skill(name="HTML", level="advanced", years_experience=2, projects_count=5),
        ],
        resume_text="""
        Junior Frontend Developer with 1.5 years of experience, recently graduated from coding bootcamp.
        
        Experience:
        • TechStartup (2023-2024) - Junior Frontend Developer
          - Built responsive web applications using React and CSS
          - Collaborated with design team to implement pixel-perfect UIs
          - Contributed to component library used across 5+ projects
        
        Education:
        • Coding Bootcamp Graduate (2023) - Full Stack Web Development
        • Bachelor's Degree in Graphic Design (2021)
        
        Projects:
        • E-commerce Platform - React, Redux, styled-components
        • Personal Portfolio - HTML, CSS, JavaScript
        • Task Management App - React, Local Storage API
        
        Technical Skills:
        • Frontend: JavaScript, React, HTML5, CSS3
        • Tools: Git, VS Code, Figma
        • Learning: TypeScript, Node.js, Testing
        """
    )
    
    scenarios.append({
        'name': 'Junior Frontend Developer',
        'candidate': junior_candidate,
        'interview_type': InterviewType.TECHNICAL,
        'description': 'Entry-level frontend developer from bootcamp background'
    })
    
    return scenarios


async def run_scenario(matcher: SmartMatchingAlgorithm, scenario_num: int, scenario: dict):
    """Run a single matching scenario"""
    
    print(f"📋 SCENARIO {scenario_num}: {scenario['name']}")
    print("-" * 50)
    print(f"📝 Description: {scenario['description']}")
    print(f"🎯 Interview Type: {scenario['interview_type'].value}")
    print(f"👤 Candidate: {scenario['candidate'].name}")
    print(f"💼 Position: {scenario['candidate'].position}")
    print(f"📅 Experience: {scenario['candidate'].experience_years} years")
    
    # Show candidate skills
    if hasattr(scenario['candidate'], 'skills') and scenario['candidate'].skills:
        skills_list = [f"{skill.name} ({skill.level})" for skill in scenario['candidate'].skills[:4]]
        print(f"🛠️ Key Skills: {', '.join(skills_list)}")
    
    print()
    
    # Get interviewer profiles
    interviewer_profiles = create_sample_interviewer_profiles()
    
    # Define interview date range (next week)
    interview_start = datetime.now() + timedelta(days=1)
    interview_end = interview_start + timedelta(days=7)
    
    print("🔍 Running intelligent matching algorithm...")
    print(f"   Analyzing candidate technical profile...")
    print(f"   Checking {len(interviewer_profiles)} available interviewers...")
    print(f"   Verifying calendar availability...")
    print(f"   Calculating multi-dimensional match scores...")
    
    try:
        # Find matches
        matches = await matcher.find_best_matches(
            candidate=scenario['candidate'],
            interviewer_profiles=interviewer_profiles,
            interview_date_range=(interview_start, interview_end),
            required_interview_type=scenario['interview_type'],
            max_results=3
        )
        
        print("✅ Analysis complete!")
        print()
        
        # Display detailed results
        print("📊 MATCH RESULTS")
        print("-" * 30)
        
        if not matches:
            print("❌ No suitable matches found")
            return
        
        for i, match in enumerate(matches, 1):
            interviewer = match.interviewer_profile.interviewer
            profile = match.interviewer_profile
            
            print(f"\n🏆 MATCH #{i}: {interviewer.name}")
            print(f"   📧 Email: {interviewer.email}")
            print(f"   🎖️ Seniority: {profile.seniority_level.title()}")
            print(f"   📊 Overall Score: {match.overall_match_score:.1f}/100")
            print(f"   🎯 Confidence: {match.confidence_level.value.upper()}")
            
            # Confidence indicator
            confidence_emoji = {
                MatchConfidence.EXCELLENT: "🟢",
                MatchConfidence.GOOD: "🟡", 
                MatchConfidence.FAIR: "🟠",
                MatchConfidence.POOR: "🔴",
                MatchConfidence.INSUFFICIENT: "⚫"
            }
            print(f"   {confidence_emoji.get(match.confidence_level, '⚪')} Confidence Level")
            
            # Detailed score breakdown
            print(f"\n   📈 SCORE BREAKDOWN:")
            print(f"      Technical Match:    {match.technical_match_score:5.1f}/100")
            print(f"      Seniority Match:    {match.seniority_match_score:5.1f}/100") 
            print(f"      Availability:       {match.availability_score:5.1f}/100")
            print(f"      Interview Type:     {match.interview_type_score:5.1f}/100")
            print(f"      Experience Match:   {match.experience_match_score:5.1f}/100")
            
            # Availability details
            print(f"\n   📅 AVAILABILITY:")
            print(f"      Available Slots:    {len(match.available_slots)}")
            if match.recommended_slot:
                rec_time = match.recommended_slot.start_time
                print(f"      Recommended Time:   {rec_time.strftime('%A, %B %d at %I:%M %p')}")
                if match.recommended_slot.is_preferred_time:
                    print(f"      ⭐ Preferred time slot")
            
            # Match strengths
            if match.match_reasons:
                print(f"\n   ✅ STRENGTHS:")
                for reason in match.match_reasons[:3]:
                    print(f"      • {reason}")
            
            # Potential concerns
            if match.potential_concerns:
                print(f"\n   ⚠️ CONSIDERATIONS:")
                for concern in match.potential_concerns[:2]:
                    print(f"      • {concern}")
            
            # Interviewer expertise
            print(f"\n   🛠️ INTERVIEWER EXPERTISE:")
            top_skills = sorted(profile.technical_expertise.items(), 
                              key=lambda x: x[1], reverse=True)[:4]
            for skill, score in top_skills:
                print(f"      • {skill.title()}: {score}/100")
            
            print(f"\n   📊 INTERVIEWER STATS:")
            print(f"      Success Rate:       {profile.success_rate:.1%}")
            print(f"      Candidate Feedback: {profile.candidate_feedback_score:.1f}/5.0")
            print(f"      Years Interviewing: {profile.years_interviewing}")
        
        # Summary recommendations
        best_match = matches[0]
        print(f"\n🎯 RECOMMENDATION:")
        
        if best_match.confidence_level == MatchConfidence.EXCELLENT:
            print("   ✅ PROCEED with top match - Excellent fit!")
        elif best_match.confidence_level == MatchConfidence.GOOD:
            print("   ✅ PROCEED with top match - Good fit with minor considerations")
        elif best_match.confidence_level == MatchConfidence.FAIR:
            print("   ⚠️ PROCEED with caution - Consider additional preparation")
        else:
            print("   ❌ RECONSIDER - May need to find additional interviewers")
        
        print(f"   Recommended Interviewer: {best_match.interviewer_profile.interviewer.name}")
        if best_match.recommended_slot:
            print(f"   Suggested Time: {best_match.recommended_slot.start_time.strftime('%A, %B %d at %I:%M %p')}")
        
        # Cost estimation
        estimated_cost = 0.003  # Approximate cost per analysis
        print(f"\n💰 ANALYSIS COST: ~${estimated_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Error during matching: {e}")
        print("   This could be due to:")
        print("   • Missing OpenRouter API key")
        print("   • Network connectivity issues") 
        print("   • Service configuration problems")


if __name__ == "__main__":
    print("🚀 Starting Smart Matching Algorithm Demo...")
    print("   Note: This demo uses mock data and services")
    print("   Set OPENROUTER_API_KEY environment variable for real AI analysis")
    print()
    
    asyncio.run(run_comprehensive_demo())
