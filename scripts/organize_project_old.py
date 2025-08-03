"""
RHero Project Organization Script
================================

This script reorganizes the RHero project into a clean, professional structure:
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── crud/
│   ├── core/
│   ├── services/
│   ├── routers/
│   └── tests/
├── scripts/
├── requirements.txt
└── .env.example
"""

import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create the organized directory structure"""
    
    print("🏗️ Creating organized directory structure...")
    
    # Define the directory structure
    directories = [
        "backend",
        "backend/app",
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/crud",
        "backend/app/core",
        "backend/app/services",
        "backend/app/routers",
        "backend/app/tests",
        "backend/scripts",
        "backend/alembic",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "frontend/src/utils",
        "frontend/public",
        "docs",
        "scripts"
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}/")
    
    # Create __init__.py files
    init_files = [
        "backend/app/__init__.py",
        "backend/app/models/__init__.py",
        "backend/app/schemas/__init__.py",
        "backend/app/crud/__init__.py",
        "backend/app/core/__init__.py",
        "backend/app/services/__init__.py",
        "backend/app/routers/__init__.py",
        "backend/app/tests/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"  ✅ Created: {init_file}")

def move_files_to_structure():
    """Move existing files to the new structure"""
    
    print("\n📁 Moving files to organized structure...")
    
    # File mappings: old_path -> new_path
    file_mappings = {
        # Core application files
        "models.py": "backend/app/models/models.py",
        "database.py": "backend/app/core/database.py",
        "database_setup.py": "backend/scripts/database_setup.py",
        
        # Services
        "google_calendar_service.py": "backend/app/services/calendar_service.py",
        "ai_service.py": "backend/app/services/ai_service.py",
        "oauth2_config.py": "backend/app/core/oauth2_config.py",
        "google_calendar_config.py": "backend/app/core/calendar_config.py",
        "background_tasks.py": "backend/app/services/background_tasks.py",
        "calendar_integration.py": "backend/app/services/calendar_integration.py",
        "smart_matching_algorithm.py": "backend/app/services/smart_matching.py",
        "automatic_interview_scheduler.py": "backend/app/services/automatic_scheduler.py",
        
        # API routes
        "candidate_management_api.py": "backend/app/routers/candidates.py",
        "interview_scheduling_api.py": "backend/app/routers/interviews.py",
        "interview_dashboard_api.py": "backend/app/routers/dashboard.py",
        
        # Configuration
        "requirements.txt": "backend/requirements.txt",
        ".env.example": "backend/.env.example",
        
        # Test files
        "usage_example.py": "backend/app/tests/test_usage.py",
        "example_usage.py": "backend/app/tests/test_examples.py",
        "ai_integration_demo.py": "backend/app/tests/test_ai_integration.py",
        "candidate_management_demo.py": "backend/app/tests/test_candidate_management.py",
        "interview_scheduling_demo.py": "backend/app/tests/test_interview_scheduling.py",
        "oauth2_demo.py": "backend/app/tests/test_oauth2.py",
        "test_calendar_integration.py": "backend/app/tests/test_calendar_integration.py",
        "dashboard_demo.py": "backend/app/tests/test_dashboard.py",
        "automatic_scheduling_demo.py": "backend/app/tests/test_automatic_scheduling.py",
        "test_automatic_scheduling.py": "backend/app/tests/test_automatic_scheduling_unit.py",
        "availability_demo.py": "backend/app/tests/test_availability.py",
        
        # Setup scripts
        "oauth2_setup.py": "backend/scripts/oauth2_setup.py",
        
        # Documentation
        "README.md": "docs/README.md",
        "AI_INTEGRATION_GUIDE.md": "docs/ai-integration-guide.md",
        "CANDIDATE_MANAGEMENT_README.md": "docs/candidate-management.md",
        "INTERVIEW_SCHEDULING_README.md": "docs/interview-scheduling.md",
        "BACKGROUND_TASKS_README.md": "docs/background-tasks.md",
        "SMART_MATCHING_README.md": "docs/smart-matching.md"
    }
    
    # Move files
    for old_path, new_path in file_mappings.items():
        if os.path.exists(old_path):
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                shutil.move(old_path, new_path)
                print(f"  ✅ {old_path} → {new_path}")
            except Exception as e:
                print(f"  ❌ Error moving {old_path}: {e}")
        else:
            print(f"  ⚠️  {old_path} not found, skipping...")

def create_main_application():
    """Create the main FastAPI application file"""
    
    print("\n🚀 Creating main application file...")
    
    main_content = '''"""
