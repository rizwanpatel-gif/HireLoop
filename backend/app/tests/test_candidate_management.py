"""
Phase 4: Candidate Management API Demo
=====================================

Comprehensive demo of the candidate management system featuring:
- Candidate creation with form data and file uploads
- Background AI analysis processing
- Database integration and status tracking
- Smart interviewer matching
- Complete workflow demonstration
"""

import asyncio
import json
import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# Demo configuration
API_BASE_URL = "http://localhost:8000"
DEMO_RESUME_DIR = Path("demo_resumes")
DEMO_RESUME_DIR.mkdir(exist_ok=True)

# Sample candidate data for testing
SAMPLE_CANDIDATES = [
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@email.com",
        "position": "Senior Full Stack Developer",
        "experience_years": 6.5,
        "phone": "+1-555-0101",
        "location": "San Francisco, CA",
        "skills": [
            {"name": "Python", "level": "advanced", "years_experience": 6, "projects_count": 12},
            {"name": "JavaScript", "level": "advanced", "years_experience": 5, "projects_count": 10},
            {"name": "React", "level": "advanced", "years_experience": 4, "projects_count": 8},
            {"name": "Django", "level": "intermediate", "years_experience": 3, "projects_count": 6},
            {"name": "PostgreSQL", "level": "intermediate", "years_experience": 4, "projects_count": 7},
            {"name": "AWS", "level": "intermediate", "years_experience": 3, "projects_count": 5}
        ],
        "education": "B.S. Computer Science, Stanford University (2017)",
        "previous_companies": ["Meta", "Spotify", "TravelTech"],
        "portfolio_url": "https://sarahchen.dev",
        "github_url": "https://github.com/sarahchen",
        "linkedin_url": "https://linkedin.com/in/sarahchen",
        "cover_letter": "I'm excited to apply for the Senior Full Stack Developer position. With 6+ years of experience building scalable web applications at top tech companies, I bring expertise in Python, JavaScript, and cloud technologies.",
        "resume_text": """
SARAH CHEN
Senior Full Stack Developer
san francisco, ca | sarah.chen@email.com | +1-555-0101

EXPERIENCE

Meta (Facebook) | Senior Software Engineer | 2022-2024
• Led development of real-time messaging platform serving 100M+ users
• Architected microservices using Python, Django, and PostgreSQL
• Implemented React components with 40% performance improvement
• Mentored team of 3 junior developers

Spotify | Software Engineer | 2020-2022  
• Built music recommendation engine using Python and machine learning
• Developed REST APIs handling 10M+ requests daily
• Optimized database queries reducing response time by 60%
• Collaborated with cross-functional teams on feature launches

TravelTech | Junior Developer | 2018-2020
• Created booking platform frontend using React and TypeScript
• Integrated payment systems and third-party APIs
• Participated in code reviews and agile development process

TECHNICAL SKILLS
• Languages: Python, JavaScript, TypeScript, SQL
• Frameworks: Django, React, Node.js, Flask
• Databases: PostgreSQL, MongoDB, Redis
• Cloud: AWS (EC2, S3, RDS), Docker, Kubernetes
• Tools: Git, Jenkins, Jira, Figma

EDUCATION
B.S. Computer Science, Stanford University (2017)
        """,
        "preferred_salary": 180000,
        "availability": "Available immediately",
        "remote_preference": "hybrid",
        "source": "linkedin"
    },
    {
        "name": "Michael Rodriguez",
        "email": "michael.rodriguez@email.com", 
        "position": "DevOps Engineer",
        "experience_years": 4.0,
        "phone": "+1-555-0102",
        "location": "Austin, TX",
        "skills": [
            {"name": "AWS", "level": "advanced", "years_experience": 4, "projects_count": 10},
            {"name": "Kubernetes", "level": "advanced", "years_experience": 3, "projects_count": 8},
            {"name": "Docker", "level": "expert", "years_experience": 4, "projects_count": 15},
            {"name": "Terraform", "level": "intermediate", "years_experience": 2, "projects_count": 6},
            {"name": "Python", "level": "intermediate", "years_experience": 3, "projects_count": 7},
            {"name": "Jenkins", "level": "advanced", "years_experience": 3, "projects_count": 9}
        ],
        "education": "B.S. Computer Engineering, UT Austin (2019)",
        "previous_companies": ["Netflix", "Uber", "CloudTech"],
        "github_url": "https://github.com/mrodriguez",
        "linkedin_url": "https://linkedin.com/in/mrodriguez",
        "cover_letter": "Passionate DevOps engineer with 4 years of experience building and maintaining cloud infrastructure at scale. Expert in containerization, orchestration, and CI/CD pipelines.",
        "resume_text": """
MICHAEL RODRIGUEZ
DevOps Engineer
austin, tx | michael.rodriguez@email.com | +1-555-0102

EXPERIENCE

Netflix | Senior DevOps Engineer | 2022-2024
• Managed Kubernetes clusters serving 200M+ global users
• Implemented CI/CD pipelines reducing deployment time by 80%
• Automated infrastructure provisioning using Terraform and AWS
• Maintained 99.99% uptime for critical streaming services

Uber | DevOps Engineer | 2020-2022
• Built containerized microservices infrastructure using Docker
• Implemented monitoring and logging solutions with ELK stack
• Automated scaling policies handling 10x traffic spikes
• Collaborated with development teams on deployment strategies

CloudTech | Junior DevOps Engineer | 2019-2020
• Managed AWS infrastructure for startup applications
• Created deployment scripts and automation tools
• Participated in incident response and troubleshooting

TECHNICAL SKILLS
• Cloud Platforms: AWS (EC2, EKS, S3, RDS), GCP, Azure
• Containerization: Docker, Kubernetes, Helm
• Infrastructure as Code: Terraform, CloudFormation
• CI/CD: Jenkins, GitLab CI, GitHub Actions
• Monitoring: Prometheus, Grafana, ELK Stack
• Languages: Python, Bash, Go, YAML

EDUCATION
B.S. Computer Engineering, University of Texas at Austin (2019)
        """,
        "preferred_salary": 140000,
        "availability": "2 weeks notice",
        "remote_preference": "remote",
        "source": "job_board"
    },
    {
        "name": "Emily Johnson",
        "email": "emily.johnson@email.com",
        "position": "Junior Frontend Developer", 
        "experience_years": 1.5,
        "phone": "+1-555-0103",
        "location": "Portland, OR",
        "skills": [
            {"name": "JavaScript", "level": "intermediate", "years_experience": 2, "projects_count": 5},
            {"name": "React", "level": "intermediate", "years_experience": 1, "projects_count": 4},
            {"name": "CSS", "level": "advanced", "years_experience": 3, "projects_count": 8},
            {"name": "HTML", "level": "expert", "years_experience": 3, "projects_count": 10},
            {"name": "TypeScript", "level": "beginner", "years_experience": 0.5, "projects_count": 2},
            {"name": "Git", "level": "intermediate", "years_experience": 2, "projects_count": 6}
        ],
        "education": "Coding Bootcamp Graduate - The Odin Project (2022), B.A. Graphic Design, Portland State (2020)",
        "previous_companies": ["TechStartup", "Freelance"],
        "portfolio_url": "https://emilyjohnson.design",
        "github_url": "https://github.com/emilyjohnson",
        "linkedin_url": "https://linkedin.com/in/emilyjohnson",
        "cover_letter": "Recent coding bootcamp graduate with a design background, passionate about creating beautiful and functional user interfaces. Eager to contribute to a collaborative development team.",
        "resume_text": """
EMILY JOHNSON
Junior Frontend Developer
portland, or | emily.johnson@email.com | +1-555-0103

EXPERIENCE

TechStartup | Junior Frontend Developer | 2023-2024
• Developed responsive web applications using React and CSS
• Collaborated with UX/UI team to implement pixel-perfect designs
• Built reusable component library used across 5+ projects
• Participated in code reviews and agile development process

Freelance | Web Designer/Developer | 2022-2023
• Created custom websites for small businesses using HTML, CSS, JavaScript
• Designed marketing materials and brand identities
• Managed client relationships and project timelines

PROJECTS

E-commerce Platform (React, Redux, Styled Components)
• Built full-featured shopping cart with payment integration
• Implemented responsive design supporting mobile and desktop
• Used modern React patterns including hooks and context

Personal Portfolio (HTML, CSS, JavaScript)
• Showcased design and development projects
• Implemented smooth animations and interactive elements
• Optimized for performance and accessibility

TECHNICAL SKILLS
• Frontend: JavaScript, React, HTML5, CSS3, TypeScript
• Styling: CSS Grid, Flexbox, Styled Components, Sass
• Tools: Git, VS Code, Figma, Adobe Creative Suite
• Learning: Node.js, Testing (Jest), GraphQL

EDUCATION
• Coding Bootcamp Graduate - The Odin Project (2022)
• B.A. Graphic Design, Portland State University (2020)
        """,
        "preferred_salary": 70000,
        "availability": "Available immediately",
        "remote_preference": "hybrid",
        "source": "referral"
    }
]


