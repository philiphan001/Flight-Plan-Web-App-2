import os
from pathlib import Path
import streamlit as st

def load_openai_key():
    """Load OpenAI API key from environment variable or Streamlit secrets"""
    # First try to get from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # If not in environment, try to get from Streamlit secrets
        if 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
            # Also set it as an environment variable for OpenAI library
            os.environ['OPENAI_API_KEY'] = api_key
    
    return api_key

def initialize_openai():
    """Initialize OpenAI configuration"""
    api_key = load_openai_key()
    
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY in your environment variables or Streamlit secrets.")
        return False
    
    return True 