"""
API module.
"""

from app.api.routes import router
from app.api.main import create_app

__all__ = ["router", "create_app"]
