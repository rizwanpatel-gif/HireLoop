#!/usr/bin/env python3
"""
HireLoop Development Runner
=======================

Quick development script for testing the HireLoop backend.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_dev_server():
    """Run the development server with hot reload"""
    
    print("🚀 Starting HireLoop Development Server...")
    print("📋 Hot reload enabled")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("🎯 API Endpoints: http://localhost:8000/api")
    print()
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    else:
        # Try to use the virtual environment
        venv_path = Path(".venv")
        if venv_path.exists():
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
            else:  # Unix/Linux/Mac
                python_exe = venv_path / "bin" / "python"
            
            subprocess.run([str(python_exe), "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        else:
            print("❌ No virtual environment found. Run start.py first to set up the environment.")
            sys.exit(1)

if __name__ == "__main__":
    try:
        run_dev_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Development server stopped")
    except Exception as e:
        print(f"\n🚨 Error: {e}")
        sys.exit(1)
