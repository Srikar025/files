import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_gemini_api_key():
    """Get Gemini API key from multiple sources with fallback"""
    # First, try Streamlit secrets (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except:
        pass
    
    # Second, try session state (user entered in app)
    try:
        if 'gemini_api_key' in st.session_state and st.session_state['gemini_api_key']:
            return st.session_state['gemini_api_key']
    except:
        pass
    
    # Third, try environment variable (local development)
    return os.getenv('GEMINI_API_KEY', '')

# Gemini API Configuration
GEMINI_API_KEY = get_gemini_api_key()
