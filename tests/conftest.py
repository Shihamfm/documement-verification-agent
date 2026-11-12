import pytest
import asyncio
import uuid
from pathlib import Path
from typing import AsyncGenerator
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from backend.app.main import app
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.core.security import hash_password, create_access_token
from backend.app.services.parser import DocumentParser
from backend.app.services.chunker import MonographChunker
from backend.app.services.rag import RAGService
from backend.app.services.dedup import DeduplicationService

TEST_DB_FILE = Path("data/test_verification.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE.resolve().as_posix()}"

test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


@pytest.fixture(scope="session", autouse=True)
def init_test_database():
    TEST_DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    async def _setup():
        async with test_engine.begin() as conn:
            from backend.app.models import (
                User, Document, Job, JobStage, FormularyChunk,
                PrescribedEntity, VerificationResult, DocumentSummary, CriticalPoint
            )
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_setup())
    yield

    async def _teardown():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()
        if TEST_DB_FILE.exists():
            try:
                TEST_DB_FILE.unlink()
            except Exception:
                pass

    asyncio.run(_teardown())


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    email = f"test_doctor_{uuid.uuid4().hex[:8]}@meridianbay.org"
    user = User(
        email=email,
        hashed_password=hash_password("DoctorPass123!"),
        full_name="Dr. Test Physician"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    email = f"other_doctor_{uuid.uuid4().hex[:8]}@meridianbay.org"
    user = User(
        email=email,
        hashed_password=hash_password("OtherPass123!"),
        full_name="Dr. Other Physician"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(data={"sub": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def indexed_reference_doc(db_session: AsyncSession, test_user: User) -> Document:
    # Check if reference doc already exists
    stmt = select(Document).where(Document.document_type == "reference").limit(1)
    existing_ref = (await db_session.execute(stmt)).scalar_one_or_none()
    if existing_ref:
        return existing_ref

    ref_path = Path("data/source_documents/reference_document_medical.docx")
    file_bytes = ref_path.read_bytes()
    raw_text, _ = DocumentParser.parse_docx(file_bytes)
    content_hash = DeduplicationService.compute_hash(file_bytes)

    ref_doc = Document(
        user_id=test_user.id,
        filename="reference_document_medical.docx",
        file_type="docx",
        document_type="reference",
        content_hash=content_hash,
        raw_text=raw_text,
        file_path=str(ref_path),
        doc_metadata={"revision": "8.2"}
    )
    db_session.add(ref_doc)
    await db_session.flush()

    chunks = MonographChunker.chunk_reference_document(raw_text)
    await RAGService.index_reference_chunks(db_session, ref_doc.id, chunks)
    await db_session.commit()
    await db_session.refresh(ref_doc)
    return ref_doc
