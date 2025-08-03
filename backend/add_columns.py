"""
Add missing columns to existing database
"""

import sqlite3
import os

# Connect to existing database
db_file = "interview_system.db"
if not os.path.exists(db_file):
    print("❌ Database doesn't exist yet")
    exit(1)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    # Check what columns exist
    cursor.execute("PRAGMA table_info(candidates)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Existing columns: {existing_columns}")
    
    # Add missing columns if they don't exist
    if 'skills' not in existing_columns:
        cursor.execute("ALTER TABLE candidates ADD COLUMN skills TEXT")
        print("✅ Added 'skills' column")
    else:
        print("✅ 'skills' column already exists")
    
    if 'resume_text' not in existing_columns:
        cursor.execute("ALTER TABLE candidates ADD COLUMN resume_text TEXT")
        print("✅ Added 'resume_text' column")
    else:
        print("✅ 'resume_text' column already exists")
    
    conn.commit()
    print("🎉 Database updated successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
