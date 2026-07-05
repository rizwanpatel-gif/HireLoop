#!/usr/bin/env python3
"""
Database migration to add the AI-agent hiring pipeline schema:
- job_roles table (JD per open role)
- users.experience_years / users.expertise_areas (interviewer assignment)
- candidates.job_role_id (link candidate -> role)
- chat_messages table (HR <-> agent chat history)
"""
import sqlite3
import os


def _db_path() -> str:
    database_url = os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
    if database_url.startswith("sqlite:///"):
        return database_url[10:]
    return database_url


def migrate_database():
    database_path = _db_path()
    print(f"Migrating database: {database_path}")

    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # job_roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                department VARCHAR(255),
                jd_text TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ job_roles table ready")

        # chat_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                candidate_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ chat_messages table ready")

        # users additions
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [c[1] for c in cursor.fetchall()]
        if 'experience_years' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN experience_years REAL")
            print("✅ Added users.experience_years")
        else:
            print("✅ users.experience_years already exists")
        if 'expertise_areas' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN expertise_areas TEXT")
            print("✅ Added users.expertise_areas")
        else:
            print("✅ users.expertise_areas already exists")

        # candidates additions
        cursor.execute("PRAGMA table_info(candidates)")
        candidate_columns = [c[1] for c in cursor.fetchall()]
        if 'job_role_id' not in candidate_columns:
            cursor.execute("ALTER TABLE candidates ADD COLUMN job_role_id INTEGER")
            print("✅ Added candidates.job_role_id")
        else:
            print("✅ candidates.job_role_id already exists")

        conn.commit()
        conn.close()
        print("✅ Database migration completed successfully")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    return True


if __name__ == "__main__":
    migrate_database()
