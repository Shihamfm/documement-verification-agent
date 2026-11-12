import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pathlib import Path
import sys

# Ensure repository root is on sys.path for direct script execution
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.db.base import Base


class PrescribedEntity(Base):
    __tablename__ = "prescribed_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    medication_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    dose: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    route: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    indication: Mapped[str] = mapped_column(String(255), nullable=False)
    source_section: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    document = relationship("Document", back_populates="prescribed_entities")
    verification_result = relationship("VerificationResult", back_populates="entity", uselist=False, cascade="all, delete-orphan")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("prescribed_entities.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # "Supported", "Contradicted", "Unsupported"
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    parameter_matches: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    citation_section: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    citation_monograph: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    citation_passage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    entity = relationship("PrescribedEntity", back_populates="verification_result")
