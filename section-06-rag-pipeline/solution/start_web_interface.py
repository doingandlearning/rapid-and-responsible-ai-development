#!/usr/bin/env python3
"""
Standalone script to start the RAG web interface.
This provides an easy way to start the web interface without running all tests.
"""

import sys
import os

# Add the current directory to the path so we can import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lab6_rag_pipeline import start_web_interface

def main():
    """Start the web interface with default settings."""
    print("🌐 Edinburgh University RAG Pipeline - Web Interface")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  Warning: OPENAI_API_KEY not set or using placeholder value")
        print("   The web interface will work but won't generate AI responses")
        print("   Set your API key: export OPENAI_API_KEY='your-actual-key'")
        print()
    
    try:
        # Start the web interface
        start_web_interface(port=5100, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 Web interface stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
