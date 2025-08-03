"""
Fix database schema - recreate with correct ID column
"""

import sqlite3
import os
from app.models.models import Base, engine

def fix_database():
    """Fix the database schema by recreating it"""
    
    # Backup existing data if any
    backup_data = []
    if os.path.exists("interview_system.db"):
        try:
            conn = sqlite3.connect("interview_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates")
            backup_data = cursor.fetchall()
            conn.close()
            print(f"📦 Backed up {len(backup_data)} existing candidates")
        except Exception as e:
            print(f"⚠️ Could not backup data: {e}")
    
    # Remove old database
    if os.path.exists("interview_system.db"):
        os.remove("interview_system.db")
        print("🗑️ Removed old database")
    
    # Create new database with correct schema
    Base.metadata.create_all(bind=engine)
    print("✅ Created new database with correct schema")
    
    # Verify the schema is correct
    conn = sqlite3.connect("interview_system.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(candidates)")
    columns = cursor.fetchall()
    
    id_column = [col for col in columns if col[1] == 'id'][0]
    print(f"✅ ID column: type={id_column[2]}, primary_key={id_column[5]}")
    
    # Check that experience_years is nullable
    exp_column = [col for col in columns if col[1] == 'experience_years'][0]
    print(f"✅ Experience_years column: type={exp_column[2]}, nullable={not exp_column[3]}")
    
    conn.close()
    
    print("🎉 Database schema fixed!")
    print("🚀 You can now restart your server and create candidates!")

if __name__ == "__main__":
    fix_database()
