"""
Candidate Management API Components
Re-exports from the candidates router to avoid import issues
"""

# Import everything from the existing candidates module
from app.routers.candidates import (
    CandidateDB, 
    AnalysisTaskDB,
    CandidateStatus,
    AnalysisStatus
)

# Import database components
from app.core.database import Base, get_db, SessionLocal

# Export everything that might be needed
__all__ = [
    "CandidateDB",
    "AnalysisTaskDB", 
    "Base",
    "get_db",
    "SessionLocal",
    "CandidateStatus",
    "AnalysisStatus"
]
