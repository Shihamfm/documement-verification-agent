from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class JobStageResponse(BaseModel):
    id: str
    stage_name: str
    order: int
    status: str  # pending, in_progress, completed, failed
    duration_seconds: float
    stage_metadata: Dict[str, Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: str
    user_id: str
    primary_document_id: str
    reference_document_id: str
    status: str  # pending, processing, completed, failed
    current_stage: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    stages: List[JobStageResponse] = []

    class Config:
        from_attributes = True


class JobEvent(BaseModel):
    job_id: str
    current_stage: str
    status: str
    progress_percentage: int
    stage: Optional[JobStageResponse] = None
    error_message: Optional[str] = None
    timestamp: str