RHero Interview Scheduling System
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .core.database import create_tables, engine
from .routers import candidates, interviews, dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="RHero Interview Scheduling API",
        description="Comprehensive AI-powered interview scheduling system",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # CORS middleware for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(candidates.router, prefix="/api", tags=["Candidates"])
    app.include_router(interviews.router, prefix="/api", tags=["Interviews"])
    app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup"""
        logger.info("🚀 Starting RHero Interview Scheduling API...")
        
        # Create database tables
        create_tables()
        logger.info("✅ Database tables created/verified")
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "RHero Interview Scheduling API",
            "version": "1.0.0",
            "docs": "/api/docs"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "RHero Interview Scheduling API",
            "version": "1.0.0"
        }
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting RHero Interview Scheduling API...")
    print("📖 API Documentation: http://localhost:8000/api/docs")
    print("🗄️ Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''
    
    with open("backend/app/main.py", "w") as f:
        f.write(main_content)
    
    print("  ✅ Created: backend/app/main.py")

def create_core_config():
    """Create core configuration file"""
    
    print("\n⚙️ Creating core configuration...")
    
    config_content = '''"""
Application Configuration Settings
"""
import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///rhero_interview_system.db")
    
    # Google Calendar
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_CALENDAR_API_KEY: Optional[str] = os.getenv("GOOGLE_CALENDAR_API_KEY")
    
    # OpenRouter AI
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    AI_MODEL: str = os.getenv("AI_MODEL", "anthropic/claude-3-haiku")
    
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # File paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CREDENTIALS_DIR: Path = BASE_DIR / "credentials"
    TOKENS_DIR: Path = BASE_DIR / "tokens"
    
    def __init__(self):
        # Create necessary directories
        self.CREDENTIALS_DIR.mkdir(exist_ok=True)
        self.TOKENS_DIR.mkdir(exist_ok=True)

settings = Settings()
'''
    
    with open("backend/app/core/config.py", "w") as f:
        f.write(config_content)
    
    print("  ✅ Created: backend/app/core/config.py")

def create_router_init_files():
    """Create router initialization files"""
    
    print("\n🛣️ Creating router files...")
    
    # Create router __init__.py files with proper imports
    routers_init = '''"""
API Router Modules
"""
from .candidates import router as candidates_router
from .interviews import router as interviews_router
from .dashboard import router as dashboard_router

__all__ = ["candidates_router", "interviews_router", "dashboard_router"]
'''
    
    with open("backend/app/routers/__init__.py", "w") as f:
        f.write(routers_init)
    
    print("  ✅ Updated: backend/app/routers/__init__.py")

def create_services_init():
    """Create services initialization file"""
    
    services_init = '''"""
