"""
AgriDiff AI — Section Detector + Chunker
Detects section headers and chunks text for semantic alignment.
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger("agridiff.chunker")

CHUNK_SIZE = 400      # max tokens per chunk (approx words × 1.3)
OVERLAP = 50          # overlap in tokens between chunks

# Patterns for common policy document section headers
SECTION_PATTERNS = [
    re.compile(r"^(\d+\.\d+\.\d+)\s+(.+)$", re.MULTILINE),   # 1.2.3 Title
    re.compile(r"^(\d+\.\d+)\s+(.+)$", re.MULTILINE),         # 1.2 Title
    re.compile(r"^(\d+\.)\s+(.+)$", re.MULTILINE),             # 1. Title
    re.compile(r"^(CHAPTER\s+\d+)[:\s]+(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^(SECTION\s+\d+)[:\s]+(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^([A-Z][A-Z\s]{4,50})$", re.MULTILINE),       # ALL CAPS headings
]


def detect_sections_and_chunks(pages: List[Dict]) -> List[Dict]:
    """
    Given page dicts from extractor, return a flat list of chunks.
    Each chunk: { chunk_id, text, section_title, section_number, page_start, page_end }
    """
    # Combine all pages into a single text with page markers
    full_text_with_pages = []
    for page in pages:
        full_text_with_pages.append((page["page_num"], page["text"]))

    # Build sections
    sections = _detect_sections(full_text_with_pages)

    # Chunk each section
    chunks = []
    chunk_id = 0
    for section in sections:
        section_chunks = _chunk_text(
            text=section["text"],
            section_title=section["section_title"],
            section_number=section["section_number"],
            page_start=section["page_start"],
            page_end=section["page_end"],
        )
        for chunk in section_chunks:
            chunk["chunk_id"] = f"chunk_{chunk_id:04d}"
            chunks.append(chunk)
            chunk_id += 1

    logger.info(f"Detected {len(sections)} sections → {len(chunks)} chunks")
    return chunks


def _detect_sections(pages_text: List[tuple]) -> List[Dict]:
    """Extract sections with their page numbers."""
    sections = []

    # Flatten all text, tracking page boundaries
    full_lines = []
    for page_num, text in pages_text:
        for line in text.split("\n"):
            full_lines.append((page_num, line))

    current_section = {
        "section_title": "Introduction",
        "section_number": None,
        "text_lines": [],
        "page_start": pages_text[0][0] if pages_text else 1,
        "page_end": pages_text[0][0] if pages_text else 1,
    }

    for page_num, line in full_lines:
        stripped = line.strip()
        if not stripped:
            current_section["text_lines"].append("")
            continue

        # Ignore benchmark footer watermark if present
        if "BIT-AI-001" in stripped or "Team CODEAVENGERS" in stripped:
            continue

        matched_header = _match_header(stripped)
        if matched_header and matched_header.get("is_top_level"):
            # Save previous section
            text = "\n".join(current_section["text_lines"]).strip()
            if text:
                current_section["text"] = text
                sections.append(dict(current_section))

            # Start new section without inserting header itself into body lines
            current_section = {
                "section_title": matched_header["title"],
                "section_number": matched_header["number"],
                "text_lines": [],
                "page_start": page_num,
                "page_end": page_num,
            }
        else:
            current_section["text_lines"].append(stripped)
            current_section["page_end"] = page_num

    # Don't forget last section
    text = "\n".join(current_section["text_lines"]).strip()
    if text:
        current_section["text"] = text
        sections.append(dict(current_section))

    # If no sections were detected (no headers found), treat whole doc as one section
    if not sections:
        full_text = "\n".join(line for _, line in full_lines).strip()
        sections = [{
            "section_title": "Document Content",
            "section_number": None,
            "text": full_text,
            "page_start": pages_text[0][0] if pages_text else 1,
            "page_end": pages_text[-1][0] if pages_text else 1,
        }]

    return sections


def _match_header(line: str) -> Dict | None:
    """Try to match a line as a section header. Returns {number, title, is_top_level} or None."""
    # Top-level numbered: "1. Title"
    m_top = re.match(r"^(\d+\.)\s+(.{3,80})$", line)
    if m_top:
        return {"number": m_top.group(1), "title": m_top.group(2).strip(), "is_top_level": True}

    # Subclause numbered: "1.1 Title" or "1.2.3 Title"
    m_sub = re.match(r"^(\d+(?:\.\d+)+\.?)\s+(.{3,80})$", line)
    if m_sub:
        return {"number": m_sub.group(1), "title": m_sub.group(2).strip(), "is_top_level": False}

    # CHAPTER / SECTION keyword
    m = re.match(r"^(CHAPTER|SECTION)\s+(\d+)[:\s]+(.+)$", line, re.IGNORECASE)
    if m:
        return {"number": f"{m.group(1)} {m.group(2)}", "title": m.group(3).strip(), "is_top_level": True}

    # All-caps heading (3+ words or 5+ chars, not colon line)
    if line.isupper() and len(line) > 5 and len(line.split()) <= 8 and not line.endswith(":"):
        return {"number": None, "title": line, "is_top_level": True}

    return None


def _chunk_text(text: str, section_title: str, section_number: str | None,
                page_start: int, page_end: int) -> List[Dict]:
    """Split section text into granular clause-level chunks."""
    if not text.strip():
        return []

    # If Introduction (e.g. doc title), return as single chunk
    if section_title == "Introduction":
        return [_make_chunk(
            text=text.strip(),
            section_title=section_title,
            section_number=None,
            page_start=page_start,
            page_end=page_end,
        )]

    # Split on double newlines OR numbered subclauses (1.1, 1.2) OR list items (a), b))
    raw_paras = [p.strip() for p in re.split(r"\n\n+|\n(?=\d+\.\d+)|\n(?=[a-e]\))", text) if p.strip()]

    if not raw_paras:
        return []

    chunks = []
    for p in raw_paras:
        m_sub = re.match(r"^(\d+\.\d+(?:\.\d+)?)\b", p)
        m_list = re.match(r"^([a-e]\))\s*", p)

        if m_sub:
            sub_num = m_sub.group(1)
        elif m_list:
            sub_num = m_list.group(1)
        else:
            sub_num = section_number

        chunks.append(_make_chunk(
            text=p,
            section_title=section_title,
            section_number=sub_num,
            page_start=page_start,
            page_end=page_end
        ))

    return chunks


def _make_chunk(text: str, section_title: str, section_number: str | None,
                page_start: int, page_end: int) -> Dict:
    return {
        "text": text,
        "section_title": section_title,
        "section_number": section_number,
        "page_start": page_start,
        "page_end": page_end,
    }


