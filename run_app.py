#!/usr/bin/env python3
"""
Simple script to run the Kolam Art Studio application
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import google.generativeai
        import PIL
        import numpy
        import matplotlib
        import cv2
        import plotly
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if Gemini API key is configured"""
    from config import GEMINI_API_KEY
    if GEMINI_API_KEY:
        print("✅ Gemini API key is configured!")
        return True
    else:
        print("⚠️ Gemini API key not found.")
        print("Set GEMINI_API_KEY environment variable or configure it in the app settings.")
        return False

def run_app():
    """Run the Streamlit application"""
    print("🚀 Starting Kolam Art Studio...")
    print("📱 Open your browser to http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎨 Kolam Art Studio Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check API key (optional)
    check_api_key()
    
    print("\n" + "=" * 50)
    
    # Run the application
    run_app()

if __name__ == "__main__":
    main()
