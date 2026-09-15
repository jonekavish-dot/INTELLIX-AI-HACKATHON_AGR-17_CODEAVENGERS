"""
AgriDiff AI — End-to-End (E2E) Workflow Test Suite
Validates the complete end-to-end lifecycle:
1. PDF upload via /api/compare
2. Job processing & status tracking via /api/status/{job_id}
3. Frozen canonical dual-view results via /api/results/{job_id}
4. Summary statistics consistency across tabs and views
5. Evidence grounding and quote verification

BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def test_e2e_complete_policy_comparison_workflow():
    old_pdf_path = os.path.join(DATA_DIR, "demo_old_policy.pdf")
    new_pdf_path = os.path.join(DATA_DIR, "demo_new_policy.pdf")

    assert os.path.exists(old_pdf_path), "demo_old_policy.pdf must exist"
    assert os.path.exists(new_pdf_path), "demo_new_policy.pdf must exist"

    # Step 1: Submit comparison job
    with open(old_pdf_path, "rb") as f_old, open(new_pdf_path, "rb") as f_new:
        files = {
            "old_pdf": ("demo_old_policy.pdf", f_old, "application/pdf"),
            "new_pdf": ("demo_new_policy.pdf", f_new, "application/pdf"),
        }
        resp = client.post("/api/compare", files=files)

    assert resp.status_code == 200, f"Submit failed: {resp.text}"
    job_data = resp.json()
    job_id = job_data["job_id"]
    assert job_id is not None
    assert job_data["status"] in ("queued", "processing", "completed")

    # Step 2: Poll status until completion
    max_wait = 20
    start = time.time()
    completed = False
    while time.time() - start < max_wait:
        status_resp = client.get(f"/api/status/{job_id}")
        assert status_resp.status_code == 200
        st = status_resp.json()
        if st["status"] == "completed":
            completed = True
            break
        elif st["status"] == "failed":
            pytest.fail(f"Job failed: {st.get('error')}")
        time.sleep(0.5)

    assert completed, f"Job did not complete within {max_wait}s"

    # Step 3: Fetch canonical results payload
    res_resp = client.get(f"/api/results/{job_id}")
    assert res_resp.status_code == 200, f"Failed to get results: {res_resp.text}"
    results = res_resp.json()

    # Step 4: Validate Dual Views & Consistency
    summary = results["summary"]
    all_changes = results["all_changes"]
    impact_changes = results["impact_changes"]
    field_changes = results.get("field_changes", [])

    # Consistency checks between summary and payload arrays
    assert summary["total_all_changes"] == len(all_changes)
    assert summary["total_impact_changes"] == len(impact_changes)
    assert summary["total_field_changes"] == len(field_changes)

    # Exhaustive comparison criteria
    assert len(all_changes) >= 20, f"Expected >= 20 exhaustive changes, got {len(all_changes)}"
    assert len(impact_changes) >= 8, f"Expected >= 8 impact changes, got {len(impact_changes)}"
    assert len(impact_changes) <= len(all_changes)

    # Verify impact changes contain ONLY HIGH and MEDIUM priority items
    for imp in impact_changes:
        assert imp["impact"] in ("HIGH", "MEDIUM")
        assert imp["change_type"] in ("MODIFIED", "ADDED", "REMOVED")

    # Step 5: Evidence Grounding and Quote Verification
    for change in all_changes:
        assert change["change_id"].startswith("CH-")
        assert change["category"] in [
            "Eligibility", "Financial", "Deadline", "Documentation",
            "Procedure", "Beneficiary", "LandRecord", "Other"
        ]
        assert change["evidence_status"] in ("SUPPORTED", "UNCERTAIN", "NOT_FOUND")

        # Check evidence spans structure
        assert "evidence_spans" in change
        assert isinstance(change["evidence_spans"], list)

    # High evidence grounding rate
    eval_meta = results["evaluation"]
    assert eval_meta["evidence_grounding_rate"] >= 0.90
