@echo off
echo.
echo ==========================================
echo  🚀 RHero Backend Server
echo ==========================================
echo.

cd /d "c:\Users\Rizwan patel\OneDrive\Documents\RHero\backend"

echo 📂 Backend Directory: %cd%
echo.

echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo 💡 Download from: https://python.org/downloads
    pause
    exit /b 1
)
echo.

echo 🔍 Checking backend dependencies...
pip show fastapi uvicorn sqlalchemy > nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing backend dependencies...
    echo 📋 Installing from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies!
        echo 💡 Try: pip install --upgrade pip
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully!
) else (
    echo ✅ Backend dependencies already installed
)
echo.

echo 🔧 Checking environment configuration...
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo 📝 Creating basic .env file...
    echo # RHero Backend Configuration > .env
    echo DATABASE_URL=sqlite:///./rhero.db >> .env
    echo OPENROUTER_API_KEY=your_openrouter_api_key_here >> .env
    echo AI_MODEL=meta-llama/llama-3.1-8b-instruct:free >> .env
    echo SECRET_KEY=your-secret-key-change-in-production >> .env
    echo DEBUG=True >> .env
    echo ✅ Basic .env file created!
    echo 🔧 Please edit .env and add your API keys
) else (
    echo ✅ Environment file found
)
echo.

echo 🗄️  Initializing database...
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine); print('✅ Database initialized')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Database initialization skipped (will auto-create on startup)
)
echo.

echo 🌟 Starting RHero Backend API Server...
echo.
echo 📍 Backend API: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo 📊 Analytics: http://localhost:8000/docs#analytics
echo.
echo 🛑 Press Ctrl+C to stop the backend server
echo.

title RHero Backend Server
python main.py

echo.
echo 👋 RHero Backend server stopped.
pause
