import uuid
from typing import Dict, Any, Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pathlib import Path
import sys

# Ensure repository root is on sys.path for direct script execution
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.db.base import Base


class FormularyChunk(Base):
    __tablename__ = "formulary_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    monograph_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    section_number: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "I", "II"
    section_title: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "Cardiovascular Agents"
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Store embedding as JSON vector (works universally across PostgreSQL and SQLite)
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    document = relationship("Document", back_populates="formulary_chunks")
