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

        matched_header = _match_header(stripped)
        if matched_header:
            # Save previous section
            text = "\n".join(current_section["text_lines"]).strip()
            if text:
                current_section["text"] = text
                sections.append(dict(current_section))

            # Start new section
            current_section = {
                "section_title": matched_header["title"],
                "section_number": matched_header["number"],
                "text_lines": [stripped],
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
    """Try to match a line as a section header. Returns {number, title} or None."""
    # Numbered: "1. Title" or "1.1 Title"
    m = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.{3,80})$", line)
    if m:
        return {"number": m.group(1), "title": m.group(2).strip()}

    # CHAPTER / SECTION keyword
    m = re.match(r"^(CHAPTER|SECTION)\s+(\d+)[:\s]+(.+)$", line, re.IGNORECASE)
    if m:
        return {"number": f"{m.group(1)} {m.group(2)}", "title": m.group(3).strip()}

    # All-caps heading (3+ words or 5+ chars)
    if line.isupper() and len(line) > 5 and len(line.split()) <= 8:
        return {"number": None, "title": line}

    return None


def _chunk_text(text: str, section_title: str, section_number: str | None,
                page_start: int, page_end: int) -> List[Dict]:
    """Split section text into manageable chunks."""
    # Split on double newline (paragraph boundaries)
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]

    if not paragraphs:
        return []

    chunks = []
    current_chunk_words = []
    current_word_count = 0

    for para in paragraphs:
        words = para.split()
        if current_word_count + len(words) > CHUNK_SIZE and current_chunk_words:
            chunks.append(_make_chunk(
                " ".join(current_chunk_words), section_title, section_number, page_start, page_end
            ))
            # Keep overlap
            overlap_words = current_chunk_words[-OVERLAP:] if len(current_chunk_words) > OVERLAP else current_chunk_words
            current_chunk_words = overlap_words + words
            current_word_count = len(current_chunk_words)
        else:
            current_chunk_words.extend(words)
            current_word_count += len(words)

    if current_chunk_words:
        chunks.append(_make_chunk(
            " ".join(current_chunk_words), section_title, section_number, page_start, page_end
        ))

    return chunks if chunks else [_make_chunk(text, section_title, section_number, page_start, page_end)]


def _make_chunk(text: str, section_title: str, section_number: str | None,
                page_start: int, page_end: int) -> Dict:
    return {
        "text": text,
        "section_title": section_title,
        "section_number": section_number,
        "page_start": page_start,
        "page_end": page_end,
    }

