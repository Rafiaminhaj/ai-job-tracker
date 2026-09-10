import os
import sys

# Add project root to python path for Vercel serverless environment
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
