#!/usr/bin/env python3
"""
RHero Backend Server Startup Script
Cross-platform Python script to start the backend
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*50)
    print("🚀 RHero Backend Server")
    print("="*50)

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current: {platform.python_version()}")
        return False
    print(f"✅ Python {platform.python_version()}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - Missing")
    
    return missing

def install_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing backend dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def setup_environment():
    """Setup environment file if needed"""
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# RHero Backend Configuration
DATABASE_URL=sqlite:///./rhero.db
OPENROUTER_API_KEY=your_openrouter_api_key_here
AI_MODEL=meta-llama/llama-3.1-8b-instruct:free
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
HOST=0.0.0.0
PORT=8000
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
        print("🔧 Please edit .env and add your API keys")
    else:
        print("✅ .env file found")

def initialize_database():
    """Initialize database tables"""
    try:
        print("🗄️  Initializing database...")
        from app.core.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database init warning: {e}")
        print("📝 Database will auto-create on startup")

def start_server():
    """Start the FastAPI server"""
    print("\n🌟 Starting RHero Backend API Server...")
    print("\n📍 Backend API: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

def main():
    """Main startup function"""
    print_banner()
    
    # Change to backend directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir / 'backend'
    
    if backend_dir.exists():
        os.chdir(backend_dir)
        print(f"📂 Backend directory: {os.getcwd()}")
    else:
        print("📂 Current directory: {os.getcwd()}")
    
    # Check requirements
    if not check_python():
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n📦 Missing packages: {', '.join(missing)}")
        install = input("Install missing dependencies? (y/n): ").lower()
        if install in ['y', 'yes']:
            if not install_dependencies():
                input("Press Enter to exit...")
                return
        else:
            print("❌ Cannot start without dependencies")
            input("Press Enter to exit...")
            return
    
    # Setup environment
    setup_environment()
    
    # Initialize database
    initialize_database()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
