from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pathlib import Path
import sys

# Ensure repository root is on sys.path for direct script execution
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from backend.app.schemas.entity import PrescribedEntityResponse


class CriticalPointResponse(BaseModel):
    id: str
    point_text: str
    category: str
    severity: str
    source_quote: str
    rank_order: int

    class Config:
        from_attributes = True


class DocumentSummaryResponse(BaseModel):
    id: str
    executive_summary: str
    clinical_highlights: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentAnalysisResponse(BaseModel):
    document_id: str
    filename: str
    patient_info: Dict[str, Any]
    summary: Optional[DocumentSummaryResponse] = None
    critical_points: List[CriticalPointResponse] = []
    prescribed_entities: List[PrescribedEntityResponse] = []
    raw_text: str
    sections: Dict[str, str] = {}
    total_medications: int = 0
    supported_count: int = 0
    contradicted_count: int = 0
    unsupported_count: int = 0
