from pathlib import Path
from backend.app.services.parser import DocumentParser


def test_parse_primary_docx():
    path = Path("data/source_documents/primary_document_medical.docx")
    assert path.exists()

    file_bytes = path.read_bytes()
    raw_text, tables = DocumentParser.parse_docx(file_bytes)

    assert "MERIDIAN BAY MEDICAL CENTER" in raw_text
    assert "Daniel Okonkwo" in raw_text
    assert "MBMC-7714209" in raw_text
    assert len(raw_text) > 1000


def test_extract_patient_demographics():
    path = Path("data/source_documents/primary_document_medical.docx")
    file_bytes = path.read_bytes()
    raw_text, _ = DocumentParser.parse_docx(file_bytes)

    info = DocumentParser.extract_patient_info(raw_text)
    assert info["patient_name"] == "Daniel Okonkwo"
    assert info["age"] == 58
    assert info["gender"].lower() == "male"
    assert info["mrn"] == "MBMC-7714209"
    assert "March 4, 2026" in info["admission_date"]
    assert "March 11, 2026" in info["discharge_date"]
    assert "Dr. R. Nakashima" in info["attending"]


def test_extract_clinical_sections():
    path = Path("data/source_documents/primary_document_medical.docx")
    file_bytes = path.read_bytes()
    raw_text, _ = DocumentParser.parse_docx(file_bytes)

    sections = DocumentParser.extract_clinical_sections(raw_text)
    assert "reason_for_admission" in sections
    assert "hospital_course" in sections
    assert "discharge_diagnoses" in sections
    assert "discharge_medications" in sections
    assert "counseling_and_warnings" in sections
    assert "follow_up" in sections

    assert "atrial fibrillation" in sections["reason_for_admission"].lower()
    assert "velantine" in sections["discharge_medications"].lower()
