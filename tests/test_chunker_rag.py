import pytest
from pathlib import Path
from backend.app.services.chunker import MonographChunker
from backend.app.services.embedder import EmbeddingEngine
from backend.app.services.rag import RAGService
from backend.app.services.parser import DocumentParser


def test_monograph_aware_chunking():
    path = Path("data/source_documents/reference_document_medical.docx")
    assert path.exists()

    file_bytes = path.read_bytes()
    raw_text, _ = DocumentParser.parse_docx(file_bytes)

    chunks = MonographChunker.chunk_reference_document(raw_text)
    assert len(chunks) >= 8

    monograph_names = [c["monograph_name"] for c in chunks]
    assert "Velantine" in monograph_names
    assert "Cordizem-XR" in monograph_names
    assert "Pravoxil" in monograph_names
    assert "Etrazolam" in monograph_names
    assert "Quintaxin" in monograph_names

    # Verify structured monograph metadata
    pravoxil_chunk = next(c for c in chunks if c["monograph_name"] == "Pravoxil")
    assert pravoxil_chunk["section_number"] == "II"
    assert "Lipid" in pravoxil_chunk["section_title"]
    assert "bedtime" in pravoxil_chunk["metadata"]["standard_dose"].lower()
    assert "morning administration substantially reduces" in pravoxil_chunk["chunk_text"].lower()


def test_embedding_vector_generation():
    text1 = "Pravoxil lipid lowering statin cholesterol synthesis"
    text2 = "Pravoxil statin cholesterol medication"
    text3 = "Quintaxin gastric acid reflux heartburn proton pump"

    vec1 = EmbeddingEngine.generate_vector(text1)
    vec2 = EmbeddingEngine.generate_vector(text2)
    vec3 = EmbeddingEngine.generate_vector(text3)

    assert len(vec1) == len(vec2) == 128

    sim_related = EmbeddingEngine.cosine_similarity(vec1, vec2)
    sim_unrelated = EmbeddingEngine.cosine_similarity(vec1, vec3)

    assert sim_related > sim_unrelated


@pytest.mark.asyncio
async def test_targeted_rag_retrieval(db_session, indexed_reference_doc):
    query = "Pravoxil 20 mg PO every morning for Hyperlipidemia"
    candidates = await RAGService.retrieve_candidates(
        db=db_session,
        document_id=indexed_reference_doc.id,
        query=query,
        drug_name="Pravoxil",
        top_k=2
    )

    assert len(candidates) > 0
    top_candidate = candidates[0]
    assert top_candidate["monograph_name"] == "Pravoxil"
    assert top_candidate["section_number"] == "II"
    assert "Lipid-Lowering" in top_candidate["section_title"]
