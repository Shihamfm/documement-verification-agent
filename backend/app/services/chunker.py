import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import re
from typing import List, Dict, Any
from backend.app.core.logger import logger


class MonographChunker:
    """Monograph-aware chunker for institutional formulary digests.

    Preserves discrete clinical monographs as cohesive semantic retrieval units,
    maintaining section hierarchies, dosage parameters, contraindications,
    and prescribing warnings without arbitrary character slicing.
    """

    # Major Section headers in Roman Numerals
    SECTION_REGEX = re.compile(r"^(I{1,3}|IV|V|VI{0,3}|IX|X)\.\s+(.+)$", re.MULTILINE)

    # Monograph drug titles in reference document
    KNOWN_DRUGS = [
        "Velantine",
        "Cordizem-XR",
        "Mirosartan",
        "Pravoxil",
        "Etrazolam",
        "Sumavast",
        "Quintaxin",
        "Floranase",
    ]

    @classmethod
    def chunk_reference_document(cls, text: str) -> List[Dict[str, Any]]:
        """Splits reference formulary text into discrete monograph chunks with metadata."""
        chunks: List[Dict[str, Any]] = []

        # Split text into sections based on Roman Numeral headings
        section_matches = list(cls.SECTION_REGEX.finditer(text))

        sections_parsed = []
        for i, match in enumerate(section_matches):
            sec_num = match.group(1).strip()
            sec_title = match.group(2).strip()
            start_pos = match.start()
            end_pos = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(text)
            sec_content = text[start_pos:end_pos].strip()
            sections_parsed.append({
                "num": sec_num,
                "title": sec_title,
                "content": sec_content
            })

        for sec in sections_parsed:
            sec_num = sec["num"]
            sec_title = sec["title"]
            sec_content = sec["content"]

            # If section is Quick-Reference Summary or Document Control, treat section as a whole chunk
            if "Summary" in sec_title or "Control" in sec_title:
                chunks.append({
                    "monograph_name": f"Section {sec_num}: {sec_title}",
                    "section_number": sec_num,
                    "section_title": sec_title,
                    "chunk_text": sec_content,
                    "metadata": {
                        "type": "summary_section",
                        "section_num": sec_num,
                        "section_title": sec_title
                    }
                })
                continue

            # In clinical sections, identify discrete drug monographs
            monograph_indices = []
            for drug in cls.KNOWN_DRUGS:
                pattern = rf"(?:^|\n)({re.escape(drug)})(?:\n|\s+Drug class:)"
                m = re.search(pattern, sec_content)
                if m:
                    monograph_indices.append((m.start(1), drug))

            monograph_indices.sort(key=lambda x: x[0])

            if not monograph_indices:
                # Fallback: store entire section
                chunks.append({
                    "monograph_name": f"Section {sec_num}: {sec_title}",
                    "section_number": sec_num,
                    "section_title": sec_title,
                    "chunk_text": sec_content,
                    "metadata": {"type": "general_section"}
                })
                continue

            for idx, (start_idx, drug_name) in enumerate(monograph_indices):
                end_idx = monograph_indices[idx + 1][0] if idx + 1 < len(monograph_indices) else len(sec_content)
                mono_text = sec_content[start_idx:end_idx].strip()

                parsed_mono = cls._extract_monograph_parameters(mono_text, drug_name, sec_num, sec_title)
                chunks.append(parsed_mono)

        logger.info(f"Chunked reference document into {len(chunks)} discrete monograph units.")
        return chunks

    @classmethod
    def _extract_monograph_parameters(
        cls, mono_text: str, drug_name: str, sec_num: str, sec_title: str
    ) -> Dict[str, Any]:
        """Extracts structured parameters from an individual monograph text."""
        params = {
            "monograph_name": drug_name,
            "section_number": sec_num,
            "section_title": sec_title,
            "chunk_text": mono_text,
            "metadata": {
                "drug_name": drug_name,
                "section": f"Section {sec_num}. {sec_title}",
                "standard_dose": cls._extract_field(mono_text, r"Standard adult dose:\s*([^\n]+)"),
                "maximum_dose": cls._extract_field(mono_text, r"Maximum dose:\s*([^\n]+)"),
                "indication": cls._extract_field(mono_text, r"Indication:\s*([^\n]+)"),
                "contraindications": cls._extract_field(mono_text, r"Contraindications:\s*([^\n]+)"),
                "interactions": cls._extract_field(mono_text, r"Significant interactions:\s*([^\n]+)"),
                "monitoring": cls._extract_field(mono_text, r"Monitoring:\s*([^\n]+)"),
                "adverse_effects": cls._extract_field(mono_text, r"Common adverse effects:\s*([^\n]+)"),
                "prescribing_notes": cls._extract_field(mono_text, r"Prescribing notes:\s*([^\n]+)"),
            }
        }
        return params

    @staticmethod
    def _extract_field(text: str, pattern: str) -> str:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

