"""Vercel Python API entry point at root api/ directory.
Properly imports the FastAPI app from backend/ with correct path setup.
"""
import sys
import os

# Add the backend directory to the path (correctly)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app

# Vercel expects the app to be named 'app'
