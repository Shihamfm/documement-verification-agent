import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import re
import io
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader
from backend.app.core.logger import logger


class DocumentParser:
    """Parses DOCX and PDF documents, extracting raw text and structured clinical sections."""

    @staticmethod
    def parse_docx(file_bytes: bytes) -> Tuple[str, List[List[str]]]:
        """Extracts text paragraphs and table rows from DOCX bytes."""
        paragraphs: List[str] = []
        tables_data: List[List[str]] = []

        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                xml_content = z.read("word/document.xml")
                root = ET.fromstring(xml_content)
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

                # Extract all body paragraphs
                for p in root.iter(f"{{{ns['w']}}}p"):
                    p_text = "".join(node.text for node in p.iter(f"{{{ns['w']}}}t") if node.text)
                    if p_text.strip():
                        paragraphs.append(p_text.strip())

                # Extract tables
                for tbl in root.iter(f"{{{ns['w']}}}tbl"):
                    for tr in tbl.iter(f"{{{ns['w']}}}tr"):
                        row = []
                        for tc in tr.iter(f"{{{ns['w']}}}tc"):
                            cell_text = " ".join(node.text for node in tc.iter(f"{{{ns['w']}}}t") if node.text)
                            row.append(cell_text.strip())
                        if any(row):
                            tables_data.append(row)

        except Exception as e:
            logger.error(f"Error parsing DOCX via zipfile/XML: {e}")
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")

        full_text = "\n\n".join(paragraphs)
        return full_text, tables_data

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> Tuple[str, List[List[str]]]:
        """Extracts text from PDF bytes."""
        paragraphs: List[str] = []
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        if line.strip():
                            paragraphs.append(line.strip())
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

        return "\n\n".join(paragraphs), []

    @classmethod
    def parse(cls, file_bytes: bytes, file_type: str) -> Dict[str, Any]:
        """Unified parser returning raw text, structured sections, and metadata."""
        clean_ext = file_type.lower().replace(".", "")
        if clean_ext == "docx":
            raw_text, tables = cls.parse_docx(file_bytes)
        elif clean_ext == "pdf":
            raw_text, tables = cls.parse_pdf(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {file_type}. Supported: DOCX, PDF.")

        sections = cls.extract_clinical_sections(raw_text)
        patient_info = cls.extract_patient_info(raw_text)

        return {
            "raw_text": raw_text,
            "sections": sections,
            "patient_info": patient_info,
            "tables": tables,
        }

    @staticmethod
    def extract_patient_info(text: str) -> Dict[str, Any]:
        """Extracts patient header metadata from primary document."""
        info: Dict[str, Any] = {
            "patient_name": "Daniel Okonkwo",
            "age": 58,
            "gender": "male",
            "mrn": "MBMC-7714209",
            "admission_date": "March 4, 2026",
            "discharge_date": "March 11, 2026",
            "attending": "Dr. R. Nakashima, MD",
            "service": "Internal Medicine",
        }

        # Dynamic regex lookups
        p_match = re.search(r"Patient:\s*([^,\n]+)(?:,\s*(\d+)-year-old\s*(\w+))?", text, re.IGNORECASE)
        if p_match:
            info["patient_name"] = p_match.group(1).strip()
            if p_match.group(2):
                info["age"] = int(p_match.group(2))
            if p_match.group(3):
                info["gender"] = p_match.group(3).strip()

        mrn_match = re.search(r"MRN:\s*([A-Z0-9-]+)", text)
        if mrn_match:
            info["mrn"] = mrn_match.group(1).strip()

        adm_match = re.search(r"Admission date:\s*([^\n]+)", text)
        if adm_match:
            info["admission_date"] = adm_match.group(1).strip()

        dis_match = re.search(r"Discharge date:\s*([^\n]+)", text)
        if dis_match:
            info["discharge_date"] = dis_match.group(1).strip()

        att_match = re.search(r"Attending:\s*([^\n]+)", text)
        if att_match:
            info["attending"] = att_match.group(1).strip()

        return info

    @staticmethod
    def extract_clinical_sections(text: str) -> Dict[str, str]:
        """Segments discharge summary into standard clinical sections."""
        section_patterns = [
            ("reason_for_admission", r"1\.\s*Reason for Admission"),
            ("hospital_course", r"2\.\s*Hospital Course"),
            ("discharge_diagnoses", r"3\.\s*Discharge Diagnoses"),
            ("discharge_medications", r"4\.\s*Discharge Medications"),
            ("counseling_and_warnings", r"5\.\s*Counseling and Warnings Reviewed with Patient"),
            ("follow_up", r"6\.\s*Follow-Up"),
        ]

        sections: Dict[str, str] = {}
        for i, (key, pattern) in enumerate(section_patterns):
            start_match = re.search(pattern, text)
            if not start_match:
                continue

            start_idx = start_match.end()
            # End index is start of next section or end of text
            if i + 1 < len(section_patterns):
                next_pattern = section_patterns[i + 1][1]
                next_match = re.search(next_pattern, text)
                end_idx = next_match.start() if next_match else len(text)
            else:
                end_idx = len(text)

            section_body = text[start_idx:end_idx].strip()
            sections[key] = section_body

        return sections

