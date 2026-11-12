import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.core.logger import logger
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.services.parser import DocumentParser
from backend.app.services.chunker import MonographChunker
from backend.app.services.rag import RAGService
from backend.app.services.dedup import DeduplicationService


async def seed_initial_data(db: AsyncSession) -> None:
    """Creates default reviewer user and pre-indexes institutional reference formulary."""
    # 1. Seed Reviewer Account
    stmt_user = select(User).where(User.email == settings.DEFAULT_ADMIN_EMAIL.lower())
    reviewer = (await db.execute(stmt_user)).scalar_one_or_none()

    if not reviewer:
        reviewer = User(
            email=settings.DEFAULT_ADMIN_EMAIL.lower(),
            hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            full_name=settings.DEFAULT_ADMIN_NAME
        )
        db.add(reviewer)
        await db.flush()
        logger.info(f"Default reviewer account seeded: {settings.DEFAULT_ADMIN_EMAIL}")

    # 2. Seed Default Reference Formulary Document
    stmt_ref = select(Document).where(Document.document_type == "reference").limit(1)
    ref_doc = (await db.execute(stmt_ref)).scalar_one_or_none()

    if not ref_doc:
        ref_path = Path("data/source_documents/reference_document_medical.docx")
        if not ref_path.exists():
            ref_path = Path("reference_documents/reference_document_medical.docx")

        if ref_path.exists():
            file_bytes = ref_path.read_bytes()
            content_hash = DeduplicationService.compute_hash(file_bytes)
            raw_text, _ = DocumentParser.parse_docx(file_bytes)

            ref_doc = Document(
                user_id=reviewer.id,
                filename="Meridian_Bay_Formulary_Digest_Rev8.2.docx",
                file_type="docx",
                document_type="reference",
                content_hash=content_hash,
                raw_text=raw_text,
                file_path=str(ref_path),
                doc_metadata={
                    "title": "Institutional Formulary Digest",
                    "committee": "Pharmacy & Therapeutics Committee",
                    "revision": "8.2",
                    "approval_date": "February 12, 2026"
                }
            )
            db.add(ref_doc)
            await db.flush()

            # Pre-chunk and pre-index monographs
            chunks = MonographChunker.chunk_reference_document(raw_text)
            await RAGService.index_reference_chunks(db, ref_doc.id, chunks)
            logger.info(f"Pre-indexed {len(chunks)} monographs from reference formulary.")

    await db.commit()


if __name__ == "__main__":
    import asyncio
    from backend.app.db.session import init_db_schema, AsyncSessionLocal, engine

    async def main():
        print("\n" + "=" * 70)
        print(" [STANDALONE TEST] Database Initialization & Seeding")
        print("=" * 70)
        print("[*] Creating database schema & tables...")
        await init_db_schema()
        print("[+] Schema verified successfully.")

        print("[*] Seeding reviewer account and institutional formulary...")
        async with AsyncSessionLocal() as session:
            await seed_initial_data(session)

        print("[+] Reviewer credentials:")
        print(f"    - Email    : {settings.DEFAULT_ADMIN_EMAIL}")
        print(f"    - Password : {settings.DEFAULT_ADMIN_PASSWORD}")
        
        await engine.dispose()
        print("\n[✓] Database initialization completed successfully!\n")

    asyncio.run(main())

