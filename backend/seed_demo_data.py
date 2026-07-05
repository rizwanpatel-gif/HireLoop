#!/usr/bin/env python3
"""
One-off seed script for the AI-agent hiring pipeline demo.
Run after migrate_add_hiring_pipeline.py. Safe to re-run (skips rows that already exist).
"""
from app.core.database import SessionLocal
from app.models.models import JobRole, User, UserRole

JOB_ROLES = [
    {
        "title": "Backend Developer",
        "department": "Engineering",
        "jd_text": (
            "We are hiring a Backend Developer to build and maintain our Python/FastAPI services. "
            "Requirements: 2+ years of Python experience, hands-on experience with REST API design, "
            "SQL databases (PostgreSQL or SQLite), and version control (Git). Familiarity with async "
            "programming, SQLAlchemy or a similar ORM, and basic cloud deployment (Docker) is a strong plus. "
            "The candidate should be comfortable writing clean, testable code and collaborating with "
            "frontend engineers on API contracts."
        ),
    },
    {
        "title": "Data Analyst",
        "department": "Analytics",
        "jd_text": (
            "We are hiring a Data Analyst to turn raw business data into actionable insights. "
            "Requirements: strong SQL skills, experience with Python (pandas) or R for data manipulation, "
            "ability to build dashboards (e.g. Power BI, Tableau, or similar), and a solid grasp of "
            "statistics. Experience presenting findings to non-technical stakeholders and working with "
            "large datasets is a plus."
        ),
    },
    {
        "title": "Frontend Developer",
        "department": "Engineering",
        "jd_text": (
            "We are hiring a Frontend Developer to build user-facing features in React. "
            "Requirements: 2+ years of JavaScript/React experience, comfort with modern CSS, REST API "
            "integration, and responsive design. Experience with TypeScript, state management libraries, "
            "and basic UX/accessibility principles is a strong plus."
        ),
    },
]

INTERVIEWERS = [
    # Placeholder emails - swap these for real Gmail accounts and run
    # scripts/authorize_interviewer.py for each if calendar integration is ever
    # revisited. None of this is wired to real accounts right now.
    {"email": "interviewer.junior@example.com", "name": "Ayesha Khan", "experience_years": 3, "expertise_areas": "python,rest-apis"},
    {"email": "interviewer.mid@example.com", "name": "Arjun Verma", "experience_years": 6, "expertise_areas": "python,react,sql"},
    {"email": "interviewer.senior@example.com", "name": "Rakesh Mohan", "experience_years": 10, "expertise_areas": "system-design,python,react,data-analytics"},
]


def seed():
    db = SessionLocal()
    try:
        for role in JOB_ROLES:
            existing = db.query(JobRole).filter(JobRole.title == role["title"]).first()
            if existing:
                print(f"✅ JobRole '{role['title']}' already exists (id={existing.id})")
                continue
            db.add(JobRole(**role, is_active=1))
            print(f"➕ Created JobRole '{role['title']}'")

        for interviewer in INTERVIEWERS:
            existing = db.query(User).filter(User.email == interviewer["email"]).first()
            if existing:
                existing.name = interviewer["name"]
                existing.experience_years = interviewer["experience_years"]
                existing.expertise_areas = interviewer["expertise_areas"]
                existing.role = UserRole.INTERVIEWER
                print(f"✅ Interviewer '{interviewer['email']}' already exists, updated name/experience/expertise")
                continue
            db.add(User(
                email=interviewer["email"],
                name=interviewer["name"],
                role=UserRole.INTERVIEWER,
                experience_years=interviewer["experience_years"],
                expertise_areas=interviewer["expertise_areas"],
            ))
            print(f"➕ Created interviewer '{interviewer['email']}'")

        db.commit()
        print("✅ Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
