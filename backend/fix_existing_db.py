"""
Fix existing database ID column without recreating
"""

import sqlite3
import os

def fix_existing_database():
    """Fix the existing database by modifying the ID column"""
    
    if not os.path.exists("interview_system.db"):
        print("❌ Database doesn't exist")
        return
    
    conn = sqlite3.connect("interview_system.db")
    cursor = conn.cursor()
    
    try:
        print("🔧 Fixing existing database...")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(candidates)")
        columns = cursor.fetchall()
        id_column = [col for col in columns if col[1] == 'id'][0]
        print(f"📋 Current ID column: type={id_column[2]}")
        
        if id_column[2] == 'VARCHAR(36)':
            print("🛠️ Need to fix ID column from VARCHAR to INTEGER...")
            
            # SQLite doesn't support ALTER COLUMN, so we need to:
            # 1. Create new table with correct schema
            # 2. Copy data (excluding ID, let it auto-increment)
            # 3. Drop old table and rename new one
            
            # Step 1: Create new table with correct schema
            cursor.execute("""
                CREATE TABLE candidates_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    position VARCHAR(255) NOT NULL,
                    experience_years FLOAT,
                    phone VARCHAR(50),
                    location VARCHAR(255),
                    resume_file_path VARCHAR(500),
                    resume_text TEXT,
                    portfolio_url VARCHAR(500),
                    github_url VARCHAR(500),
                    linkedin_url VARCHAR(500),
                    skills TEXT,
                    education TEXT,
                    previous_companies TEXT,
                    cover_letter TEXT,
                    preferred_salary FLOAT,
                    availability VARCHAR(255),
                    remote_preference VARCHAR(50),
                    status VARCHAR(50),
                    source VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analyzed_at DATETIME,
                    ai_analysis_status VARCHAR(50),
                    ai_overall_score FLOAT,
                    ai_technical_score FLOAT,
                    ai_experience_score FLOAT,
                    ai_cultural_fit_score FLOAT,
                    ai_analysis_results TEXT,
                    ai_model_used VARCHAR(100),
                    ai_confidence_score FLOAT,
                    matched_interviewers TEXT,
                    interview_scheduled BOOLEAN DEFAULT 0,
                    interview_datetime DATETIME,
                    interview_type VARCHAR(50),
                    recruiter_notes TEXT,
                    red_flags TEXT,
                    tags TEXT
                )
            """)
            print("✅ Created new table with correct schema")
            
            # Step 2: Copy existing data (if any) excluding the old ID
            cursor.execute("SELECT COUNT(*) FROM candidates")
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.execute("""
                    INSERT INTO candidates_new (
                        name, email, position, experience_years, phone, location,
                        resume_file_path, resume_text, portfolio_url, github_url,
                        linkedin_url, skills, education, previous_companies,
                        cover_letter, preferred_salary, availability,
                        remote_preference, status, source, created_at, updated_at,
                        analyzed_at, ai_analysis_status, ai_overall_score,
                        ai_technical_score, ai_experience_score, ai_cultural_fit_score,
                        ai_analysis_results, ai_model_used, ai_confidence_score,
                        matched_interviewers, interview_scheduled, interview_datetime,
                        interview_type, recruiter_notes, red_flags, tags
                    )
                    SELECT 
                        name, email, position, experience_years, phone, location,
                        resume_file_path, resume_text, portfolio_url, github_url,
                        linkedin_url, skills, education, previous_companies,
                        cover_letter, preferred_salary, availability,
                        remote_preference, status, source, created_at, updated_at,
                        analyzed_at, ai_analysis_status, ai_overall_score,
                        ai_technical_score, ai_experience_score, ai_cultural_fit_score,
                        ai_analysis_results, ai_model_used, ai_confidence_score,
                        matched_interviewers, interview_scheduled, interview_datetime,
                        interview_type, recruiter_notes, red_flags, tags
                    FROM candidates
                """)
                print(f"✅ Copied {count} existing records")
            
            # Step 3: Replace old table
            cursor.execute("DROP TABLE candidates")
            cursor.execute("ALTER TABLE candidates_new RENAME TO candidates")
            print("✅ Replaced old table with new one")
            
        else:
            print("✅ ID column is already correct")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(candidates)")
        columns = cursor.fetchall()
        id_column = [col for col in columns if col[1] == 'id'][0]
        print(f"✅ Fixed ID column: type={id_column[2]}, primary_key={id_column[5]}")
        
        conn.commit()
        print("🎉 Database fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_existing_database()
