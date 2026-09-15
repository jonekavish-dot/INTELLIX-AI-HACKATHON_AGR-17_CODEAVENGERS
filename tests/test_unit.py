"""
AgriDiff AI — Unit Test Suite
Covers: Extractor, Chunker, Entity Extractor, Aligner, Differ, Validator, and Schemas.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import pytest
import numpy as np

from backend.pipeline.extractor import extract_pdf
from backend.pipeline.chunker import detect_sections_and_chunks, _match_header
from backend.pipeline.entity_extractor import (
    extract_entities_from_pages,
    compare_structured_entities,
)
from backend.pipeline.aligner import align_chunks
from backend.pipeline.differ import compute_textual_diff, _compute_diff
from backend.pipeline.validator import _verify_quote
from backend.models.schemas import DetectedChange, FieldChange, SummaryStats


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ── 1. Document Extraction Tests ───────────────────────────────────────────────

def test_u01_pdf_extraction_page_count():
    pdf_path = os.path.join(DATA_DIR, "demo_old_policy.pdf")
    assert os.path.exists(pdf_path), "demo_old_policy.pdf missing"
    with open(pdf_path, "rb") as f:
        pages = extract_pdf(f.read(), "demo_old_policy.pdf")
    assert len(pages) >= 1
    assert "ELIGIBILITY" in pages[0]["text"].upper()
    assert pages[0]["char_count"] > 100


def test_u02_extractor_page_number_tracking():
    pdf_path = os.path.join(DATA_DIR, "land_record_old.pdf")
    with open(pdf_path, "rb") as f:
        pages = extract_pdf(f.read(), "land_record_old.pdf")
    assert pages[0]["page_num"] == 1
    assert "PATTA" in pages[0]["text"].upper() or "SURVEY" in pages[0]["text"].upper()


# ── 2. Chunker & Section Detection Tests ───────────────────────────────────────

def test_u06_header_detection_numbered():
    match = _match_header("1. ELIGIBILITY CRITERIA")
    assert match is not None
    assert match["number"] == "1."
    assert "ELIGIBILITY" in match["title"]


def test_u07_header_detection_subclause():
    match = _match_header("1.1 Land Holding Limit")
    assert match is not None
    assert match["number"] == "1.1"


def test_u08_header_detection_all_caps():
    match = _match_header("BENEFICIARY COVERAGE")
    assert match is not None
    assert match["title"] == "BENEFICIARY COVERAGE"


def test_u10_chunking_preserves_content():
    dummy_pages = [{"page_num": 1, "text": "## 1. TITLE\nParagraph one.\n\nParagraph two."}]
    chunks = detect_sections_and_chunks(dummy_pages)
    assert len(chunks) >= 1
    assert "Paragraph one" in chunks[0]["text"]


# ── 3. Structured Entity Extractor Tests ───────────────────────────────────────

def test_u13_extract_land_area():
    sample_pages = [{"page_num": 1, "text": "Holding limit is 2 hectares for this scheme."}]
    entities = extract_entities_from_pages(sample_pages)
    assert entities["land_area"] is not None
    assert "2 hectares" in entities["land_area"]["value"]


def test_u15_extract_survey_number():
    sample_pages = [{"page_num": 1, "text": "Survey No: 123/2, Village: Anaimalai"}]
    entities = extract_entities_from_pages(sample_pages)
    assert entities["survey_number"] is not None
    assert entities["survey_number"]["value"] == "123/2"


def test_u16_extract_date_and_deadline():
    sample_pages = [{"page_num": 1, "text": "Applications must be submitted by 15-10-2026."}]
    entities = extract_entities_from_pages(sample_pages)
    assert entities["deadline"] is not None
    assert "15-10-2026" in entities["deadline"]["value"]


def test_u17_extract_percentage_and_currency():
    sample_pages = [{"page_num": 1, "text": "Subsidy of Rs. 8,000 at 50% benchmark."}]
    entities = extract_entities_from_pages(sample_pages)
    assert entities["subsidy_amount"] is not None
    assert "8,000" in entities["subsidy_amount"]["value"]
    assert entities["subsidy_percentage"]["value"] == "50%"


def test_u19_structured_entity_comparison_not_found():
    old_ent = {"land_area": {"value": "2 acres", "page": 1}}
    new_ent = {"land_area": None}
    changes = compare_structured_entities(old_ent, new_ent)
    assert len(changes) == 1
    assert changes[0].change_type == "REMOVED"
    assert changes[0].new_value == "NOT_FOUND"
    assert changes[0].evidence_status == "SUPPORTED"


def test_u20_no_false_seller_buyer_inference():
    # Verify entity extractor never creates seller/buyer unless explicit
    sample_pages = [{"page_num": 1, "text": "Farmer ABC visited Officer XYZ."}]
    entities = extract_entities_from_pages(sample_pages)
    assert entities["transaction_date"] is None


# ── 4. Aligner Tests ──────────────────────────────────────────────────────────

def test_u21_aligner_identical_unchanged():
    old_c = [{"chunk_id": "c1", "text": "Identical passage", "section_title": "Sec"}]
    new_c = [{"chunk_id": "c2", "text": "Identical passage", "section_title": "Sec"}]
    emb = np.array([[1.0, 0.0]])
    pairs = align_chunks(old_c, new_c, emb, emb)
    assert len(pairs) == 1
    assert pairs[0]["change_type_pre"] == "UNCHANGED"


def test_u22_aligner_semantic_equivalent():
    old_c = [{"chunk_id": "c1", "text": "Resident must hold domicile card", "section_title": "Sec"}]
    new_c = [{"chunk_id": "c2", "text": "Inhabitant must produce domicile proof", "section_title": "Sec"}]
    # Simulate high cosine similarity >= 0.95
    old_emb = np.array([[0.98, 0.19]])
    new_emb = np.array([[0.99, 0.14]])
    pairs = align_chunks(old_c, new_c, old_emb, new_emb)
    assert len(pairs) == 1
    assert pairs[0]["change_type_pre"] == "SEMANTICALLY_EQUIVALENT"


def test_u24_aligner_unmatched_chunks():
    old_c = [{"chunk_id": "c1", "text": "Deleted rule", "section_title": "Sec"}]
    new_c = [{"chunk_id": "c2", "text": "Completely novel rule", "section_title": "Sec"}]
    # Orthogonal vectors -> cosine = 0.0 -> no match
    old_emb = np.array([[1.0, 0.0]])
    new_emb = np.array([[0.0, 1.0]])
    pairs = align_chunks(old_c, new_c, old_emb, new_emb)
    assert any(p["change_type_pre"] == "REMOVED" for p in pairs)
    assert any(p["change_type_pre"] == "ADDED" for p in pairs)


# ── 5. Differ Tests ───────────────────────────────────────────────────────────

def test_u29_differ_identical_texts():
    ratio, ops = _compute_diff("Word A Word B", "Word A Word B")
    assert ratio == 1.0
    assert len(ops) == 1
    assert ops[0]["op"] == "equal"


def test_u31_differ_word_replacement():
    ratio, ops = _compute_diff("Subsidy of Rs. 5,000", "Subsidy of Rs. 8,000")
    assert ratio < 1.0
    ops_types = [o["op"] for o in ops]
    assert "insert" in ops_types and "delete" in ops_types


# ── 6. Evidence Validator Tests ───────────────────────────────────────────────

def test_u32_quote_verification_supported():
    text = "Farmers owning agricultural land up to 5 hectares are eligible."
    quote = "up to 5 hectares are eligible"
    v_quote, status = _verify_quote(quote, text)
    assert status == "SUPPORTED"
    assert v_quote == quote


def test_u33_quote_verification_hallucination_fallback():
    text = "Farmers owning agricultural land up to 5 hectares are eligible."
    hallucinated = "Subsidy of 100% is granted unconditionally."
    v_quote, status = _verify_quote(hallucinated, text)
    assert status == "UNCERTAIN"
    assert "Farmers owning" in v_quote


# ── 7. Pydantic Schema Constraints Tests ──────────────────────────────────────

def test_u38_canonical_change_schema():
    change = DetectedChange(
        change_id="CH-001",
        section="ELIGIBILITY CRITERIA",
        change_type="MODIFIED",
        category="Eligibility",
        summary="Land area limit increased.",
        interpretation="Medium farmers now eligible.",
        impact="HIGH",
        evidence_status="SUPPORTED",
        confidence=0.95
    )
    assert change.change_id == "CH-001"
    assert change.impact == "HIGH"

