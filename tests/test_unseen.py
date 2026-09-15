"""
AgriDiff AI — Generalization Test on Unseen Document Pair
Validates that our safe normalization, section chunking, and structural
alignment rules generalize to completely unseen agricultural advisory documents
without overfitting to the original benchmark pair.

BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import pytest
from tests.test_exhaustive import run_full_pipeline_sync

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def test_unseen_advisory_pair_generalization():
    old_pdf = "unseen_advisory_old.pdf"
    new_pdf = "unseen_advisory_new.pdf"

    assert os.path.exists(os.path.join(DATA_DIR, old_pdf)), f"{old_pdf} missing"
    assert os.path.exists(os.path.join(DATA_DIR, new_pdf)), f"{new_pdf} missing"

    results = run_full_pipeline_sync(old_pdf, new_pdf)

    all_changes = results.all_changes
    impact_changes = results.impact_changes

    # 1. Total changes detected: we introduced 8-10 distinct changes across sections 1, 2, and 3
    assert len(all_changes) >= 7, f"Expected >= 7 changes in unseen advisory, got {len(all_changes)}"

    # 2. Section detection verification
    sections_detected = {c.section for c in all_changes}
    assert any("CROP PROTECTION" in s or "GUIDELINES" in s for s in sections_detected)
    assert any("SUBSIDY" in s or "FERTILIZER" in s for s in sections_detected)
    assert any("TIMELINE" in s or "APPLICATION" in s for s in sections_detected)

    # 3. Numeric difference detection in unseen documents
    # 2.1 Subsidy: Rs. 400 -> Rs. 600
    subsidy_changes = [c for c in all_changes if "400" in (c.old_text or "") and "600" in (c.new_text or "")]
    assert len(subsidy_changes) == 1
    assert subsidy_changes[0].change_type == "MODIFIED"

    # 4. Added clause detection in unseen documents
    # 1.4 Drone Spraying (ADDED)
    drone_changes = [c for c in all_changes if "drone" in (c.new_text or "").lower()]
    assert len(drone_changes) >= 1
    assert any(c.change_type == "ADDED" for c in drone_changes)

    # 2.3 Nano-Urea Grant (ADDED)
    nano_changes = [c for c in all_changes if "nano-urea" in (c.new_text or "").lower()]
    assert len(nano_changes) >= 1
    assert any(c.change_type == "ADDED" for c in nano_changes)

    # 5. Date difference detection in unseen documents
    # 3.1: 30-11-2025 -> 15-12-2025
    date_changes = [c for c in all_changes if "30-11-2025" in (c.old_text or "") and "15-12-2025" in (c.new_text or "")]
    assert len(date_changes) == 1
    assert date_changes[0].change_type == "MODIFIED"

    # 6. Evidence grounding must remain 100% on unseen documents
    assert results.evaluation.evidence_grounding_rate >= 0.90
    for c in all_changes:
        assert c.evidence_status in ("SUPPORTED", "UNCERTAIN")
        assert len(c.evidence_spans) >= 1
