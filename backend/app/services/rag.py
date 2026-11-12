import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.rag import FormularyChunk
from backend.app.services.embedder import EmbeddingEngine
from backend.app.core.logger import logger


class RAGService:
    """Manages formulary chunk persistence and targeted retrieval for verification."""

    @classmethod
    async def index_reference_chunks(
        cls, db: AsyncSession, document_id: str, chunks: List[Dict[str, Any]]
    ) -> List[FormularyChunk]:
        """Stores chunks with embeddings in database."""
        db_chunks = []
        for c in chunks:
            text = c["chunk_text"]
            embedding = EmbeddingEngine.generate_vector(text)
            embedding_json = json.dumps(embedding)

            chunk_obj = FormularyChunk(
                document_id=document_id,
                monograph_name=c["monograph_name"],
                section_number=c["section_number"],
                section_title=c["section_title"],
                chunk_text=text,
                embedding_json=embedding_json,
                chunk_metadata=c["metadata"]
            )
            db.add(chunk_obj)
            db_chunks.append(chunk_obj)

        await db.flush()
        logger.info(f"Indexed {len(db_chunks)} chunks for document {document_id}")
        return db_chunks

    @classmethod
    async def retrieve_candidates(
        cls,
        db: AsyncSession,
        document_id: str,
        query: str,
        drug_name: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant monograph chunks using hybrid vector similarity and keyword grounding."""
        stmt = select(FormularyChunk).where(FormularyChunk.document_id == document_id)
        result = await db.execute(stmt)
        all_chunks = result.scalars().all()

        if not all_chunks:
            return []

        query_vec = EmbeddingEngine.generate_vector(query)
        scored_chunks = []

        for chunk in all_chunks:
            chunk_vec = json.loads(chunk.embedding_json) if chunk.embedding_json else []
            sim = EmbeddingEngine.cosine_similarity(query_vec, chunk_vec)

            # Keyword booster: if chunk monograph name matches target drug name
            if drug_name and drug_name.lower() in chunk.monograph_name.lower():
                sim += 1.0  # Dominant boost for exact monograph candidate

            scored_chunks.append({
                "chunk_id": chunk.id,
                "monograph_name": chunk.monograph_name,
                "section_number": chunk.section_number,
                "section_title": chunk.section_title,
                "chunk_text": chunk.chunk_text,
                "metadata": chunk.chunk_metadata,
                "score": sim
            })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
