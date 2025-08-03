"""
Enhanced Candidate Analysis Demo
Demonstrates the improved AI-powered candidate evaluation with detailed scoring and interview strategy
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Import enhanced AI service components
from ai_service import (
    AIService, CandidateProfile, CandidateSkill, SkillLevel
)
from ai_config import load_ai_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_detailed_candidate_samples() -> list[Dict[str, Any]]:
    """Create realistic candidate profiles with detailed resume content for testing"""
    return [
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@email.com",
            "position": "Senior Full Stack Developer",
            "experience_years": 6.5,
            "skills": [
                {"name": "Python", "level": "expert", "years_experience": 6.0, "projects_count": 15},
                {"name": "React", "level": "advanced", "years_experience": 4.5, "projects_count": 12},
                {"name": "Node.js", "level": "advanced", "years_experience": 5.0, "projects_count": 10},
                {"name": "PostgreSQL", "level": "advanced", "years_experience": 5.5, "projects_count": 8},
                {"name": "AWS", "level": "intermediate", "years_experience": 3.0, "projects_count": 6},
                {"name": "Docker", "level": "intermediate", "years_experience": 2.5, "projects_count": 7}
            ],
            "education": "MS Computer Science, Stanford University",
            "previous_companies": ["Meta", "Spotify", "Airbnb"],
            "github_url": "https://github.com/sarahchen",
            "linkedin_url": "https://linkedin.com/in/sarahchen-dev",
            "cover_letter": "I'm a passionate full-stack developer with 6+ years of experience building scalable web applications. At Meta, I led the development of a real-time messaging system serving 50M+ users. I'm particularly interested in performance optimization and have reduced application load times by 40% through strategic caching and database optimization.",
            "resume_text": """
SARAH CHEN - Senior Full Stack Developer
Email: sarah.chen@email.com | LinkedIn: linkedin.com/in/sarahchen-dev | GitHub: github.com/sarahchen

EXPERIENCE
Senior Software Engineer | Meta (Facebook) | 2021-2024
• Led development of real-time messaging platform serving 50M+ daily active users
• Implemented WebSocket architecture with Redis clustering, reducing latency by 35%
• Mentored 3 junior developers and conducted technical interviews for 20+ candidates
• Built microservices using Python/Django and deployed on AWS EKS
• Collaborated with product team to define technical requirements for new features

Software Engineer | Spotify | 2019-2021
• Developed music recommendation algorithms using Python and machine learning
• Built React-based admin dashboard for content management, used by 200+ internal users
• Optimized database queries reducing API response time from 800ms to 120ms
• Implemented A/B testing framework that increased user engagement by 15%
• Technologies: Python, React, PostgreSQL, Redis, Kubernetes

Full Stack Developer | Airbnb | 2018-2019
• Built booking management system handling 10K+ transactions daily
• Developed responsive frontend using React and TypeScript
• Created RESTful APIs with Node.js and Express, serving 1M+ requests/day
• Implemented payment processing integration with Stripe and PayPal
• Set up CI/CD pipelines using Jenkins and Docker

TECHNICAL SKILLS
Languages: Python (Expert), JavaScript/TypeScript (Advanced), SQL (Advanced)
Frameworks: Django, React, Node.js, Express, Flask
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS (EC2, S3, RDS, Lambda), Kubernetes, Docker
Tools: Git, Jenkins, Jira, Datadog

EDUCATION
Master of Science in Computer Science | Stanford University | 2016-2018
Bachelor of Science in Software Engineering | UC Berkeley | 2012-2016

