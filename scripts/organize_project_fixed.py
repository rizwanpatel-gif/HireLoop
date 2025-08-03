#!/usr/bin/env python3
"""
RHero Project Organization Script
Reorganizes the project into a professional folder structure
"""

import os
import shutil
import sys
from pathlib import Path

def create_directory_structure():
    """Create the organized directory structure"""
    print("Creating organized directory structure...")
    
    directories = [
        "backend/",
        "backend/app/",
        "backend/app/models/",
        "backend/app/schemas/",
        "backend/app/crud/",
        "backend/app/core/",
        "backend/app/services/",
        "backend/app/routers/",
        "backend/app/tests/",
        "backend/scripts/",
        "backend/alembic/",
        "frontend/",
        "frontend/src/",
        "frontend/src/components/",
        "frontend/src/pages/",
        "frontend/src/services/",
        "frontend/src/utils/",
        "frontend/public/",
        "docs/",
        "scripts/",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}")
    
    # Create __init__.py files
    init_files = [
        "backend/app/__init__.py",
        "backend/app/models/__init__.py",
        "backend/app/schemas/__init__.py",
        "backend/app/crud/__init__.py",
        "backend/app/core/__init__.py",
        "backend/app/services/__init__.py",
        "backend/app/routers/__init__.py",
        "backend/app/tests/__init__.py",
    ]
    
    for init_file in init_files:
        with open(init_file, "w", encoding='utf-8') as f:
            f.write("")
        print(f"  Created: {init_file}")

def move_files():
    """Move files to their new organized locations"""
    print("Moving files to organized structure...")
    
    file_mappings = {
        # Core models and database
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
        
        # API Routes
        "candidate_management_api.py": "backend/app/routers/candidates.py",
        "interview_scheduling_api.py": "backend/app/routers/interviews.py",
        "interview_dashboard_api.py": "backend/app/routers/dashboard.py",
        
        # Configuration
        "requirements.txt": "backend/requirements.txt",
        ".env.example": "backend/.env.example",
        
        # Tests and demos
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
        
        # Scripts
        "oauth2_setup.py": "backend/scripts/oauth2_setup.py",
        
        # Documentation
        "README.md": "docs/README.md",
        "AI_INTEGRATION_GUIDE.md": "docs/ai-integration-guide.md",
        "CANDIDATE_MANAGEMENT_README.md": "docs/candidate-management.md",
        "INTERVIEW_SCHEDULING_README.md": "docs/interview-scheduling.md",
        "BACKGROUND_TASKS_README.md": "docs/background-tasks.md",
        "SMART_MATCHING_README.md": "docs/smart-matching.md",
    }
    
    for source_file, destination in file_mappings.items():
        if os.path.exists(source_file):
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Move the file
            shutil.move(source_file, destination)
            print(f"  {source_file} -> {destination}")

def create_main_application():
    """Create the main FastAPI application file"""
    print("Creating main application file...")
    
    main_content = '''"""
RHero Interview Management System
Main FastAPI Application

Features:
- Smart Interview Scheduling
- Calendar Integration (Google Calendar)
- AI-Powered Candidate Analysis
- Interview Dashboard & Analytics
- OAuth2 Authentication
- Email Notifications
- Background Task Processing
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import candidates, interviews, dashboard

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="RHero Interview Management System",
    description="Comprehensive interview scheduling and candidate management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to RHero Interview Management System!",
        "docs": "/docs",
        "health": "OK"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RHero API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
'''

    with open("backend/main.py", "w", encoding='utf-8') as f:
        f.write(main_content)

def create_config_file():
    """Create the configuration file"""
    print("Creating configuration file...")
    
    config_content = '''"""
Configuration settings for RHero Interview Management System
"""

import os
from pathlib import Path
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "RHero Interview Management System"
    debug: bool = False
    
    # Database Settings
    database_url: str = "sqlite:///./rhero.db"
    
    # Google Calendar API Settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    
    # OpenAI API Settings
    openai_api_key: str = ""
    
    # Email Settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Business Logic Settings
    interview_duration_minutes: int = 60
    business_hours_start: int = 9  # 9 AM
    business_hours_end: int = 18   # 6 PM
    
    class Config:
        env_file = ".env"

settings = Settings()
'''

    with open("backend/app/core/config.py", "w", encoding='utf-8') as f:
        f.write(config_content)

