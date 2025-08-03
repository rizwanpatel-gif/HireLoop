@echo off
echo Starting RHero Backend Server...
echo ================================

cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-multipart

REM Start the server
echo Starting FastAPI server on http://localhost:8000
python main.py

pause