ACHIEVEMENTS
• Led team that won company hackathon for innovative caching solution
• Speaker at PyCon 2023: "Building Scalable Real-time Systems"
• Open source contributor to Django and React projects (500+ GitHub stars)
            """,
            "preferred_salary": 165000.0,
            "availability": "Available in 2 weeks with 2-week notice period"
        },
        {
            "name": "Michael Rodriguez",
            "email": "michael.rodriguez@email.com",
            "position": "DevOps Engineer",
            "experience_years": 4.0,
            "skills": [
                {"name": "Kubernetes", "level": "advanced", "years_experience": 3.5, "projects_count": 10},
                {"name": "AWS", "level": "expert", "years_experience": 4.0, "projects_count": 15},
                {"name": "Terraform", "level": "advanced", "years_experience": 3.0, "projects_count": 8},
                {"name": "Python", "level": "intermediate", "years_experience": 4.0, "projects_count": 6},
                {"name": "Docker", "level": "expert", "years_experience": 4.0, "projects_count": 12},
                {"name": "Jenkins", "level": "advanced", "years_experience": 3.5, "projects_count": 9}
            ],
            "education": "BS Computer Engineering, Texas A&M University",
            "previous_companies": ["Netflix", "Uber", "HashiCorp"],
            "github_url": "https://github.com/mrodriguez-devops",
            "cover_letter": "DevOps engineer with 4 years of experience in building and maintaining large-scale infrastructure. At Netflix, I managed Kubernetes clusters serving 200M+ users globally. I'm passionate about automation and have reduced deployment times by 60% through improved CI/CD processes.",
            "resume_text": """
MICHAEL RODRIGUEZ - DevOps Engineer
Email: michael.rodriguez@email.com | GitHub: github.com/mrodriguez-devops

EXPERIENCE
Senior DevOps Engineer | Netflix | 2022-2024
• Managed Kubernetes clusters across multiple AWS regions serving 200M+ global users
• Implemented auto-scaling policies reducing infrastructure costs by 30% ($2M annually)
• Built monitoring and alerting systems using Prometheus, Grafana, and PagerDuty
• Led incident response for critical outages, maintaining 99.9% uptime SLA
• Automated deployment pipelines reducing release time from 4 hours to 30 minutes

DevOps Engineer | Uber | 2020-2022
• Designed and implemented infrastructure as code using Terraform and Ansible
• Managed containerized applications across 50+ microservices
• Set up centralized logging with ELK stack processing 100GB+ daily logs
• Collaborated with development teams to optimize application performance
• Technologies: AWS, Kubernetes, Docker, Terraform, Jenkins, Python

Infrastructure Engineer | HashiCorp | 2020
• Contributed to Terraform provider development for AWS services
• Built internal tools for infrastructure provisioning and management
• Implemented security scanning and compliance automation
• Worked with enterprise customers on infrastructure optimization

TECHNICAL SKILLS
Cloud Platforms: AWS (Expert), Azure (Intermediate), GCP (Basic)
Container Orchestration: Kubernetes (Advanced), Docker Swarm, ECS
Infrastructure as Code: Terraform, CloudFormation, Ansible
CI/CD: Jenkins, GitLab CI, GitHub Actions, ArgoCD
Monitoring: Prometheus, Grafana, Datadog, New Relic, ELK Stack
Languages: Python, Bash, Go (Learning)

EDUCATION
Bachelor of Science in Computer Engineering | Texas A&M University | 2016-2020

CERTIFICATIONS
• AWS Solutions Architect Professional
• Certified Kubernetes Administrator (CKA)
• HashiCorp Certified: Terraform Associate

PROJECTS
• Built multi-region disaster recovery system reducing RTO from 4 hours to 15 minutes
• Created automated security compliance framework achieving SOC 2 Type II certification
• Open source contributor to Kubernetes and Terraform ecosystems
            """,
            "preferred_salary": 145000.0,
            "availability": "Available immediately"
        },
        {
            "name": "Emily Johnson",
            "email": "emily.johnson@email.com",
            "position": "Junior Frontend Developer",
            "experience_years": 1.5,
            "skills": [
                {"name": "JavaScript", "level": "intermediate", "years_experience": 1.5, "projects_count": 5},
                {"name": "React", "level": "intermediate", "years_experience": 1.0, "projects_count": 4},
                {"name": "HTML/CSS", "level": "advanced", "years_experience": 2.0, "projects_count": 8},
                {"name": "TypeScript", "level": "beginner", "years_experience": 0.5, "projects_count": 2},
                {"name": "Git", "level": "intermediate", "years_experience": 1.5, "projects_count": 6}
            ],
            "education": "Bootcamp Graduate - General Assembly Full Stack Web Development",
            "previous_companies": ["Local Startup", "Freelance"],
            "github_url": "https://github.com/emilyjohnson",
            "portfolio_url": "https://emilyjohnson.dev",
            "cover_letter": "Recent bootcamp graduate with passion for frontend development and user experience. During my bootcamp, I built 5 full-stack applications and contributed to open source projects. I'm eager to learn and grow as part of an experienced development team.",
            "resume_text": """
