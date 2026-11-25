import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.api.routes import router as api_router
from backend.api.schemas import HealthResponse
from backend.memory.database import Base, engine

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite database tables are created
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="PodResearch Agent API",
    description="Autonomous Multi-Agent Podcast Research & Journalism System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)


@app.get("/", response_model=HealthResponse, tags=["Health"])
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="ok",
        app="PodResearch Agent API",
        version="1.0.0"
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "true").lower() == "true"

    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)

