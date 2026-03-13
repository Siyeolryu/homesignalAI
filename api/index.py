"""
Vercel Serverless Function Entry Point

FastAPI application entrypoint for Vercel.
The actual app is defined in src/main.py and configured in pyproject.toml.

See: https://vercel.com/docs/frameworks/backend/fastapi
"""
import sys
from pathlib import Path

# Add project root to Python path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

# Import the FastAPI app instance from src.main
from src.main import app

# Export for Vercel (required)
__all__ = ["app"]
