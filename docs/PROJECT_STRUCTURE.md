# RHero Project Structure

## 📁 Directory Organization

### `/backend/` - FastAPI Backend Application
- **`/app/`** - Main application code
  - **`/core/`** - Core functionality (database, config, etc.)
  - **`/models/`** - SQLAlchemy database models  
  - **`/routers/`** - FastAPI route handlers
  - **`/services/`** - Business logic and external services
  - **`/schemas/`** - Pydantic models for API
  - **`/crud/`** - Database operations
  - **`/tests/`** - Backend tests
- **`requirements.txt`** - Python dependencies
- **`main.py`** - FastAPI application entry point
- **`.env`** - Environment variables

### `/frontend/` - React Frontend Application  
- **`/src/`** - React source code
- **`/public/`** - Static assets
- **`package.json`** - Node.js dependencies

### `/docs/` - Documentation
- **`/guides/`** - Implementation guides and documentation
- **`/api/`** - API documentation

### `/scripts/` - Utility Scripts
- Startup scripts for frontend/backend
- Setup and deployment scripts  
- Test scripts

### `/examples/` - Demo and Example Code
- Demo implementations
- Usage examples
- Proof of concept code

### `/config/` - Configuration Files
- Service configuration files
- Setup configurations

### `/archived/` - Legacy/Duplicate Files
- Old implementations
- Duplicate files
- Files moved during cleanup

## 🚀 Quick Start

1. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\Activate
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend  
   npm install
   npm start
   ```

3. **Both Together:**
   ```bash
   # Use the startup scripts in /scripts/
   scripts\start_both.bat
   ```

## 🔧 Key Files

- **`smart_matching_algorithm.py`** - Core matching algorithm
- **`requirements.txt`** - Root Python dependencies  
- **`README.md`** - Main project documentation
- **`HOW_TO_RUN.md`** - Running instructions
- **`SEPARATE_STARTUP_GUIDE.md`** - Detailed startup guide

## 📝 Notes

- All empty files have been cleaned up
- Duplicate files moved to `/archived/`
- Development dependencies are in respective directories
- Environment variables configured in backend/.env
