import streamlit as st
import os
import sys

# Extensive debug logging
print("Python version:", sys.version)
print("Starting Streamlit app...")
print("Current working directory:", os.getcwd())
print("Directory contents:", os.listdir())
print("Environment variables:", dict(os.environ))

try:
    # Basic app
    st.set_page_config(page_title="Test App", layout="wide")
    print("Page config set successfully")

    st.write("Debug: App initialization started")
    st.title("Test App")
    st.write("Debug: Title rendered")
    st.write("Hello World!")
    print("App rendered successfully")

except Exception as e:
    print("Error during app initialization:", str(e))
    print("Error type:", type(e).__name__)
    import traceback
    print("Traceback:", traceback.format_exc())