def create_demo_resume_files():
    """Create sample resume files for upload testing"""
    print("📄 Creating demo resume files...")
    
    for candidate in SAMPLE_CANDIDATES:
        # Create text resume file
        resume_filename = f"{candidate['name'].replace(' ', '_').lower()}_resume.txt"
        resume_path = DEMO_RESUME_DIR / resume_filename
        
        with open(resume_path, 'w', encoding='utf-8') as f:
            f.write(candidate['resume_text'])
        
        print(f"   ✅ Created: {resume_filename}")
    
    print()


def check_api_health():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to API server")
        print(f"   Make sure the server is running on {API_BASE_URL}")
        print("   Run: python candidate_management_api.py")
        return False


def create_candidate(candidate_data: Dict[str, Any], with_file: bool = True) -> Dict[str, Any]:
    """Create a candidate via API"""
    print(f"👤 Creating candidate: {candidate_data['name']}")
    
    # Prepare form data
    form_data = {
        'name': candidate_data['name'],
        'email': candidate_data['email'],
        'position': candidate_data['position'],
        'experience_years': candidate_data['experience_years'],
        'skills': json.dumps(candidate_data['skills']),
        'phone': candidate_data.get('phone'),
        'location': candidate_data.get('location'),
        'education': candidate_data.get('education'),
        'previous_companies': json.dumps(candidate_data.get('previous_companies', [])),
        'portfolio_url': candidate_data.get('portfolio_url'),
        'github_url': candidate_data.get('github_url'),
        'linkedin_url': candidate_data.get('linkedin_url'),
        'cover_letter': candidate_data.get('cover_letter'),
        'resume_text': candidate_data.get('resume_text'),
        'preferred_salary': candidate_data.get('preferred_salary'),
        'availability': candidate_data.get('availability'),
        'remote_preference': candidate_data.get('remote_preference'),
        'source': candidate_data.get('source')
    }
    
    # Remove None values
    form_data = {k: v for k, v in form_data.items() if v is not None}
    
    files = None
    if with_file:
        # Prepare resume file
        resume_filename = f"{candidate_data['name'].replace(' ', '_').lower()}_resume.txt"
        resume_path = DEMO_RESUME_DIR / resume_filename
        
        if resume_path.exists():
            files = {'resume_file': (resume_filename, open(resume_path, 'rb'), 'text/plain')}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/candidates/",
            data=form_data,
            files=files
        )
        
        if files:
            files['resume_file'][1].close()  # Close file handle
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Created successfully")
            print(f"   📋 Candidate ID: {result['candidate_id']}")
            print(f"   🔄 Analysis Task ID: {result['analysis_task_id']}")
            print(f"   ⏱️ Estimated analysis time: {result['estimated_analysis_time']}s")
            return result
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def wait_for_analysis(candidate_id: str, timeout: int = 120) -> bool:
    """Wait for candidate analysis to complete"""
    print(f"⏳ Waiting for AI analysis to complete for candidate {candidate_id}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_BASE_URL}/api/candidates/{candidate_id}")
            if response.status_code == 200:
                candidate = response.json()
                status = candidate.get('ai_analysis_status')
                
                if status == 'completed':
                    print(f"   ✅ Analysis completed!")
                    print(f"   📊 Overall Score: {candidate.get('ai_overall_score', 'N/A')}/100")
                    print(f"   🔧 Technical Score: {candidate.get('ai_technical_score', 'N/A')}/100")
                    print(f"   🎯 Confidence: {candidate.get('ai_confidence_score', 'N/A')}")
                    return True
                elif status == 'failed':
                    print(f"   ❌ Analysis failed")
                    return False
                else:
                    print(f"   🔄 Status: {status}")
                    time.sleep(5)
            else:
                print(f"   ❌ Error checking status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print(f"   ⏰ Timeout after {timeout} seconds")
    return False


def get_candidate_details(candidate_id: str) -> Dict[str, Any]:
    """Get detailed candidate information"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/candidates/{candidate_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting candidate details: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_candidate_analysis(candidate_id: str) -> Dict[str, Any]:
    """Get detailed AI analysis results"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/candidates/{candidate_id}/analysis")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting analysis: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def list_candidates(filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """List candidates with optional filters"""
    try:
        params = filters or {}
        response = requests.get(f"{API_BASE_URL}/api/candidates/", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error listing candidates: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def display_candidate_summary(candidate: Dict[str, Any]):
    """Display a summary of candidate information"""
    print(f"\n📋 CANDIDATE SUMMARY: {candidate['name']}")
    print(f"   📧 Email: {candidate['email']}")
    print(f"   💼 Position: {candidate['position']}")
    print(f"   📅 Experience: {candidate['experience_years']} years")
    print(f"   📍 Location: {candidate.get('location', 'Not specified')}")
    print(f"   📊 Status: {candidate['status']}")
    print(f"   🤖 AI Analysis: {candidate['ai_analysis_status']}")
    
    if candidate.get('ai_overall_score'):
        print(f"   📈 Overall Score: {candidate['ai_overall_score']}/100")
        print(f"   🔧 Technical Score: {candidate['ai_technical_score']}/100")
    
    print(f"   🛠️ Top Skills: {', '.join(candidate.get('top_skills', []))}")
    print(f"   ⏰ Created: {candidate['created_at']}")


def display_analysis_results(analysis: Dict[str, Any]):
    """Display detailed analysis results"""
    if analysis.get('status') != 'completed':
        print(f"❌ Analysis not completed: {analysis.get('status')}")
        return
    
    results = analysis.get('analysis_results', {})
    
    print(f"\n🔍 DETAILED AI ANALYSIS")
    print(f"   📊 Overall Score: {results.get('overall_score', 'N/A')}/100")
    print(f"   🔧 Technical Score: {results.get('technical_score', 'N/A')}/100")
    print(f"   🎖️ Estimated Level: {results.get('estimated_level', 'N/A')}")
    
    # Strengths
    strengths = results.get('strengths', [])
    if strengths:
        print(f"   ✅ Strengths:")
        for strength in strengths[:3]:
            print(f"      • {strength}")
    
    # Areas for improvement
    improvements = results.get('areas_for_improvement', [])
    if improvements:
        print(f"   📝 Areas for Improvement:")
        for improvement in improvements[:2]:
            print(f"      • {improvement}")
    
    # Competency scores
    competency = results.get('competency_scores', {})
    if competency:
        print(f"   🎯 Competency Breakdown:")
        for skill, score in competency.items():
            if isinstance(score, (int, float)):
                print(f"      • {skill.replace('_', ' ').title()}: {score}/100")
    
    # Matched interviewers
    matched = analysis.get('matched_interviewers', [])
    if matched:
        print(f"   🎯 Top Interviewer Matches:")
        for match in matched[:2]:
            print(f"      • {match.get('interviewer_name')}: {match.get('overall_score')}/100 ({match.get('confidence')})")


async def run_comprehensive_demo():
    """Run comprehensive candidate management demo"""
    print("🤖 Candidate Management API - Comprehensive Demo")
    print("=" * 60)
    print("Features:")
    print("• Candidate creation with form data and file uploads")
    print("• Background AI analysis and scoring")
    print("• Database integration with PostgreSQL")
    print("• Smart interviewer matching")
    print("• Real-time status tracking")
    print("• Comprehensive candidate management")
    print("=" * 60)
    print()
    
    # Check API availability
    if not check_api_health():
        print("Please start the API server first:")
        print("python candidate_management_api.py")
        return
    
    print()
    
    # Create demo files
    create_demo_resume_files()
    
    # Track created candidates
    created_candidates = []
    
    print("📝 PHASE 1: CANDIDATE CREATION")
    print("-" * 40)
    
    # Create candidates
    for i, candidate_data in enumerate(SAMPLE_CANDIDATES):
        print(f"\n{i+1}. Creating candidate: {candidate_data['name']}")
        
        result = create_candidate(candidate_data, with_file=True)
        if result:
            created_candidates.append(result['candidate_id'])
        
        # Small delay between creations
        time.sleep(2)
    
    print(f"\n✅ Created {len(created_candidates)} candidates")
    print()
    
    print("🔍 PHASE 2: ANALYSIS MONITORING")
    print("-" * 40)
    
    # Wait for analysis completion
    for i, candidate_id in enumerate(created_candidates):
        print(f"\n{i+1}. Monitoring analysis for candidate {candidate_id}")
        success = wait_for_analysis(candidate_id, timeout=60)
        if not success:
            print(f"   ⚠️ Analysis did not complete in time")
    
    print()
    
    print("📊 PHASE 3: RESULTS REVIEW")
    print("-" * 40)
    
    # Display results for each candidate
    for i, candidate_id in enumerate(created_candidates):
        candidate = get_candidate_details(candidate_id)
        if candidate:
            display_candidate_summary(candidate)
            
            # Get detailed analysis
            analysis = get_candidate_analysis(candidate_id)
            if analysis:
                display_analysis_results(analysis)
        
        print()
    
    print("📋 PHASE 4: CANDIDATE LISTING & FILTERING")
    print("-" * 40)
    
    # List all candidates
    print("\n🔍 All Candidates:")
    all_candidates = list_candidates()
    if all_candidates:
        print(f"   Total: {all_candidates['total_count']} candidates")
        for candidate in all_candidates['candidates']:
            print(f"   • {candidate['name']} - {candidate['position']} ({candidate['status']})")
    
    # Filter by status
    print("\n🔍 Analyzed Candidates:")
    analyzed = list_candidates({'status': 'analyzed'})
    if analyzed:
        print(f"   Found: {analyzed['total_count']} analyzed candidates")
        for candidate in analyzed['candidates']:
            score = candidate.get('ai_overall_score', 'N/A')
            print(f"   • {candidate['name']}: {score}/100")
    
    # Filter by experience
    print("\n🔍 Senior Candidates (5+ years):")
    senior = list_candidates({'min_experience': 5.0})
    if senior:
        print(f"   Found: {senior['total_count']} senior candidates")
        for candidate in senior['candidates']:
            exp = candidate['experience_years']
            print(f"   • {candidate['name']}: {exp} years experience")
    
    # Filter by score
    print("\n🔍 High-scoring Candidates (80+):")
    high_score = list_candidates({'min_score': 80.0})
    if high_score:
        print(f"   Found: {high_score['total_count']} high-scoring candidates")
        for candidate in high_score['candidates']:
            score = candidate.get('ai_overall_score', 'N/A')
            print(f"   • {candidate['name']}: {score}/100")
    
    print()
    
    print("📈 DEMO SUMMARY")
    print("=" * 40)
    print(f"✅ Candidates Created: {len(created_candidates)}")
    
    # Get final statistics
    final_list = list_candidates()
    if final_list:
        total = final_list['total_count']
        analyzed_count = len([c for c in final_list['candidates'] if c['ai_analysis_status'] == 'completed'])
        avg_score = sum([c.get('ai_overall_score', 0) for c in final_list['candidates'] if c.get('ai_overall_score')]) / max(analyzed_count, 1)
        
        print(f"📊 Analysis Success Rate: {analyzed_count}/{total} ({analyzed_count/total*100:.1f}%)")
        print(f"📈 Average Score: {avg_score:.1f}/100")
        print(f"🎯 Interviews Ready: {len([c for c in final_list['candidates'] if c.get('ai_overall_score', 0) >= 70])}")
    
    print("\n🚀 Key Features Demonstrated:")
    print("   • Form-based candidate creation with file uploads")
    print("   • Background AI analysis processing")
    print("   • Real-time status tracking and monitoring")
    print("   • Database persistence and querying")
    print("   • Smart interviewer matching")
    print("   • Comprehensive filtering and search")
    
    print("\n📖 Next Steps:")
    print("   • View API documentation: http://localhost:8000/docs")
    print("   • Explore candidate details via API")
    print("   • Implement frontend interface")
    print("   • Configure production database")


if __name__ == "__main__":
    print("🚀 Starting Candidate Management Demo...")
    print("   Make sure the API server is running first!")
    print("   Run: python candidate_management_api.py")
    print()
    
    asyncio.run(run_comprehensive_demo())
