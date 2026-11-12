import os
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.job import Job, JobStage
from backend.app.schemas.document import DocumentUploadResponse, DocumentListItem, DocumentResponse
from backend.app.api.dependencies import get_current_user
from backend.app.services.parser import DocumentParser
from backend.app.services.dedup import DeduplicationService
from backend.app.services.pipeline import AsyncPipelineEngine, PIPELINE_STAGES
from backend.app.core.config import settings
from backend.app.core.logger import logger

router = APIRouter(prefix="/api/documents", tags=["Documents"])


async def ensure_reference_document(db: AsyncSession, user_id: str) -> Document:
    """Ensures an authoritative reference document exists in the system."""
    stmt = select(Document).where(Document.document_type == "reference").limit(1)
    ref_doc = (await db.execute(stmt)).scalar_one_or_none()
    if ref_doc:
        return ref_doc

    ref_path = Path("data/source_documents/reference_document_medical.docx")
    if not ref_path.exists():
        ref_path = Path("reference_documents/reference_document_medical.docx")

    if not ref_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System reference document is missing from data/source_documents."
        )

    content_bytes = ref_path.read_bytes()
    content_hash = DeduplicationService.compute_hash(content_bytes)
    raw_text, _ = DocumentParser.parse_docx(content_bytes)

    ref_doc = Document(
        user_id=user_id,
        filename="Meridian_Bay_Formulary_Digest_Rev8.2.docx",
        file_type="docx",
        document_type="reference",
        content_hash=content_hash,
        raw_text=raw_text,
        file_path=str(ref_path),
        doc_metadata={"digest_name": "Meridian Bay Institutional Formulary", "revision": "8.2"}
    )
    db.add(ref_doc)
    await db.flush()
    return ref_doc


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    reference_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ingests a primary clinical discharge summary (DOCX or PDF), validates format,

    checks for duplicates, commits initial records in an atomic transaction,
    and enqueues the verification pipeline asynchronously.
    """
    filename = file.filename or "uploaded_document"
    ext = Path(filename).suffix.lower().replace(".", "")
    if ext not in ("docx", "pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only .docx and .pdf files are accepted."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    content_hash = DeduplicationService.compute_hash(file_bytes)

    # -------------------------------------------------------------
    # Extra Credit: Duplicate Upload Detection (5-minute window)
    # -------------------------------------------------------------
    dup = await DeduplicationService.find_recent_duplicate(
        db=db,
        user_id=current_user.id,
        content_hash=content_hash,
        window_minutes=settings.DUPLICATE_WINDOW_MINUTES
    )
    if dup:
        existing_doc, existing_job = dup
        return DocumentUploadResponse(
            document_id=existing_doc.id,
            job_id=existing_job.id,
            filename=existing_doc.filename,
            status=existing_job.status,
            is_duplicate=True,
            message="Identical document uploaded within the deduplication window. Returning existing analysis."
        )

    # Parse primary document text
    try:
        parsed_data = DocumentParser.parse(file_bytes, ext)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Document parsing error: {str(e)}")

    # Save physical copy to storage directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{uuid.uuid4()}_{filename}"
    saved_path = upload_dir / saved_filename
    saved_path.write_bytes(file_bytes)

    # -------------------------------------------------------------
    # Atomic Transaction: Create Document, Job, and 7 Stages
    # -------------------------------------------------------------
    try:
        # Resolve reference document
        if reference_id:
            ref_doc = await db.get(Document, reference_id)
            if not ref_doc:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified reference document not found.")
        else:
            ref_doc = await ensure_reference_document(db, current_user.id)

        # 1. Primary Document Record
        primary_doc = Document(
            user_id=current_user.id,
            filename=filename,
            file_type=ext,
            document_type="primary",
            content_hash=content_hash,
            raw_text=parsed_data["raw_text"],
            file_path=str(saved_path),
            doc_metadata={
                "patient_info": parsed_data["patient_info"],
                "sections": list(parsed_data["sections"].keys())
            }
        )
        db.add(primary_doc)
        await db.flush()

        # 2. Asynchronous Job Record
        job = Job(
            user_id=current_user.id,
            primary_document_id=primary_doc.id,
            reference_document_id=ref_doc.id,
            status="pending",
            current_stage="pending"
        )
        db.add(job)
        await db.flush()

        # 3. Pre-create the 7 granular pipeline stages
        for idx, (stage_name, desc, _) in enumerate(PIPELINE_STAGES):
            stage = JobStage(
                job_id=job.id,
                stage_name=stage_name,
                order=idx + 1,
                status="pending",
                stage_metadata={"description": desc}
            )
            db.add(stage)

        # Commit transaction atomically
        await db.commit()
        await db.refresh(job)

    except Exception as e:
        await db.rollback()
        # Clean up disk file on database failure
        if saved_path.exists():
            saved_path.unlink()
        logger.error(f"Atomic upload creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction failed during upload registration: {str(e)}"
        )

    # -------------------------------------------------------------
    # Asynchronous non-blocking pipeline trigger
    # -------------------------------------------------------------
    asyncio.create_task(AsyncPipelineEngine.run_pipeline(job.id))

    return DocumentUploadResponse(
        document_id=primary_doc.id,
        job_id=job.id,
        filename=filename,
        status="pending",
        is_duplicate=False,
        message="Document uploaded successfully. Processing pipeline initialized."
    )


@router.get("/", response_model=List[DocumentListItem])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all primary documents belonging to the authenticated user."""
    stmt = (
        select(Document)
        .where(Document.user_id == current_user.id, Document.document_type == "primary")
        .order_by(Document.created_at.desc())
    )
    docs = (await db.execute(stmt)).scalars().all()

    items = []
    for doc in docs:
        # Get latest job
        job_stmt = (
            select(Job)
            .where(Job.primary_document_id == doc.id)
            .order_by(Job.created_at.desc())
            .limit(1)
        )
        job = (await db.execute(job_stmt)).scalar_one_or_none()

        items.append(
            DocumentListItem(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                document_type=doc.document_type,
                created_at=doc.created_at,
                latest_job_id=job.id if job else None,
                latest_job_status=job.status if job else None
            )
        )
    return items


@router.get("/references", response_model=List[DocumentResponse])
async def list_reference_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists available reference formulary documents."""
    # Ensure default reference document exists
    await ensure_reference_document(db, current_user.id)
    await db.commit()

    stmt = select(Document).where(Document.document_type == "reference")
    refs = (await db.execute(stmt)).scalars().all()
    return refs


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetches metadata for a specific document with tenant isolation check."""
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Allow access if document is reference or owned by user
    if doc.document_type != "reference" and doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view this document."
        )

    return doc
