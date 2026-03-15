"""Vercel API entry point for FastAPI app."""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel expects the app to be named 'app'
# This file serves as the entry point for Vercel's Python runtime