@echo off
echo.
echo ==========================================
echo  🚀 RHero Full Stack Application
echo ==========================================
echo.

echo 🎯 Starting both Backend and Frontend...
echo.

echo [1/2] 🚀 Starting Backend Server...
start "RHero Backend" cmd /k "cd /d \"%~dp0\" && start_backend.bat"

echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak > nul

echo 🔍 Checking if backend started successfully...
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running successfully!
) else (
    echo ⚠️  Backend may still be starting...
)

echo.
echo [2/2] ⚛️  Starting Frontend React App...
start "RHero Frontend" cmd /k "cd /d \"%~dp0\" && start_frontend.bat"

echo.
echo ✅ Both servers are starting in separate windows:
echo.
echo 📊 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo ⚛️  Frontend App: http://localhost:3000
echo.
echo 💡 You can close this window - servers will keep running
echo 🛑 To stop servers: Close the Backend and Frontend windows
echo.

pause
