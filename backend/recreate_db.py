"""
Recreate database with updated Candidate model
"""

import os
from sqlalchemy import create_engine
from app.models.models import Base

# Remove existing database
db_file = "interview_system.db"
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ Removed existing database: {db_file}")

# Create new database with updated schema
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Created new database with updated schema")
print("📋 New fields added to Candidate model:")
print("   - skills (Text)")
print("   - resume_text (Text)")
print("🚀 Database is ready for candidate creation!")
