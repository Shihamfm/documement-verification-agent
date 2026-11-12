import pytest
import io
import asyncio
import time
import httpx
from pathlib import Path
from backend.app.models.user import User
from backend.app.models.job import Job, JobStage
from backend.app.models.summary import DocumentSummary, CriticalPoint
from backend.app.models.entity import PrescribedEntity
from backend.app.services.pipeline import AsyncPipelineEngine
from sqlalchemy import select
from sqlalchemy.orm import selectinload


@pytest.mark.asyncio
async def test_non_blocking_upload_endpoint(
    client: httpx.AsyncClient,
    test_user: User,
    auth_headers: dict,
    indexed_reference_doc
):
    """Asserts that upload endpoint returns immediately (< 250ms) without blocking on pipeline execution."""
    doc_path = Path("data/source_documents/primary_document_medical.docx")
    file_bytes = doc_path.read_bytes()

    start_time = time.time()
    files = {"file": ("non_blocking_test.docx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    resp = await client.post("/api/documents/upload", headers=auth_headers, files=files)
    elapsed = time.time() - start_time

    assert resp.status_code == 202
    assert elapsed < 0.5  # Returns immediately
    data = resp.json()
    assert "job_id" in data
    assert "document_id" in data


@pytest.mark.asyncio
async def test_complete_async_pipeline_execution(
    db_session,
    test_user: User,
    indexed_reference_doc
):
    """Asserts that all 7 pipeline stages complete successfully with telemetry timings."""
    doc_path = Path("data/source_documents/primary_document_medical.docx")
    from backend.app.services.parser import DocumentParser
    from backend.app.services.dedup import DeduplicationService
    from backend.app.models.document import Document
    from backend.app.services.pipeline import PIPELINE_STAGES

    file_bytes = doc_path.read_bytes()
    parsed = DocumentParser.parse(file_bytes, "docx")
    content_hash = DeduplicationService.compute_hash(file_bytes)

    doc = Document(
        user_id=test_user.id,
        filename="pipeline_test.docx",
        file_type="docx",
        document_type="primary",
        content_hash=content_hash,
        raw_text=parsed["raw_text"],
        file_path=str(doc_path),
        doc_metadata={"patient_info": parsed["patient_info"]}
    )
    db_session.add(doc)
    await db_session.flush()

    job = Job(
        user_id=test_user.id,
        primary_document_id=doc.id,
        reference_document_id=indexed_reference_doc.id,
        status="pending",
        current_stage="pending"
    )
    db_session.add(job)
    await db_session.flush()

    for idx, (stage_name, desc, _) in enumerate(PIPELINE_STAGES):
        db_session.add(JobStage(job_id=job.id, stage_name=stage_name, order=idx+1, status="pending", stage_metadata={"desc": desc}))
    await db_session.commit()

    # Execute pipeline using test session factory
    from tests.conftest import TestSessionLocal
    await AsyncPipelineEngine.run_pipeline(job.id, session_factory=TestSessionLocal)

    # Validate final job state (refresh from database to clear identity map cache)
    await db_session.refresh(job)
    assert job.status == "completed"
    assert job.current_stage == "done"
    assert job.completed_at is not None

    # Validate stages
    stages = (await db_session.execute(select(JobStage).where(JobStage.job_id == job.id).order_by(JobStage.order))).scalars().all()
    assert len(stages) == 7
    for s in stages:
        assert s.status == "completed"
        assert s.duration_seconds >= 0

    # Validate extracted entities
    entities = (await db_session.execute(select(PrescribedEntity).options(selectinload(PrescribedEntity.verification_result)).where(PrescribedEntity.document_id == doc.id))).scalars().all()
    assert len(entities) == 6

    # Validate summary
    summary = (await db_session.execute(select(DocumentSummary).where(DocumentSummary.document_id == doc.id))).scalar_one_or_none()
    assert summary is not None
    assert len(summary.executive_summary) > 100

    # Validate critical points
    crit_pts = (await db_session.execute(select(CriticalPoint).where(CriticalPoint.document_id == doc.id))).scalars().all()
    assert len(crit_pts) >= 5
