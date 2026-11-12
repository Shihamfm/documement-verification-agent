import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.logger import configure_logging, logger
from backend.app.db.session import init_db_schema, AsyncSessionLocal
from backend.app.db.init_db import seed_initial_data
from backend.app.api import (
    auth_router,
    documents_router,
    jobs_router,
    analysis_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    configure_logging(level=10 if settings.DEBUG else 20)
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode...")

    # 1. Initialize DB schema (tables, vector extensions)
    await init_db_schema()

    # 2. Seed initial reviewer credentials and reference formulary
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)

    yield

    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous RAG-Grounded Prescribed Medication Verification System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(jobs_router)
app.include_router(analysis_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Healthcheck endpoint for container orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER
    }


# Serve React Frontend SPA
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory="frontend/dist", check_dir=False), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(frontend_dist / "index.html")
