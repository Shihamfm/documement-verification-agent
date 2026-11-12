from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class VerificationResultResponse(BaseModel):
    id: str
    status: str  # "Supported", "Contradicted", "Unsupported"
    explanation: str
    parameter_matches: Dict[str, Any]
    citation_section: Optional[str] = None
    citation_monograph: Optional[str] = None
    citation_passage: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PrescribedEntityResponse(BaseModel):
    id: str
    medication_name: str
    dose: str
    unit: str
    route: str
    frequency: str
    duration: str
    indication: str
    source_section: str
    raw_attributes: Dict[str, Any]
    verification: Optional[VerificationResultResponse] = None

    class Config:
        from_attributes = True
