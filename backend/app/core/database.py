"""
Database connection and session management module
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database connection and session management class
    """
    
    def __init__(self, database_url: str = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL. If None, uses environment variable
        """
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
        self._engine = None
        self._session_factory = None
        
    @property
    def engine(self):
        """Get or create database engine"""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine
    
    @property
    def session_factory(self):
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._session_factory
    
    def _create_engine(self):
        """Create database engine with proper configuration"""
        connect_args = {}
        
        # SQLite specific configurations
        if self.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            
        # PostgreSQL specific configurations
        elif self.database_url.startswith("postgresql"):
            connect_args["connect_timeout"] = 10
            
        engine = create_engine(
            self.database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            connect_args=connect_args
        )
        
        logger.info(f"Database engine created for: {self.database_url}")
        return engine
    
    def create_tables(self):
        """Create all database tables"""
        from models import Base
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("✓ All tables created successfully")
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        from models import Base
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("✓ All tables dropped")
    
    def get_session(self) -> Session:
        """
        Get a database session for direct use
        Remember to close the session when done
        
        Returns:
            Session: SQLAlchemy session object
        """
        return self.session_factory()
    
    def get_db_dependency(self) -> Generator[Session, None, None]:
        """
        Dependency function for FastAPI/Flask applications
        
        Yields:
            Session: SQLAlchemy session object
        """
        db = self.get_session()
        try:
            yield db
        except Exception as e:
            db.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            db.close()
    
    @contextmanager
    def get_db_context(self):
        """
        Context manager for database sessions
        
        Usage:
            with db_manager.get_db_context() as db:
                users = db.query(User).all()
        """
        db = self.get_session()
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            db.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("✓ Database connection test successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_table_info(self):
        """Get information about database tables"""
        from models import Base
        tables = Base.metadata.tables.keys()
        logger.info(f"Available tables: {list(tables)}")
        return tables
    
    def execute_raw_sql(self, sql: str, params: dict = None):
        """
        Execute raw SQL query
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql), params or {})
                return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"Raw SQL execution failed: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def get_db() -> Generator[Session, None, None]:
    """Global get_db dependency function"""
    yield from db_manager.get_db_dependency()

def get_db_session() -> Session:
    """Global get_db_session function"""
    return db_manager.get_session()

def create_tables():
    """Global create_tables function"""
    db_manager.create_tables()

def test_connection() -> bool:
    """Global test_connection function"""
    return db_manager.test_connection()

# Export the engine and session factory for direct access
engine = db_manager.engine
SessionLocal = db_manager.session_factory
