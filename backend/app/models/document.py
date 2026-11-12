import sys
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pathlib import Path

# Ensure repository root is on sys.path for direct script execution
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "docx", "pdf"
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "primary", "reference"
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # SHA-256
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    doc_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User", back_populates="documents")
    formulary_chunks = relationship("FormularyChunk", back_populates="document", cascade="all, delete-orphan")
    prescribed_entities = relationship("PrescribedEntity", back_populates="document", cascade="all, delete-orphan")
    summary = relationship("DocumentSummary", back_populates="document", uselist=False, cascade="all, delete-orphan")
    critical_points = relationship("CriticalPoint", back_populates="document", cascade="all, delete-orphan")
