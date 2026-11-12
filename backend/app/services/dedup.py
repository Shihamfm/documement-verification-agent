import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.document import Document
from backend.app.models.job import Job
from backend.app.core.config import settings
from backend.app.core.logger import logger


class DeduplicationService:
    """Detects duplicate document uploads by same user within a configurable sliding window."""

    @staticmethod
    def compute_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 hash of document binary content."""
        return hashlib.sha256(file_bytes).hexdigest()

    @classmethod
    async def find_recent_duplicate(
        cls,
        db: AsyncSession,
        user_id: str,
        content_hash: str,
        window_minutes: Optional[int] = None
    ) -> Optional[Tuple[Document, Job]]:
        """Queries whether the user uploaded the exact same document within the time window."""
        window = window_minutes if window_minutes is not None else settings.DUPLICATE_WINDOW_MINUTES
        threshold_time = datetime.now(timezone.utc) - timedelta(minutes=window)

        stmt = (
            select(Document, Job)
            .join(Job, Job.primary_document_id == Document.id)
            .where(
                Document.user_id == user_id,
                Document.content_hash == content_hash,
                Document.created_at >= threshold_time
            )
            .order_by(Document.created_at.desc())
            .limit(1)
        )

        result = await db.execute(stmt)
        row = result.first()
        if row:
            doc, job = row
            logger.info(
                f"Duplicate upload detected for user {user_id}: "
                f"reusing existing doc={doc.id}, job={job.id} (within {window}m window)"
            )
            return doc, job

        return None
