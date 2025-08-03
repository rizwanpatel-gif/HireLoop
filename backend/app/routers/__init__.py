"""
Router modules for RHero Interview Management System
"""

from .candidates_clean import router as candidates_router
from .interviews import router as interviews_router
from .dashboard import router as dashboard_router

# Additional routers
try:
    from .calendar_api import router as calendar_router
except ImportError:
    calendar_router = None

try:
    from .smart_matching_api import router as smart_matching_router
except ImportError:
    smart_matching_router = None

try:
    from .availability_api import router as availability_router
except ImportError:
    availability_router = None

__all__ = [
    "candidates_router",
    "interviews_router", 
    "dashboard_router",
    "calendar_router",
    "smart_matching_router",
    "availability_router"
]
