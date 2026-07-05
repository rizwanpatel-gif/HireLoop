#!/usr/bin/env python3
"""
Database migration to add current_round column to candidates table
"""
import sqlite3
import os

def migrate_database():
    """Add current_round column to candidates table"""
    database_path = os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
    
    # Remove sqlite:/// prefix if present
    if database_path.startswith("sqlite:///"):
        database_path = database_path[10:]
    
    print(f"Migrating database: {database_path}")
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Check if current_round column already exists
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'current_round' not in columns:
            print("Adding current_round column...")
            cursor.execute("ALTER TABLE candidates ADD COLUMN current_round INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Successfully added current_round column")
        else:
            print("✅ current_round column already exists")
        
        # Update existing candidates to have current_round = 1 if they have interview_datetime
        cursor.execute("""
            UPDATE candidates 
            SET current_round = 1 
            WHERE interview_datetime IS NOT NULL AND current_round = 0
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        if updated_count > 0:
            print(f"✅ Updated {updated_count} candidates with interview_datetime to round 1")
        
        conn.close()
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate_database()