EMILY JOHNSON - Frontend Developer
Email: emily.johnson@email.com | Portfolio: emilyjohnson.dev | GitHub: github.com/emilyjohnson

EXPERIENCE
Frontend Developer | Local Tech Startup | 2023-2024 (1 year)
• Built responsive web applications using React and modern JavaScript
• Collaborated with UX designers to implement pixel-perfect designs
• Implemented user authentication and state management with Redux
• Participated in code reviews and agile development processes
• Technologies: React, JavaScript, HTML5, CSS3, Redux, Git

Freelance Web Developer | 2022-2023
• Created websites for small businesses using HTML, CSS, and JavaScript
• Built responsive designs ensuring mobile compatibility
• Integrated third-party APIs for payment processing and social media
• Delivered 8 projects on time and within budget

EDUCATION
Full Stack Web Development Immersive | General Assembly | 2022
• 12-week intensive program covering HTML, CSS, JavaScript, React, Node.js
• Built 4 full-stack applications including e-commerce site and social media app
• Capstone project: Task management app with real-time collaboration features

Bachelor of Arts in Graphic Design | California State University | 2018-2021

TECHNICAL SKILLS
Languages: JavaScript (Intermediate), HTML5 (Advanced), CSS3 (Advanced)
Frameworks: React, Bootstrap, jQuery
Tools: Git, VS Code, Figma, Adobe Creative Suite
Learning: TypeScript, Node.js, Testing frameworks

PROJECTS
Portfolio Website (2024)
• Personal portfolio showcasing projects and skills
• Built with React and deployed on Netlify
• Features responsive design and smooth animations

E-commerce App (Bootcamp Project)
• Full-stack application with product catalog and shopping cart
• React frontend with Node.js/Express backend
• Implemented user authentication and payment processing

Task Management App (Capstone)
• Real-time collaborative task management with WebSocket integration
• React frontend with Redux state management
• Features drag-and-drop interface and team collaboration tools

