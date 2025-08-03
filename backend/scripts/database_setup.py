"""
Database initialization and setup script
"""
import os
from database import DatabaseManager, db_manager, get_db_session, create_tables, test_connection
from models import UserRole, create_user, create_candidate
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database(database_url: str = None):
    """Initialize the database with tables and sample data"""
    
    # Use global database manager
    if database_url:
        # Create a new database manager for specific URL
        db_mgr = DatabaseManager(database_url)
    else:
        # Use global database manager
        db_mgr = db_manager
    
    # Create all tables
    db_mgr.create_tables()
    
    # Get a session for adding sample data
    session = db_mgr.get_session()
    
    try:
        # Create sample users
        logger.info("Creating sample users...")
        
        admin_user = create_user(
            session, 
            email="admin@company.com",
            name="System Admin",
            role=UserRole.ADMIN,
            google_calendar_id="admin@company.com"
        )
        
        interviewer1 = create_user(
            session,
            email="john.doe@company.com",
            name="John Doe",
            role=UserRole.INTERVIEWER,
            google_calendar_id="john.doe@company.com"
        )
        
        interviewer2 = create_user(
            session,
            email="jane.smith@company.com",
            name="Jane Smith",
            role=UserRole.INTERVIEWER,
            google_calendar_id="jane.smith@company.com"
        )
        
        hr_user = create_user(
            session,
            email="hr@company.com",
            name="HR Manager",
            role=UserRole.HR,
            google_calendar_id="hr@company.com"
        )
        
        logger.info("✓ Sample users created")
        
        # Create sample candidates
        logger.info("Creating sample candidates...")
        
        candidate1 = create_candidate(
            session,
            name="Alice Johnson",
            email="alice.johnson@email.com",
            phone="+1-234-567-8901",
            position="Software Engineer",
            resume_text="Experienced software engineer with 5 years in Python and React...",
            skills='["Python", "React", "PostgreSQL", "Docker", "AWS"]',
            ai_score=8.5
        )
        
        candidate2 = create_candidate(
            session,
            name="Bob Wilson",
            email="bob.wilson@email.com",
            phone="+1-234-567-8902",
            position="Data Scientist",
            resume_text="Data scientist with expertise in machine learning and analytics...",
            skills='["Python", "Machine Learning", "SQL", "TensorFlow", "Pandas"]',
            ai_score=9.2
        )
        
        candidate3 = create_candidate(
            session,
            name="Carol Brown",
            email="carol.brown@email.com",
            phone="+1-234-567-8903",
            position="Frontend Developer",
            resume_text="Frontend developer specializing in modern web technologies...",
            skills='["JavaScript", "React", "Vue.js", "CSS", "HTML5"]',
            ai_score=7.8
        )
        
        logger.info("✓ Sample candidates created")
        logger.info("✓ Database initialization completed successfully!")
        
        return db_mgr
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during database initialization: {e}")
        raise
    finally:
        session.close()

# Additional utility functions for database operations
def reset_database():
    """Drop all tables and recreate them (use with caution!)"""
    logger.warning("Dropping all tables...")
    db_manager.drop_tables()
    db_manager.create_tables()

def check_database_connection():
    """Check if database connection is working"""
    return db_manager.test_connection()

if __name__ == "__main__":
    # Check database connection first
    if not check_database_connection():
        logger.error("Failed to connect to database. Exiting...")
        exit(1)
    
    # Initialize with default database
    db_mgr = init_database()
    logger.info(f"\nDatabase file created: {db_mgr.database_url}")
    logger.info("You can now use the database models in your application!")
    
    # Example of using the session management
    logger.info("\nTesting session management...")
    with db_mgr.get_db_context() as db:
        from models import User
        user_count = db.query(User).count()
        logger.info(f"Total users in database: {user_count}")
