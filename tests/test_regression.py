"""
AgriDiff AI — Regression & Normalization Test Suite
Validates precision improvements, safe normalization, structural alignment,
and non-regression of the exhaustive change detection engine.

BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import pytest
import numpy as np

from backend.pipeline.normalizer import (
    normalize_whitespace,
    extract_critical_tokens,
    is_formatting_only_diff,
    extract_clause_identifier,
    strip_clause_identifier,
    deduplicate_evidence_spans,
)
from backend.pipeline.chunker import _match_header, _chunk_text
from backend.pipeline.aligner import align_chunks
from backend.models.schemas import DetectedChange, EvidenceSpan


# ── 1. Safe Normalization & Token Preservation Tests ──────────────────────────

def test_r01_whitespace_normalization():
    raw = "  Eligible   small\n\nand   marginal\t\tfarmers  receive  cash.  "
    expected = "Eligible small and marginal farmers receive cash."
    assert normalize_whitespace(raw) == expected


def test_r02_punctuation_only_diff():
    text_a = "Land Ownership Record (Khatauni / Chitta);"
    text_b = "Land Ownership Record Khatauni Chitta"
    assert is_formatting_only_diff(text_a, text_b) is True


def test_r03_numeric_difference_preservation():
    text_a = "Farmers owning agricultural land up to 2 hectares shall be eligible."
    text_b = "Farmers owning agricultural land up to 5 hectares shall be eligible."
    assert is_formatting_only_diff(text_a, text_b) is False
    tokens_a = extract_critical_tokens(text_a)
    tokens_b = extract_critical_tokens(text_b)
    assert tokens_a != tokens_b
    assert "2hectares" in tokens_a or "2" in tokens_a


def test_r04_date_difference_preservation():
    text_a = "Applications must be submitted on or before 30-09-2026."
    text_b = "Applications must be submitted on or before 15-10-2026."
    assert is_formatting_only_diff(text_a, text_b) is False
    tokens_a = extract_critical_tokens(text_a)
    tokens_b = extract_critical_tokens(text_b)
    assert "30-09-2026" in tokens_a
    assert "15-10-2026" in tokens_b


def test_r05_survey_number_preservation():
    text_a = "Land parcel registered under Survey No: 123 in village A."
    text_b = "Land parcel registered under Survey No: 123/2 in village A."
    assert is_formatting_only_diff(text_a, text_b) is False
    tokens_a = extract_critical_tokens(text_a)
    tokens_b = extract_critical_tokens(text_b)
    assert "123" in tokens_a
    assert "123/2" in tokens_b


def test_r06_clause_identifier_extraction_and_stripping():
    text = "4.2 Physical Verification: Hard copies must be verified."
    cid = extract_clause_identifier(text)
    assert cid == "4.2"

    body = strip_clause_identifier(text)
    assert body.startswith("Physical Verification")

    bullet = "a) Aadhaar Card for identification"
    assert extract_clause_identifier(bullet) == "a)"
    assert strip_clause_identifier(bullet).startswith("Aadhaar Card")


def test_r07_deduplicate_evidence_spans():
    spans = [
        {"old_text": "Clause A", "old_page": 1, "new_text": "Clause A modified", "new_page": 1, "quote": "Clause A"},
        {"old_text": "  Clause A  ", "old_page": 1, "new_text": "Clause A modified", "new_page": 1, "quote": "Clause A"},
        {"old_text": "Clause B", "old_page": 2, "new_text": "Clause B new", "new_page": 2, "quote": "Clause B"},
    ]
    deduped = deduplicate_evidence_spans(spans)
    assert len(deduped) == 2


# ── 2. Structural Alignment & Chunking Regression Tests ────────────────────────

def test_r08_top_level_section_vs_subclause():
    match_top = _match_header("4. DOCUMENTATION REQUIREMENTS")
    assert match_top is not None
    assert match_top["is_top_level"] is True

    match_sub = _match_header("4.1 Mandatory Documents:")
    assert match_sub is not None
    assert match_sub["is_top_level"] is False


def test_r09_structural_clause_pairing_modified():
    # Clause 4.2: Phrasing is different (cosine similarity ~0.29), but both share subclause 4.2
    old_chunks = [{
        "chunk_id": "o1",
        "text": "4.2 Physical Verification: Physical submission of hard copies is mandatory at the local Agricultural Extension Center.",
        "section_title": "DOCUMENTATION REQUIREMENTS",
        "section_number": "4.2",
        "page_start": 1,
    }]
    new_chunks = [{
        "chunk_id": "n1",
        "text": "4.2 Online Upload: Physical submission is discontinued; all documents must be scanned and uploaded directly on the State Agriculture Portal.",
        "section_title": "DOCUMENTATION REQUIREMENTS",
        "section_number": "4.2",
        "page_start": 1,
    }]
    # Simulate non-zero similarity ~0.29
    old_emb = np.array([[1.0, 0.0]])
    new_emb = np.array([[0.29, float(np.sqrt(1.0 - 0.29**2))]])

    pairs = align_chunks(old_chunks, new_chunks, old_emb, new_emb)
    assert len(pairs) == 1
    assert pairs[0]["matched"] is True
    assert pairs[0]["change_type_pre"] == "MODIFIED"



def test_r10_unrelated_neighboring_clauses_not_merged():
    text = "1.1 Land Holding: Up to 2 ha.\n\n1.2 Annual Income: Up to Rs. 1,50,000."
    chunks = _chunk_text(text, "ELIGIBILITY CRITERIA", "1.", 1, 1)
    assert len(chunks) == 2
    assert chunks[0]["section_number"] == "1.1"
    assert chunks[1]["section_number"] == "1.2"
    assert "Land Holding" in chunks[0]["text"]
    assert "Annual Income" in chunks[1]["text"]


def test_r11_evidence_spans_in_detected_change():
    spans = [
        EvidenceSpan(old_text="Old rule text", old_page=1, quote="Old rule", status="SUPPORTED"),
        EvidenceSpan(new_text="New rule text", new_page=1, quote="New rule", status="SUPPORTED"),
    ]
    change = DetectedChange(
        change_id="CH-001",
        section="FINANCIAL ASSISTANCE & SUBSIDY",
        change_type="MODIFIED",
        category="Financial",
        summary="Subsidy increased from Rs. 5,000 to Rs. 8,000.",
        interpretation="Higher seasonal benefit.",
        impact="HIGH",
        evidence_status="SUPPORTED",
        confidence=0.95,
        evidence_spans=spans,
    )
    assert len(change.evidence_spans) == 2
    assert change.evidence_spans[0].quote == "Old rule"
    assert change.evidence_spans[1].quote == "New rule"