ACHIEVEMENTS
• Bootcamp top performer with 98% final grade
• Contributed to 3 open source React component libraries
• Built portfolio website featured in bootcamp showcase
            """,
            "preferred_salary": 75000.0,
            "availability": "Available with 1 week notice"
        }
    ]

def analyze_candidate_with_details(ai_service: AIService, candidate_data: Dict) -> Dict:
    """Analyze a single candidate and display detailed results"""
    try:
        print(f"\n{'='*80}")
        print(f"🔍 ANALYZING CANDIDATE: {candidate_data['name']}")
        print(f"{'='*80}")
        
        # Create candidate profile
        skills = []
        for skill_data in candidate_data["skills"]:
            skills.append(CandidateSkill(
                name=skill_data["name"],
                level=SkillLevel(skill_data["level"]),
                years_experience=skill_data["years_experience"],
                projects_count=skill_data["projects_count"],
                certifications=skill_data.get("certifications", [])
            ))
        
        candidate = CandidateProfile(
            name=candidate_data["name"],
            email=candidate_data["email"],
            position=candidate_data["position"],
            experience_years=candidate_data["experience_years"],
            skills=skills,
            education=candidate_data["education"],
            previous_companies=candidate_data["previous_companies"],
            github_url=candidate_data["github_url"],
            linkedin_url=candidate_data.get("linkedin_url", ""),
            portfolio_url=candidate_data.get("portfolio_url", ""),
            cover_letter=candidate_data["cover_letter"],
            resume_text=candidate_data["resume_text"],
            preferred_salary=candidate_data["preferred_salary"],
            availability=candidate_data["availability"]
        )
        
        # Perform AI analysis
        analysis = ai_service.analyze_candidate(candidate)
        
        if not analysis:
            print("❌ Analysis failed")
            return {"success": False}
        
        # Display comprehensive results
        print(f"\n📊 OVERALL ASSESSMENT")
        print(f"Overall Score: {analysis.overall_score}/100")
        print(f"Experience Level: {analysis.estimated_level} ({analysis.experience_analysis.years_experience} years)")
        print(f"Specialization: {analysis.technical_skills.specialization_area}")
        print(f"Career Progression: {analysis.experience_analysis.career_progression}")
        
        print(f"\n🎯 COMPETENCY BREAKDOWN")
        print(f"Technical Skills:     {analysis.competency_scores.technical_skills:6.1f}/100")
        print(f"Problem Solving:     {analysis.competency_scores.problem_solving:6.1f}/100")
        print(f"System Design:       {analysis.competency_scores.system_design:6.1f}/100")
        print(f"Communication:       {analysis.competency_scores.communication:6.1f}/100")
        print(f"Leadership:          {analysis.competency_scores.leadership:6.1f}/100")
        print(f"Domain Knowledge:    {analysis.competency_scores.domain_knowledge:6.1f}/100")
        print(f"Learning Agility:    {analysis.competency_scores.learning_agility:6.1f}/100")
        print(f"Collaboration:       {analysis.competency_scores.collaboration:6.1f}/100")
        
        print(f"\n💻 TECHNICAL SKILLS ANALYSIS")
        tech = analysis.technical_skills
        print(f"Primary Languages:   {', '.join(tech.programming_languages.get('primary', []))}")
        print(f"Secondary Languages: {', '.join(tech.programming_languages.get('secondary', []))}")
        print(f"Proficiency Score:   {tech.proficiency_score}/100")
        print(f"Technical Depth:     {tech.technical_depth_score}/100")
        print(f"Technical Breadth:   {tech.technical_breadth_score}/100")
        print(f"Learning Trajectory: {tech.learning_trajectory}")
        
        print(f"\n📈 EXPERIENCE ANALYSIS")
        exp = analysis.experience_analysis
        print(f"Leadership Experience: {'Yes' if exp.leadership_experience.get('has_leadership') else 'No'}")
        if exp.leadership_experience.get('has_leadership'):
            print(f"Team Size Managed:     {exp.leadership_experience.get('team_size_managed', 0)} people")
            print(f"Leadership Score:      {exp.leadership_experience.get('leadership_score', 0)}/100")
        print(f"Project Scale:         {exp.project_complexity.get('scale', 'unknown')}")
        print(f"Complexity Score:      {exp.project_complexity.get('complexity_score', 0)}/100")
        print(f"Industry Experience:   {', '.join(exp.industry_experience) if exp.industry_experience else 'Not specified'}")
        
        print(f"\n✅ KEY STRENGTHS")
        for i, strength in enumerate(analysis.strengths, 1):
            print(f"{i}. {strength}")
        
        if analysis.areas_for_growth:
            print(f"\n📝 AREAS FOR GROWTH")
            for i, area in enumerate(analysis.areas_for_growth, 1):
                print(f"{i}. {area}")
        
        print(f"\n🎯 INTERVIEW STRATEGY")
        strategy = analysis.interview_strategy
        print(f"Primary Interview Type: {strategy.primary_interview_type}")
        print(f"Recommended Duration:   {strategy.interview_duration} minutes")
        print(f"Interviewer Seniority:  {strategy.interviewer_seniority}")
        print(f"Focus Areas:")
        for i, area in enumerate(strategy.recommended_focus_areas, 1):
            print(f"  {i}. {area}")
        
        print(f"\n📋 HIRING RECOMMENDATION")
        hiring = analysis.hiring_recommendation
        proceed_text = "✅ PROCEED" if hiring.proceed_to_interview else "❌ DO NOT PROCEED"
        print(f"Decision: {proceed_text} to interview")
        print(f"Recommended Level:      {hiring.recommended_role_level}")
        print(f"Salary Assessment:      {hiring.salary_expectation_assessment}")
        print(f"Success Likelihood:     {hiring.likelihood_of_success}")
        print(f"Key Decision Factors:")
        for i, factor in enumerate(hiring.key_decision_factors, 1):
            print(f"  {i}. {factor}")
        
        if analysis.red_flags:
            print(f"\n⚠️ RED FLAGS")
            for i, flag in enumerate(analysis.red_flags, 1):
                print(f"{i}. {flag}")
        
        print(f"\n📋 NEXT STEPS")
        for i, step in enumerate(analysis.next_steps, 1):
            print(f"{i}. {step}")
        
        print(f"\n💰 ANALYSIS METADATA")
        print(f"Confidence Score: {analysis.confidence_score:.2f}/1.0")
        print(f"Analysis Time: {analysis.analysis_timestamp}")
        
        return {
            "success": True,
            "analysis": analysis.to_dict(),
            "candidate_name": candidate_data["name"]
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {candidate_data['name']}: {e}")
        return {"success": False, "error": str(e)}

def run_enhanced_demo():
    """Run the enhanced candidate analysis demo"""
    print("🤖 Enhanced AI Candidate Analysis Demo")
    print("=" * 60)
    print("Features: Detailed technical assessment, experience evaluation,")
    print("interview strategy, and hiring recommendations with numerical scores")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        print("   Get your key from: https://openrouter.ai/keys")
        return
    
    try:
        # Initialize AI service
        config = load_ai_config()
        ai_service = AIService(api_key=api_key, model=config["model"])
        
        print(f"✅ AI Service initialized")
        print(f"   Model: {ai_service.model}")
        print(f"   Cost per analysis: ~$0.002-0.005")
        
        # Get sample candidates
        candidates = create_detailed_candidate_samples()
        print(f"\n📊 Sample Candidates: {len(candidates)}")
        for i, candidate in enumerate(candidates, 1):
            print(f"   {i}. {candidate['name']} - {candidate['position']} ({candidate['experience_years']} years)")
        
        # Analyze each candidate
        results = []
        total_cost = 0.0
        
        for candidate_data in candidates:
            result = analyze_candidate_with_details(ai_service, candidate_data)
            results.append(result)
            
            if result["success"]:
                # Estimate cost (rough approximation)
                resume_length = len(candidate_data.get("resume_text", ""))
                estimated_tokens = resume_length * 0.75 + 2000  # Rough estimation
                estimated_cost = estimated_tokens * 0.00025 / 1000  # Claude-3-Haiku pricing
                total_cost += estimated_cost
        
        # Summary
        successful_analyses = sum(1 for r in results if r["success"])
        print(f"\n{'='*80}")
        print(f"📈 DEMO SUMMARY")
        print(f"{'='*80}")
        print(f"Candidates Analyzed: {successful_analyses}/{len(candidates)}")
        print(f"Total Estimated Cost: ${total_cost:.6f}")
        print(f"Average Cost per Analysis: ${total_cost/len(candidates):.6f}")
        
        if successful_analyses > 0:
            # Show comparison
            print(f"\n📊 CANDIDATE COMPARISON")
            print(f"{'Name':<20} {'Level':<12} {'Overall':<8} {'Technical':<10} {'Proceed':<8}")
            print("-" * 70)
            
            for result in results:
                if result["success"]:
                    analysis_data = result["analysis"]
                    overall = analysis_data["overall_assessment"]
                    hiring = analysis_data["hiring_recommendation"]
                    
                    name = result["candidate_name"][:19]
                    level = overall["estimated_level"][:11]
                    overall_score = f"{overall['overall_score']}/100"
                    tech_score = f"{analysis_data['competency_scores']['technical_skills']:.0f}/100"
                    proceed = "✅ Yes" if hiring["proceed_to_interview"] else "❌ No"
                    
                    print(f"{name:<20} {level:<12} {overall_score:<8} {tech_score:<10} {proceed:<8}")
        
        print(f"\n✨ Enhanced analysis complete!")
        print(f"\nKey improvements:")
        print(f"• Detailed technical skills breakdown with proficiency scoring")
        print(f"• Experience analysis with leadership and project complexity")
        print(f"• 8-dimensional competency scoring")
        print(f"• Specific interview strategy recommendations")
        print(f"• Data-driven hiring recommendations")
        print(f"• Comprehensive red flag detection")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo error details:")

if __name__ == "__main__":
    run_enhanced_demo()
