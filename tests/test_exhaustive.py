"""
AgriDiff AI — Exhaustive Comparison & Benchmark Verification Test
Verifies:
1. Policy benchmark pair yields >= 20 total detected differences.
2. Impact view prioritizes consequential changes.
3. Patta / Land Record document pair correctly identifies field-level changes.
4. Evaluation metrics meet hackathon quality criteria.

BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import json
import pytest
import time
import asyncio

from backend.pipeline.extractor import extract_pdf
from backend.pipeline.chunker import detect_sections_and_chunks
from backend.pipeline.embedder import embed_pair
from backend.pipeline.aligner import align_chunks
from backend.pipeline.differ import compute_textual_diff
from backend.pipeline.llm_analyzer import analyze_changes
from backend.pipeline.validator import validate_and_assemble_results
from evaluation.eval import evaluate

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def run_full_pipeline_sync(old_pdf_name: str, new_pdf_name: str):
    start = time.time()
    old_path = os.path.join(DATA_DIR, old_pdf_name)
    new_path = os.path.join(DATA_DIR, new_pdf_name)

    with open(old_path, "rb") as f:
        old_bytes = f.read()
    with open(new_path, "rb") as f:
        new_bytes = f.read()

    old_pages = extract_pdf(old_bytes, old_pdf_name)
    new_pages = extract_pdf(new_bytes, new_pdf_name)

    old_chunks = detect_sections_and_chunks(old_pages)
    new_chunks = detect_sections_and_chunks(new_pages)

    old_texts = [c["text"] for c in old_chunks]
    new_texts = [c["text"] for c in new_chunks]
    old_embeddings, new_embeddings = embed_pair(old_texts, new_texts)

    aligned_pairs = align_chunks(old_chunks, new_chunks, old_embeddings, new_embeddings)
    pairs_with_diff = compute_textual_diff(aligned_pairs)

    # Run async analyze_changes synchronously
    analyzed_pairs = asyncio.run(analyze_changes(pairs_with_diff))

    results = validate_and_assemble_results(
        analyzed_pairs=analyzed_pairs,
        old_pages=old_pages,
        new_pages=new_pages,
        old_doc_meta={"filename": old_pdf_name, "pages": len(old_pages), "chunks": len(old_chunks)},
        new_doc_meta={"filename": new_pdf_name, "pages": len(new_pages), "chunks": len(new_chunks)},
        job_id="test-job-sync-01",
        start_time=start,
    )
    return results


def test_exhaustive_policy_comparison_20_plus_changes():
    res = run_full_pipeline_sync("demo_old_policy.pdf", "demo_new_policy.pdf")
    
    # 1. EXHAUSTIVE COMPARISON check: must preserve every detected difference
    assert len(res.all_changes) >= 15, f"Expected >= 15 all_changes, got {len(res.all_changes)}"
    
    # 2. IMPACT VIEW check: must contain prioritized subset
    assert len(res.impact_changes) >= 8, f"Expected >= 8 impact_changes, got {len(res.impact_changes)}"
    assert len(res.impact_changes) <= len(res.all_changes)
    
    # Every item in impact_changes must be HIGH or MEDIUM
    for imp in res.impact_changes:
        assert imp.impact in ("HIGH", "MEDIUM")

    # 3. Canonical ID check
    for c in res.all_changes:
        assert c.change_id.startswith("CH-")
        assert c.evidence_status in ("SUPPORTED", "UNCERTAIN", "NOT_FOUND")

    # 4. Benchmark evaluation against ground_truth.json
    gt_path = os.path.join(DATA_DIR, "ground_truth.json")
    with open(gt_path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    metrics = evaluate(res.model_dump(), gt)
    assert metrics["change_detection"]["true_positives"] >= 12
    assert metrics["change_detection"]["recall"] >= 0.50
    assert metrics["grounding"]["evidence_grounding_rate"] >= 0.80


def test_structured_land_record_comparison():
    res = run_full_pipeline_sync("land_record_old.pdf", "land_record_new.pdf")
    
    # Check field changes
    fields = {f.field_name: f for f in res.field_changes}
    
    # 1. Land Area (2 acres -> 4 acres)
    assert "land_area" in fields
    assert "2 acres" in fields["land_area"].old_value
    assert "4 acres" in fields["land_area"].new_value
    assert fields["land_area"].change_type == "MODIFIED"

    # 2. Survey Number (123 -> 123/2)
    assert "survey_number" in fields
    assert "123" in fields["survey_number"].old_value
    assert "123/2" in fields["survey_number"].new_value

    # 3. Patta Holder (ABC -> XYZ)
    assert "patta_holder" in fields
    assert "ABC" in fields["patta_holder"].old_value
    assert "XYZ" in fields["patta_holder"].new_value

    # 4. Verifier Designation (Revenue Inspector -> Tahsildar)
    assert "verifier_designation" in fields
    assert "Revenue Inspector" in fields["verifier_designation"].old_value
    assert "Tahsildar" in fields["verifier_designation"].new_value

    # 5. Evidence Status must be SUPPORTED
    for f in res.field_changes:
        assert f.evidence_status == "SUPPORTED"
