from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    document_type: str
    content_hash: str
    file_path: Optional[str] = None
    doc_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: str
    job_id: str
    filename: str
    status: str
    is_duplicate: bool = False
    message: str


class DocumentListItem(BaseModel):
    id: str
    filename: str
    file_type: str
    document_type: str
    created_at: datetime
    latest_job_id: Optional[str] = None
    latest_job_status: Optional[str] = None

    class Config:
        from_attributes = True
