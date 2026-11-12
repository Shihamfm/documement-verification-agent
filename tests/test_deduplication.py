import pytest
import io
import httpx
from pathlib import Path
from backend.app.services.dedup import DeduplicationService
from backend.app.models.user import User


def test_hash_computation():
    content = b"Clinical discharge summary text for testing hashing"
    hash1 = DeduplicationService.compute_hash(content)
    hash2 = DeduplicationService.compute_hash(content)
    assert hash1 == hash2
    assert len(hash1) == 64


@pytest.mark.asyncio
async def test_duplicate_upload_detection(
    client: httpx.AsyncClient,
    test_user: User,
    auth_headers: dict,
    indexed_reference_doc
):
    """Extra Credit §4: Uploading identical document within window returns existing job ID."""
    doc_path = Path("data/source_documents/primary_document_medical.docx")
    file_bytes = doc_path.read_bytes()

    # 1. First upload -> Spawns new job
    files1 = {"file": ("primary_document_medical.docx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    resp1 = await client.post("/api/documents/upload", headers=auth_headers, files=files1)
    assert resp1.status_code == 202
    data1 = resp1.json()
    job1_id = data1["job_id"]
    assert data1["is_duplicate"] is False

    # 2. Duplicate upload within 5-minute window -> Returns existing job
    files2 = {"file": ("primary_document_medical.docx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    resp2 = await client.post("/api/documents/upload", headers=auth_headers, files=files2)
    assert resp2.status_code == 202
    data2 = resp2.json()
    assert data2["is_duplicate"] is True
    assert data2["job_id"] == job1_id
    assert "Identical document uploaded within the deduplication window" in data2["message"]
