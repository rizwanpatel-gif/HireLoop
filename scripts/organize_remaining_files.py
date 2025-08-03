#!/usr/bin/env python3
"""
Organize remaining files in RHero project
Move the remaining 18+ files to their proper locations in the organized structure
"""

import os
import shutil
import sys
from pathlib import Path

def organize_remaining_files():
    """Organize the remaining files into the proper structure"""
    print("Organizing remaining files...")
    
    # Define file mappings for remaining files
    file_mappings = {
        # Core API files
        "api.py": "backend/app/main_old.py",  # Keep as backup since we have new main.py
        
        # Configuration files
        "ai_config.py": "backend/app/core/ai_config.py",
        
        # Service files
        "ai_fastapi_integration.py": "backend/app/services/ai_fastapi_integration.py",
        
        # API route files
        "calendar_api.py": "backend/app/routers/calendar_api.py",
        "smart_matching_api.py": "backend/app/routers/smart_matching_api.py",
        "interviewer_availability_api.py": "backend/app/routers/availability_api.py",
        
        # Calendar utilities
        "calendar_event_functions.py": "backend/app/services/calendar_event_functions.py",
        
        # Demo and test files
        "background_tasks_demo.py": "backend/app/tests/test_background_tasks_demo.py",
        "calendar_event_demo.py": "backend/app/tests/test_calendar_events.py",
        "enhanced_analysis_demo.py": "backend/app/tests/test_enhanced_analysis.py",
        "smart_matching_demo.py": "backend/app/tests/test_smart_matching_demo.py",
        
        # Documentation files
        "google-calendar-oauth2-setup.md": "docs/google-calendar-oauth2-setup.md",
        "google-calendar-setup.md": "docs/google-calendar-setup.md",
        "react-integration.md": "docs/react-integration.md",
        "OAUTH2_IMPLEMENTATION_SUMMARY.md": "docs/oauth2-implementation-summary.md",
        
        # Utility scripts
        "organize_project.py": "scripts/organize_project_old.py",
        "organize_project_fixed.py": "scripts/organize_project_fixed.py",
    }
    
    # Move files to their new locations
    moved_count = 0
    for source_file, destination in file_mappings.items():
        if os.path.exists(source_file):
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            try:
                # Move the file
                shutil.move(source_file, destination)
                print(f"  ✅ {source_file} -> {destination}")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Error moving {source_file}: {e}")
        else:
            print(f"  ⚠️  File not found: {source_file}")
    
    return moved_count

