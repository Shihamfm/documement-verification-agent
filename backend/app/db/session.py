import os
import sys
from pathlib import Path
from typing import AsyncGenerator

# Ensure repository root is on sys.path for direct script execution
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.db.base import Base



# Determine database engine URL
_db_url = settings.DATABASE_URL
_is_sqlite = False

# Ensure data directory exists
if settings.SQLITE_FALLBACK and (
    "localhost" in _db_url or "127.0.0.1" in _db_url or "sqlite" in _db_url
):
    db_file = Path(settings.SQLITE_DB_PATH)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    if os.getenv("FORCE_POSTGRES") != "true":
        # On Windows, SQLite URLs require forward slashes
        clean_path = db_file.resolve().as_posix()
        _db_url = f"sqlite+aiosqlite:///{clean_path}"
        _is_sqlite = True
        logger.info(f"Using SQLite async database at {clean_path}")

engine = create_async_engine(
    _db_url,
    echo=False,
    future=True,
    **({"connect_args": {"check_same_thread": False}} if _is_sqlite else {})
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db_schema() -> None:
    """Create all tables on application startup."""
    # Ensure all models are registered with Base.metadata
    from backend.app.models import (
        User, Document, Job, JobStage, FormularyChunk,
        PrescribedEntity, VerificationResult, DocumentSummary, CriticalPoint
    )
    
    async with engine.begin() as conn:
        if not _is_sqlite:
            try:
                from sqlalchemy import text
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            except Exception as e:
                logger.warning(f"Could not enable pgvector: {e}")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")


