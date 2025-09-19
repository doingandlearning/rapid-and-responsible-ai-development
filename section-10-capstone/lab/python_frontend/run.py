#!/usr/bin/env python3
"""
Run script for Python RAG Frontend
Provides easy startup with environment detection
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    print("🚀 Starting Python RAG Frontend")
    print("=" * 40)
    print("No Node.js required! 🎉")
    print()

def check_requirements():
    """Check if all requirements are met"""
    issues = []
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        issues.append("app.py not found - make sure you're in the python_frontend directory")
    
    # Check if virtual environment exists
    venv_path = Path('venv')
    if not venv_path.exists():
        issues.append("Virtual environment not found - run 'python setup.py' first")
    
    # Check if requirements are installed
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    try:
        result = subprocess.run([pip_cmd, 'list'], capture_output=True, text=True)
        if 'Flask' not in result.stdout:
            issues.append("Flask not installed - run 'python setup.py' first")
    except FileNotFoundError:
        issues.append("pip not found in virtual environment")
    
    return issues

def get_python_command():
    """Get the correct Python command for the platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\python"
    else:
        return "venv/bin/python"

def check_backend():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print("⚠️  Backend responded with status:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running on port 5000")
        print("   Please start your RAG backend first")
        return False
    except ImportError:
        print("⚠️  requests module not available - cannot check backend")
        return True

def run_application():
    """Run the Flask application"""
    python_cmd = get_python_command()
    
    print("🚀 Starting Flask application...")
    print("   Frontend: http://localhost:3000")
    print("   Backend:  http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        subprocess.run([python_cmd, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except FileNotFoundError:
        print(f"❌ Python not found at {python_cmd}")
        print("   Make sure virtual environment is set up correctly")
        sys.exit(1)

def main():
    """Main run function"""
    print_banner()
    
    # Check requirements
    issues = check_requirements()
    if issues:
        print("❌ Setup issues found:")
        for issue in issues:
            print(f"   • {issue}")
        print()
        print("💡 Run 'python setup.py' to fix these issues")
        sys.exit(1)
    
    # Check backend
    backend_ok = check_backend()
    if not backend_ok:
        print()
        print("⚠️  You can still start the frontend, but some features may not work")
        print("   without the backend running.")
        print()
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("👋 Exiting...")
            sys.exit(0)
    
    print()
    run_application()

if __name__ == "__main__":
    main()
