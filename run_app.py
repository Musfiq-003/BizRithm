"""
BizRithm — Run App Entry Point
Run: streamlit run run_app.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the main Streamlit app
from frontend.app import main
main()
