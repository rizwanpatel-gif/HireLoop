@echo off
echo.
echo ==========================================
echo  ⚛️  RHero Frontend React App
echo ==========================================
echo.

cd /d "c:\Users\Rizwan patel\OneDrive\Documents\RHero\frontend"

echo 📂 Frontend Directory: %cd%
echo.

echo 🔍 Checking Node.js installation...
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js first.
    echo 💡 Download from: https://nodejs.org/downloads
    echo 📋 Recommended: Node.js 16+ with npm
    pause
    exit /b 1
) else (
    echo ✅ Node.js found:
    node --version
    npm --version
)
echo.

echo 🔍 Checking if backend is running...
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running at http://localhost:8000
) else (
    echo ⚠️  Backend not detected!
    echo 💡 Please start the backend first using: start_backend.bat
    echo 🔄 Or run both with: start_both.bat
    echo.
    set /p "continue=Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        echo 🛑 Startup cancelled
        pause
        exit /b 1
    )
)
echo.

echo 🔍 Checking frontend dependencies...
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    echo 📋 Running npm install...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies!
        echo 💡 Try: npm cache clean --force
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully!
) else (
    echo ✅ Frontend dependencies already installed
)
echo.

echo 🔧 Checking environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 Creating .env from .env.example...
        copy .env.example .env > nul
    ) else (
        echo 📝 Creating basic .env file...
        echo REACT_APP_API_URL=http://localhost:8000 > .env
        echo REACT_APP_ENV=development >> .env
    )
    echo ✅ Environment file created!
) else (
    echo ✅ Environment file found
)
echo.

echo ⚛️  Starting RHero Frontend React App...
echo.
echo 📍 Frontend App: http://localhost:3000
echo 🔗 Backend API: http://localhost:8000
echo 📚 Backend Docs: http://localhost:8000/docs
echo.
echo 🛑 Press Ctrl+C to stop the frontend server
echo.

title RHero Frontend React App
npm start

echo.
echo 👋 RHero Frontend app stopped.
pause
