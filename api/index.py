"""Vercel Python API entry point at root api/ directory.
Forward to the actual backend entry point in backend/api/
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.api.index import app

# Vercel expects the app to be named 'app'
# This file just forwards from root api/ to backend/api/
