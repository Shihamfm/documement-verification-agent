import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pathlib import Path
import sys

# Ensure repository root is on sys.path for direct script execution
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.db.base import Base


class DocumentSummary(Base):
    __tablename__ = "document_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    clinical_highlights: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    document = relationship("Document", back_populates="summary")


class CriticalPoint(Base):
    __tablename__ = "critical_points"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    point_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # "timing_critical", "duration_limit", "urgent_adverse_effect", "abrupt_cessation_warning", "follow_up"
    severity: Mapped[str] = mapped_column(String(50), nullable=False)  # "High", "Medium", "Low"
    source_quote: Mapped[str] = mapped_column(Text, nullable=False)
    rank_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    document = relationship("Document", back_populates="critical_points")
