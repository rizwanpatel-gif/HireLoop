@echo off
echo Starting RHero Frontend...
echo ========================

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
)

REM Start the development server
echo Starting React development server on http://localhost:3000
npm start

pause
