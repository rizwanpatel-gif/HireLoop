"""
Create database tables for the interview system
"""

from app.models.models import Base, engine
import os

def create_tables():
    """Create all database tables"""
    
    print("🗃️ Creating database tables...")
    
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        
        # List the tables that were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📋 Created tables:")
        for table in tables:
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