def create_docker_files():
    """Create Docker configuration files"""
    print("Creating Docker configuration...")
    
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
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

    with open("backend/Dockerfile", "w", encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    # docker-compose.yml
    docker_compose_content = '''version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./rhero.db
    volumes:
      - ./backend:/app
      - ./data:/app/data
    restart: unless-stopped

  # Uncomment to add PostgreSQL database
  # db:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: rhero
  #     POSTGRES_USER: postgres
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
'''

    with open("docker-compose.yml", "w", encoding='utf-8') as f:
        f.write(docker_compose_content)

def create_environment_file():
    """Create environment configuration file"""
    print("Creating environment configuration...")
    
    env_content = '''# RHero Interview Management System Environment Configuration

# Application Settings
APP_NAME=RHero Interview Management System
DEBUG=True

# Database Settings (SQLite for development, PostgreSQL for production)
DATABASE_URL=sqlite:///./rhero.db
# For PostgreSQL: DATABASE_URL=postgresql://username:password@localhost/rhero

# Google Calendar API Settings (Get these from Google Cloud Console)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# OpenAI API Settings (Get from OpenAI Dashboard)
OPENAI_API_KEY=your_openai_api_key_here

# Email Settings (For notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Security Settings (Change these in production!)
SECRET_KEY=your-very-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Business Logic Settings
INTERVIEW_DURATION_MINUTES=60
BUSINESS_HOURS_START=9
BUSINESS_HOURS_END=18
'''

    with open("backend/.env.example", "w", encoding='utf-8') as f:
        f.write(env_content)

def create_readme():
    """Create comprehensive README file"""
    print("Creating README file...")
    
    readme_content = '''# RHero Interview Management System

A comprehensive interview scheduling and candidate management platform built with FastAPI, featuring AI-powered candidate analysis and smart scheduling.

## Features

- **Smart Interview Scheduling**: Automatic scheduling with availability checking
- **Calendar Integration**: Google Calendar integration for seamless scheduling
- **AI-Powered Analysis**: Intelligent candidate evaluation and matching
- **Interview Dashboard**: Comprehensive dashboard with analytics
- **OAuth2 Authentication**: Secure authentication system
- **Email Notifications**: Automated notifications for all stakeholders
- **Background Tasks**: Asynchronous task processing

## Project Structure

```
RHero/
├── backend/                    # FastAPI backend application
│   ├── app/                   # Main application package
│   │   ├── core/             # Core configuration and database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── crud/             # Database operations
│   │   ├── services/         # Business logic services
│   │   ├── routers/          # API route handlers
│   │   └── tests/            # Test files
│   ├── scripts/              # Utility scripts
│   ├── requirements.txt      # Python dependencies
│   ├── main.py              # FastAPI application entry point
│   └── Dockerfile           # Docker configuration
├── frontend/                  # React frontend (future)
├── docs/                     # Documentation
├── scripts/                  # Project scripts
└── docker-compose.yml       # Docker Compose configuration
```

## Quick Start

### 1. Clone and Setup

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Run the Application

```bash
# Development server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

### 4. Access the Application

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
cd backend
docker build -t rhero-backend .
docker run -p 8000:8000 rhero-backend
```

## API Endpoints

### Candidates
- `GET /api/candidates/` - List all candidates
- `POST /api/candidates/` - Create new candidate
- `GET /api/candidates/{id}` - Get specific candidate
- `GET /api/availability/{interviewer_id}` - Check interviewer availability

### Interviews
- `GET /api/interviews/` - List all interviews
- `POST /api/interviews/` - Schedule new interview
- `POST /api/interviews/automatic-schedule` - Automatic scheduling
- `PUT /api/interviews/{id}/status` - Update interview status

### Dashboard
- `GET /api/dashboard/overview` - Dashboard overview
- `GET /api/dashboard/interviews` - Interview analytics
- `GET /api/dashboard/filters` - Available filters

## Configuration

### Required API Keys

1. **Google Calendar API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable Calendar API
   - Create OAuth2 credentials
   - Add credentials to `.env`

2. **OpenAI API**:
   - Get API key from [OpenAI Dashboard](https://platform.openai.com)
   - Add to `.env` file

3. **Email Configuration**:
   - Configure SMTP settings for notifications
   - Use app passwords for Gmail

## Development

### Running Tests

```bash
cd backend
python -m pytest app/tests/
```

### Adding New Features

1. **Models**: Add to `app/models/`
2. **Schemas**: Add to `app/schemas/`
3. **Services**: Add business logic to `app/services/`
4. **Routes**: Add API endpoints to `app/routers/`
5. **Tests**: Add tests to `app/tests/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
'''

    with open("docs/README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)

def update_imports():
    """Update import statements in moved files"""
    print("Updating import statements...")
    
    # Files that need import updates
    import_updates = {
        "backend/app/routers/candidates.py": [
            ("from models import", "from app.models.models import"),
            ("from database import", "from app.core.database import"),
            ("from google_calendar_service import", "from app.services.calendar_service import"),
            ("from ai_service import", "from app.services.ai_service import"),
        ],
        "backend/app/routers/interviews.py": [
            ("from models import", "from app.models.models import"),
            ("from database import", "from app.core.database import"),
            ("from automatic_interview_scheduler import", "from app.services.automatic_scheduler import"),
        ],
        "backend/app/routers/dashboard.py": [
            ("from models import", "from app.models.models import"),
            ("from database import", "from app.core.database import"),
        ],
    }
    
    for file_path, replacements in import_updates.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                for old_import, new_import in replacements:
                    content = content.replace(old_import, new_import)
                
                with open(file_path, "w", encoding='utf-8') as f:
                    f.write(content)
                print(f"  Updated imports in {file_path}")
            except Exception as e:
                print(f"  Warning: Could not update imports in {file_path}: {e}")

def main():
    """Main organization function"""
    print("RHero Project Organization")
    print("=" * 50)
    print("This will organize your project into a professional structure")
    
    try:
        # Create directory structure
        create_directory_structure()
        
        # Move files
        move_files()
        
        # Create new configuration files
        create_main_application()
        create_config_file()
        create_docker_files()
        create_environment_file()
        create_readme()
        
        # Update import statements
        update_imports()
        
        print("\nProject organization completed successfully!")
        print("\nNext steps:")
        print("1. cd backend")
        print("2. cp .env.example .env")
        print("3. Edit .env with your API keys")
        print("4. pip install -r requirements.txt")
        print("5. python main.py")
        print("\nAPI will be available at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"ERROR: Organization failed")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
