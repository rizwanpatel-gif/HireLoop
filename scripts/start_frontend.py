#!/usr/bin/env python3
"""
RHero Frontend React App Startup Script
Cross-platform Python script to start the frontend
"""

import os
import sys
import subprocess
import platform
import time
import requests
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*50)
    print("⚛️  RHero Frontend React App")
    print("="*50)

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            node_version = result.stdout.strip()
            print(f"✅ Node.js {node_version}")
            
            npm_result = subprocess.run(['npm', '--version'], 
                                      capture_output=True, text=True)
            if npm_result.returncode == 0:
                npm_version = npm_result.stdout.strip()
                print(f"✅ npm {npm_version}")
                return True
        
        return False
    except FileNotFoundError:
        print("❌ Node.js not found!")
        print("💡 Download from: https://nodejs.org/downloads")
        print("📋 Recommended: Node.js 16+ with npm")
        return False

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running at http://localhost:8000")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("⚠️  Backend not detected!")
    print("💡 Please start the backend first:")
    print("   - Windows: start_backend.bat")
    print("   - Cross-platform: python start_backend.py")
    print("🔄 Or run both: python start_both.py")
    
    continue_anyway = input("\nContinue anyway? (y/n): ").lower()
    return continue_anyway in ['y', 'yes']

def check_dependencies():
    """Check if npm dependencies are installed"""
    node_modules = Path('node_modules')
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.check_call(['npm', 'install'])
            print("✅ Dependencies installed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            print("💡 Try: npm cache clean --force")
            return False
    else:
        print("✅ Frontend dependencies found")
        return True

def setup_environment():
    """Setup environment file if needed"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env from .env.example...")
            env_file.write_text(env_example.read_text())
        else:
            print("📝 Creating basic .env file...")
            env_content = """REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
"""
            env_file.write_text(env_content)
        print("✅ Environment file created!")
    else:
        print("✅ Environment file found")

def start_frontend():
    """Start the React development server"""
    print("\n⚛️  Starting RHero Frontend React App...")
    print("\n📍 Frontend App: http://localhost:3000")
    print("🔗 Backend API: http://localhost:8000")
    print("📚 Backend Docs: http://localhost:8000/docs")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(['npm', 'start'])
    except KeyboardInterrupt:
        print("\n👋 Frontend app stopped by user")
    except Exception as e:
        print(f"\n❌ Frontend error: {e}")

def main():
    """Main startup function"""
    print_banner()
    
    # Change to frontend directory
    script_dir = Path(__file__).parent
    frontend_dir = script_dir / 'frontend'
    
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        print(f"📂 Frontend directory: {os.getcwd()}")
    else:
        print("📂 Current directory: {os.getcwd()}")
    
    # Check requirements
    if not check_node():
        input("Press Enter to exit...")
        return
    
    # Check backend
    if not check_backend():
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Setup environment
    setup_environment()
    
    # Start frontend
    start_frontend()

if __name__ == "__main__":
    main()