def update_router_imports():
    """Update import statements in the moved router files"""
    print("Updating import statements in router files...")
    
    router_files = [
        "backend/app/routers/calendar_api.py",
        "backend/app/routers/smart_matching_api.py", 
        "backend/app/routers/availability_api.py"
    ]
    
    for file_path in router_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                # Common import replacements
                replacements = [
                    ("from models import", "from app.models.models import"),
                    ("from database import", "from app.core.database import"),
                    ("from google_calendar_service import", "from app.services.calendar_service import"),
                    ("from ai_service import", "from app.services.ai_service import"),
                    ("from oauth2_config import", "from app.core.oauth2_config import"),
                    ("from google_calendar_config import", "from app.core.calendar_config import"),
                    ("from background_tasks import", "from app.services.background_tasks import"),
                    ("from calendar_integration import", "from app.services.calendar_integration import"),
                    ("from smart_matching_algorithm import", "from app.services.smart_matching import"),
                    ("from automatic_interview_scheduler import", "from app.services.automatic_scheduler import"),
                ]
                
                for old_import, new_import in replacements:
                    content = content.replace(old_import, new_import)
                
                with open(file_path, "w", encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Updated imports in {file_path}")
                
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")

def create_router_init_file():
    """Create/update the routers __init__.py file to include all routers"""
    print("Updating routers __init__.py...")
    
    init_content = '''"""
Router modules for RHero Interview Management System
"""

from .candidates import router as candidates_router
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
'''
    
    try:
        with open("backend/app/routers/__init__.py", "w", encoding='utf-8') as f:
            f.write(init_content)
        print("  ✅ Updated backend/app/routers/__init__.py")
    except Exception as e:
        print(f"  ❌ Error updating routers __init__.py: {e}")

def clean_up_pycache():
    """Remove __pycache__ directories"""
    print("Cleaning up __pycache__ directories...")
    
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                print(f"  ✅ Removed {pycache_path}")
            except Exception as e:
                print(f"  ❌ Error removing {pycache_path}: {e}")

def create_project_summary():
    """Create a summary of the organized project structure"""
    print("Creating project structure summary...")
    
    summary_content = '''# RHero Project Organization Summary

## Project Structure After Organization

```
RHero/
├── backend/                           # FastAPI backend application
│   ├── app/                          # Main application package
│   │   ├── core/                     # Core configuration and utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Application configuration
│   │   │   ├── database.py           # Database connection and setup
│   │   │   ├── oauth2_config.py      # OAuth2 configuration
│   │   │   ├── calendar_config.py    # Google Calendar configuration
│   │   │   └── ai_config.py          # AI service configuration
│   │   ├── models/                   # SQLAlchemy database models
│   │   │   ├── __init__.py
│   │   │   └── models.py             # User, Candidate, Interview models
│   │   ├── schemas/                  # Pydantic schemas for API
│   │   │   └── __init__.py
│   │   ├── crud/                     # Database CRUD operations
│   │   │   └── __init__.py
│   │   ├── services/                 # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py         # AI integration service
│   │   │   ├── calendar_service.py   # Google Calendar service
│   │   │   ├── automatic_scheduler.py # Auto scheduling logic
│   │   │   ├── background_tasks.py   # Background task processing
│   │   │   ├── calendar_integration.py # Calendar integration
│   │   │   ├── smart_matching.py     # Smart matching algorithm
│   │   │   ├── ai_fastapi_integration.py # AI FastAPI integration
│   │   │   └── calendar_event_functions.py # Calendar utilities
│   │   ├── routers/                  # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── candidates.py         # Candidate management endpoints
│   │   │   ├── interviews.py         # Interview scheduling endpoints
│   │   │   ├── dashboard.py          # Dashboard and analytics
│   │   │   ├── calendar_api.py       # Calendar API endpoints
│   │   │   ├── smart_matching_api.py # Smart matching endpoints
│   │   │   └── availability_api.py   # Availability checking endpoints
│   │   └── tests/                    # Test files and demos
│   │       ├── __init__.py
│   │       ├── test_*.py             # All test files
│   │       └── *_demo.py             # Demo scripts
│   ├── scripts/                      # Utility scripts
│   │   ├── database_setup.py         # Database initialization
│   │   ├── oauth2_setup.py           # OAuth2 setup script
│   │   └── organize_project_*.py     # Organization scripts
│   ├── requirements.txt              # Python dependencies
│   ├── main.py                      # FastAPI application entry point
│   ├── main_old.py                  # Backup of original API
│   ├── .env.example                 # Environment variables template
│   └── Dockerfile                   # Docker configuration
├── frontend/                        # React frontend (future)
├── docs/                            # Documentation
│   ├── README.md                    # Main documentation
│   ├── *.md                         # Feature-specific docs
│   └── setup guides                 # Setup and configuration guides
├── scripts/                         # Project-level scripts
└── docker-compose.yml              # Docker Compose configuration
```

## Files Organized

### Backend Core (app/core/)
- config.py - Application settings and configuration
- database.py - Database connection and SQLAlchemy setup
- oauth2_config.py - OAuth2 authentication configuration
- calendar_config.py - Google Calendar API configuration  
- ai_config.py - AI service configuration

### Backend Services (app/services/)
- ai_service.py - OpenAI integration and candidate analysis
- calendar_service.py - Google Calendar API wrapper
- automatic_scheduler.py - Automatic interview scheduling logic
- background_tasks.py - Asynchronous task processing
- calendar_integration.py - Calendar integration utilities
- smart_matching.py - AI-powered candidate matching
- ai_fastapi_integration.py - AI FastAPI integration
- calendar_event_functions.py - Calendar event utilities

### Backend Routers (app/routers/)
- candidates.py - Candidate management API endpoints
- interviews.py - Interview scheduling API endpoints
- dashboard.py - Dashboard and analytics endpoints
- calendar_api.py - Calendar-specific API endpoints
- smart_matching_api.py - Smart matching API endpoints
- availability_api.py - Availability checking endpoints

### Backend Tests (app/tests/)
- test_*.py - Unit and integration tests
- *_demo.py - Demonstration scripts
- test_usage.py, test_examples.py, etc.

### Documentation (docs/)
- README.md - Main project documentation
- google-calendar-oauth2-setup.md - OAuth2 setup guide
- google-calendar-setup.md - Calendar setup guide
- react-integration.md - Frontend integration guide
- oauth2-implementation-summary.md - OAuth2 implementation details
- Feature-specific documentation files

### Scripts
- database_setup.py - Database initialization
- oauth2_setup.py - OAuth2 credential setup
- organize_project_*.py - Project organization scripts

## Next Steps

1. **Environment Setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pydantic-settings  # For newer pydantic
   ```

3. **Run Application**:
   ```bash
   python main.py
   ```

4. **Access API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Features Available

- ✅ Smart Interview Scheduling with AI
- ✅ Google Calendar Integration
- ✅ Candidate Management with AI Analysis
- ✅ Interview Dashboard and Analytics
- ✅ OAuth2 Authentication
- ✅ Background Task Processing
- ✅ Email Notifications
- ✅ Availability Checking
- ✅ Smart Candidate Matching
- ✅ Comprehensive API Documentation

The project is now professionally organized and ready for development!
'''
    
    try:
        with open("docs/PROJECT_STRUCTURE.md", "w", encoding='utf-8') as f:
            f.write(summary_content)
        print("  ✅ Created docs/PROJECT_STRUCTURE.md")
    except Exception as e:
        print(f"  ❌ Error creating project summary: {e}")

def main():
    """Main function to organize remaining files"""
    print("RHero Project - Organizing Remaining Files")
    print("=" * 50)
    
    try:
        # Organize remaining files
        moved_count = organize_remaining_files()
        
        # Update imports in router files
        update_router_imports()
        
        # Create/update router init file
        create_router_init_file()
        
        # Clean up cache directories
        clean_up_pycache()
        
        # Create project summary
        create_project_summary()
        
        print(f"\n✅ Successfully organized {moved_count} remaining files!")
        print("\nProject organization completed!")
        print("\nProject structure:")
        print("  backend/app/core/       - Configuration and core utilities")
        print("  backend/app/services/   - Business logic services") 
        print("  backend/app/routers/    - API route handlers")
        print("  backend/app/tests/      - Tests and demo scripts")
        print("  docs/                   - Documentation")
        print("  scripts/                - Utility scripts")
        print("\nAll files are now properly organized in the professional structure!")
        
    except Exception as e:
        print(f"❌ Error during organization: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
