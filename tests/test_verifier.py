import pytest
from pathlib import Path
from backend.app.services.chunker import MonographChunker
from backend.app.services.parser import DocumentParser
from backend.app.services.verifier import ClinicalVerifier


@pytest.fixture(scope="module")
def reference_chunks():
    path = Path("data/source_documents/reference_document_medical.docx")
    file_bytes = path.read_bytes()
    raw_text, _ = DocumentParser.parse_docx(file_bytes)
    return MonographChunker.chunk_reference_document(raw_text)


def test_verify_velantine_supported(reference_chunks):
    """Velantine 10 mg PO once daily -> Supported."""
    entity = {
        "medication_name": "Velantine",
        "dose": "10 mg",
        "route": "PO",
        "frequency": "once daily",
        "duration": "Continue indefinitely",
        "indication": "Hypertension"
    }
    result = ClinicalVerifier.verify_entity(entity, reference_chunks)
    assert result["status"] == "Supported"
    assert "Section I. Cardiovascular Agents" in result["citation_section"]
    assert "Velantine" in result["citation_monograph"]
    assert "10 mg orally once daily" in result["citation_passage"]


def test_verify_cordizem_dose_contradiction(reference_chunks):
    """Cordizem-XR 100 mg PO once daily -> Contradicted (initial dose > standard 50 mg)."""
    entity = {
        "medication_name": "Cordizem-XR",
        "dose": "100 mg",
        "route": "PO",
        "frequency": "once daily",
        "duration": "Continue indefinitely",
        "indication": "Rate control, hypertension"
    }
    result = ClinicalVerifier.verify_entity(entity, reference_chunks)
    assert result["status"] == "Contradicted"
    assert result["parameter_matches"]["dose_matched"] is False
    assert "50 mg" in result["explanation"]
    assert "exceeds" in result["explanation"].lower()
    assert "Standard adult dose: 50 mg" in result["citation_passage"]


def test_verify_pravoxil_timing_contradiction(reference_chunks):
    """Pravoxil 20 mg PO every morning -> Contradicted (morning administration vs bedtime requirement)."""
    entity = {
        "medication_name": "Pravoxil",
        "dose": "20 mg",
        "route": "PO",
        "frequency": "every morning",
        "duration": "Continue indefinitely",
        "indication": "Hyperlipidemia"
    }
    result = ClinicalVerifier.verify_entity(entity, reference_chunks)
    assert result["status"] == "Contradicted"
    assert result["parameter_matches"]["timing_matched"] is False
    assert "bedtime" in result["explanation"].lower()
    assert "morning administration" in result["explanation"].lower()
    assert "Section II. Lipid-Lowering Agents" in result["citation_section"]
    assert "evening" in result["citation_passage"].lower() or "nighttime" in result["citation_passage"].lower()


def test_verify_etrazolam_duration_contradiction(reference_chunks):
    """Etrazolam 0.5 mg PO twice daily for 8 weeks -> Contradicted (exceeds 4-week maximum duration limit)."""
    entity = {
        "medication_name": "Etrazolam",
        "dose": "0.5 mg",
        "route": "PO",
        "frequency": "twice daily",
        "duration": "8 weeks",
        "indication": "Acute anxiety, sleep disturbance"
    }
    result = ClinicalVerifier.verify_entity(entity, reference_chunks)
    assert result["status"] == "Contradicted"
    assert result["parameter_matches"]["duration_matched"] is False
    assert "4 weeks" in result["explanation"]
    assert "dependence" in result["explanation"].lower()
    assert "Section III. Anxiolytics and Sedatives" in result["citation_section"]


def test_verify_pranixol_unsupported(reference_chunks):
    """Pranixol 10 mg PO once daily -> Unsupported (not in formulary digest)."""
    entity = {
        "medication_name": "Pranixol",
        "dose": "10 mg",
        "route": "PO",
        "frequency": "once daily",
        "duration": "Continue indefinitely",
        "indication": "Adjunctive cardiovascular protection"
    }
    result = ClinicalVerifier.verify_entity(entity, reference_chunks)
    assert result["status"] == "Unsupported"
    assert "not listed in the institutional formulary digest" in result["explanation"]
    assert "Section VII" in result["citation_section"]
    assert "Other medications may be on formulary" in result["citation_passage"]


def test_verify_quintaxin_supported(reference_chunks):
    """Quintaxin 20 mg PO once daily, before breakfast, 8 weeks reassess -> Supported."""
    entity = {
        "medication_name": "Quintaxin",
        "dose": "20 mg",
        "route": "PO",
        "frequency": "once daily, before breakfast",
        "duration": "8 weeks, reassess",
        "indication": "GERD prophylaxis"
    }
    result = ClinicalVerifier.verify_entity(entity, reference_chunks)
    assert result["status"] == "Supported"
    assert "Section V. Gastrointestinal Agents" in result["citation_section"]
    assert "Quintaxin" in result["citation_monograph"]
