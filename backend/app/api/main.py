from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="PodResearch 2.0 API",
        description="Autonomous Multi-Agent YouTube Article Generator with LangChain, LangGraph, and Human-in-the-Loop Review",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API Routes
    app.include_router(router)

    return app


app = create_app()
