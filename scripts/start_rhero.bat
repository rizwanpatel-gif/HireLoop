@echo off
echo 🚀 Starting RHero Interview Management System...
echo.

cd /d "c:\Users\Rizwan patel\OneDrive\Documents\RHero\backend"

echo 📂 Current directory: %cd%
echo.

echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo.
echo 🔍 Checking if dependencies are installed...
pip show fastapi uvicorn SQLAlchemy > nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
) else (
    echo ✅ Dependencies already installed
)

echo.
echo 🌟 Starting RHero API Server...
echo.
echo 📍 Server will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

echo.
echo 👋 RHero server stopped.
pause