Business Logic Services
"""
from .calendar_service import GoogleCalendarService
from .ai_service import AIService
from .background_tasks import *
from .smart_matching import SmartMatchingAlgorithm

__all__ = [
    "GoogleCalendarService",
    "AIService", 
    "SmartMatchingAlgorithm"
]
'''
    
    with open("backend/app/services/__init__.py", "w") as f:
        f.write(services_init)
    
    print("  ✅ Updated: backend/app/services/__init__.py")

def create_docker_files():
    """Create Docker configuration files"""
    
    print("\n🐳 Creating Docker configuration...")
    
    # Dockerfile
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p credentials tokens

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    with open("backend/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # Docker Compose
    docker_compose_content = '''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://rhero:password@db:5432/rhero_interview
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./credentials:/app/credentials
      - ./tokens:/app/tokens
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=rhero
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=rhero_interview
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
'''
    
    with open("backend/docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    print("  ✅ Created: backend/Dockerfile")
    print("  ✅ Created: backend/docker-compose.yml")

def create_frontend_structure():
    """Create basic frontend structure"""
    
    print("\n🎨 Creating frontend structure...")
    
    package_json = '''{
  "name": "rhero-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.3.0",
    "react-scripts": "5.0.1",
    "axios": "^1.4.0",
    "date-fns": "^2.29.3",
    "@mui/material": "^5.13.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
'''
    
    with open("frontend/package.json", "w") as f:
        f.write(package_json)
    
    print("  ✅ Created: frontend/package.json")

def create_updated_readme():
    """Create an updated README for the organized project"""
    
    print("\n📚 Creating updated README...")
    
    readme_content = '''# RHero Interview Scheduling System

A comprehensive AI-powered interview scheduling system with Google Calendar integration and intelligent candidate matching.

## 📂 Project Structure

```
RHero/
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── models/                    # SQLAlchemy database models
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── crud/                      # Database CRUD operations
│   │   ├── core/                      # Core configuration and utilities
│   │   │   ├── config.py              # Application settings
│   │   │   ├── database.py            # Database connection
│   │   │   ├── oauth2_config.py       # OAuth2 configuration
│   │   │   └── calendar_config.py     # Calendar configuration
│   │   ├── services/                  # Business logic services
│   │   │   ├── calendar_service.py    # Google Calendar integration
│   │   │   ├── ai_service.py          # AI analysis service
│   │   │   ├── background_tasks.py    # Background task processing
│   │   │   ├── smart_matching.py      # AI matching algorithm
│   │   │   └── automatic_scheduler.py # Automatic scheduling
│   │   ├── routers/                   # API route handlers
│   │   │   ├── candidates.py          # Candidate management
│   │   │   ├── interviews.py          # Interview scheduling
│   │   │   └── dashboard.py           # Dashboard endpoints
│   │   └── tests/                     # Test files
│   ├── scripts/                       # Utility scripts
│   │   ├── database_setup.py          # Database initialization
│   │   └── oauth2_setup.py            # OAuth2 setup
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment variables template
│   ├── Dockerfile                     # Docker configuration
│   └── docker-compose.yml             # Multi-container setup
├── frontend/                          # React Frontend (future)
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/                              # Documentation
└── scripts/                           # Project management scripts
```

## 🚀 Quick Start

### Method 1: Direct Start

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/database_setup.py

# Start the API
python -m app.main
```

### Method 2: Docker

```bash
cd backend

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
```

## 🔧 Configuration

Edit `backend/.env` with your API keys:

```bash
# Database
DATABASE_URL=sqlite:///rhero_interview_system.db

# Google Calendar API
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key

# OpenRouter AI
OPENROUTER_API_KEY=your_openrouter_api_key
AI_MODEL=anthropic/claude-3-haiku

# Application
SECRET_KEY=your_secret_key
DEBUG=True

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@company.com
EMAIL_PASSWORD=your_email_password
```

## 📚 API Endpoints

Once running, access:

- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **Candidate Management**: http://localhost:8000/api/candidates/
- **Interview Dashboard**: http://localhost:8000/api/interviews/
- **Calendar Availability**: http://localhost:8000/api/availability/

## 🧪 Testing

```bash
cd backend

# Run specific tests
python app/tests/test_candidate_management.py
python app/tests/test_interview_scheduling.py
python app/tests/test_ai_integration.py

# Run dashboard tests
python app/tests/test_dashboard.py
```

## 🏗️ Architecture

### Core Features

- **Candidate Management**: Complete candidate lifecycle management
- **AI Analysis**: Automated candidate evaluation and scoring
- **Smart Matching**: AI-powered interviewer matching
- **Calendar Integration**: Google Calendar with OAuth2
- **Automatic Scheduling**: End-to-end interview scheduling
- **Dashboard**: Comprehensive interview management dashboard

### Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **AI**: OpenRouter API (Claude, GPT models)
- **Calendar**: Google Calendar API with OAuth2
- **Frontend**: React (prepared structure)
- **Deployment**: Docker, Docker Compose

## 🔄 Migration from Old Structure

If you have an existing installation, the old files have been automatically organized. Key changes:

- Main API moved to `backend/app/main.py`
- Services organized in `backend/app/services/`
- Routes organized in `backend/app/routers/`
- Tests moved to `backend/app/tests/`
- Documentation moved to `docs/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
'''
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("  ✅ Created: README.md")

def print_completion_summary():
    """Print completion summary with next steps"""
    
    print("\n" + "="*60)
    print("🎉 PROJECT ORGANIZATION COMPLETE!")
    print("="*60)
    
    print("\n📂 New Project Structure Created:")
    print("   ✅ backend/app/ - Main application code")
    print("   ✅ backend/app/services/ - Business logic")
    print("   ✅ backend/app/routers/ - API endpoints")
    print("   ✅ backend/app/core/ - Configuration")
    print("   ✅ backend/app/tests/ - Test files")
    print("   ✅ backend/scripts/ - Utility scripts")
    print("   ✅ docs/ - Documentation")
    print("   ✅ frontend/ - React frontend structure")
    
    print("\n🚀 Quick Start Commands:")
    print("   cd backend")
    print("   pip install -r requirements.txt")
    print("   cp .env.example .env")
    print("   # Edit .env with your API keys")
    print("   python scripts/database_setup.py")
    print("   python -m app.main")
    
    print("\n🌐 Access Points:")
    print("   📖 API Docs: http://localhost:8000/api/docs")
    print("   🏥 Health: http://localhost:8000/health")
    print("   👥 Candidates: http://localhost:8000/api/candidates/")
    print("   📊 Dashboard: http://localhost:8000/api/interviews/")
    
    print("\n🐳 Docker Alternative:")
    print("   cd backend")
    print("   docker-compose up -d")
    
    print("\n💡 Next Steps:")
    print("   1. Configure your API keys in backend/.env")
    print("   2. Start the backend API")
    print("   3. Test the endpoints using the API docs")
    print("   4. Run the test files to verify functionality")
    
    print("\n" + "="*60)

def main():
    """Main organization function"""
    
    print("🏗️ RHero Project Organization")
    print("=" * 50)
    print("This will organize your project into a professional structure")
    print()
    
    try:
        # Step 1: Create directory structure
        create_directory_structure()
        
        # Step 2: Move existing files
        move_files_to_structure()
        
        # Step 3: Create main application
        create_main_application()
        
        # Step 4: Create core configuration
        create_core_config()
        
        # Step 5: Create router init files
        create_router_init_files()
        
        # Step 6: Create services init
        create_services_init()
        
        # Step 7: Create Docker files
        create_docker_files()
        
        # Step 8: Create frontend structure
        create_frontend_structure()
        
        # Step 9: Create updated README
        create_updated_readme()
        
        # Step 10: Print completion summary
        print_completion_summary()
        
    except Exception as e:
        print(f"\n❌ Error during organization: {e}")
        logger.exception("Organization failed")

if __name__ == "__main__":
    main()
