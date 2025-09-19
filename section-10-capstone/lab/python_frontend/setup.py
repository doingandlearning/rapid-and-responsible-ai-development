#!/usr/bin/env python3
"""
Setup script for Python RAG Frontend
Makes it easy to get started without Node.js
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("🐍 Python RAG Frontend Setup")
    print("=" * 40)
    print("No Node.js required! 🎉")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip is not available")
        print("   Please install pip first")
        return False

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    if os.path.exists('venv'):
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_activation_command():
    """Get the correct activation command for the platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine pip command
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    try:
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    env_content = """# Python RAG Frontend Configuration
API_BASE=http://localhost:5000/api
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=uploads
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_uploads_directory():
    """Create uploads directory"""
    if os.path.exists('uploads'):
        print("✅ uploads directory already exists")
        return True
    
    print("📁 Creating uploads directory...")
    try:
        os.makedirs('uploads', exist_ok=True)
        print("✅ uploads directory created")
        return True
    except Exception as e:
        print(f"❌ Failed to create uploads directory: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    activation_cmd = get_activation_command()
    
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("Next steps:")
    print()
    print("1. Activate the virtual environment:")
    print(f"   {activation_cmd}")
    print()
    print("2. Make sure your RAG backend is running on port 5000")
    print()
    print("3. Start the frontend:")
    print("   python app.py")
    print()
    print("4. Open your browser:")
    print("   http://localhost:3000")
    print()
    print("📚 For more information, see README.md")
    print()
    print("🐍 Happy coding!")

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Setup steps
    steps = [
        create_virtual_environment,
        install_dependencies,
        create_env_file,
        create_uploads_directory
    ]
    
    for step in steps:
        if not step():
            print(f"\n❌ Setup failed at step: {step.__name__}")
            sys.exit(1)
    
    print_next_steps()

if __name__ == "__main__":
    main()
