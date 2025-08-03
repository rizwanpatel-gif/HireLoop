#!/usr/bin/env python3
"""
Quick Start Script for RHero Interview Management System
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", platform.python_version())
        return False
    print(f"✅ Python {platform.python_version()} - Compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['fastapi', 'uvicorn', 'SQLAlchemy', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False

def check_env_file():
    """Check if .env file exists and has basic configuration"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("📝 Creating basic .env file...")
        create_basic_env_file()
    else:
        print("✅ .env file found")

def create_basic_env_file():
    """Create a basic .env file with comments"""
    env_content = """# RHero Interview Management System Environment Variables

# Database Settings (SQLite by default)
DATABASE_URL=sqlite:///./rhero.db

# OpenRouter API (Free AI Models) - Get from: https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
AI_MODEL=meta-llama/llama-3.1-8b-instruct:free

# Google Calendar API (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Email Settings (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Security Settings
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Basic .env file created!")
    print("🔧 Please edit .env file and add your API keys")

def start_server():
    """Start the RHero server"""
    print("\n🚀 Starting RHero Interview Management System...")
    print("📍 Server URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n\n👋 RHero server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    """Main function to start RHero"""
    print("🎯 RHero Interview Management System - Quick Start")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"📂 Changed to directory: {os.getcwd()}")
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check .env file
    check_env_file()
    
    # Check dependencies
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        install_choice = input("🤔 Install missing dependencies? (y/n): ").lower()
        
        if install_choice in ['y', 'yes']:
            if not install_dependencies():
                input("Press Enter to exit...")
                return
        else:
            print("❌ Cannot start without dependencies!")
            input("Press Enter to exit...")
            return
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
