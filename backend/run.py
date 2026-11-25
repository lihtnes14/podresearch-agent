#!/usr/bin/env python3
"""
Entry point launcher for pod_research_2 FastAPI server.
"""

import os
import sys
from pathlib import Path

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting PodResearch 2.0 Backend on http://{settings.HOST}:{settings.PORT}")
    print(f"📖 OpenAPI Swagger Docs available at http://{settings.HOST}:{settings.PORT}/docs")
    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
