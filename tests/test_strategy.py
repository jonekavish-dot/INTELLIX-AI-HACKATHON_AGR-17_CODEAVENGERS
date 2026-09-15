"""
AgriDiff AI — Test Strategy and Fixture Index
BIT-AI-001 | AGR-17 | CODEAVENGERS

This file documents every test case, fixture, and the full test matrix.
Tests themselves live in tests/ (to be created).

Run with:
    pip install pytest httpx
    pytest tests/ -v
"""

# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

UNIT_TESTS = [
    # ── Extraction ──────────────────────────────────────────────────────────
    {"id": "U01", "module": "extractor", "desc": "PyMuPDF extracts correct page count"},
    {"id": "U02", "module": "extractor", "desc": "pdfplumber fallback used when PyMuPDF returns empty"},
    {"id": "U03", "module": "extractor", "desc": "OCR fallback triggered when avg chars/page < 50"},
    {"id": "U04", "module": "extractor", "desc": "Page numbers are preserved and sequential"},
    {"id": "U05", "module": "extractor", "desc": "Returns empty list gracefully on corrupt PDF"},

    # ── Chunker / Section Detection ─────────────────────────────────────────
    {"id": "U06", "module": "chunker", "desc": "Numbered heading '1. Title' detected as section"},
    {"id": "U07", "module": "chunker", "desc": "Numbered heading '1.1 Title' detected as section"},
    {"id": "U08", "module": "chunker", "desc": "ALL CAPS heading detected as section"},
    {"id": "U09", "module": "chunker", "desc": "No header → whole doc treated as one section"},
    {"id": "U10", "module": "chunker", "desc": "Chunk size respects CHUNK_SIZE=400 word limit"},
    {"id": "U11", "module": "chunker", "desc": "Overlap tokens preserved between consecutive chunks"},
    {"id": "U12", "module": "chunker", "desc": "Page numbers propagated correctly into chunks"},

    # ── Entity Extraction (TO BUILD) ────────────────────────────────────────
    {"id": "U13", "module": "entity_extractor", "desc": "Extracts land_area: '2 acres' → {value: 2, unit: 'acres'}"},
    {"id": "U14", "module": "entity_extractor", "desc": "Extracts land_area: '4 hectares' → {value: 4, unit: 'hectares'}"},
    {"id": "U15", "module": "entity_extractor", "desc": "Extracts survey_number: '123' and '123/2'"},
    {"id": "U16", "module": "entity_extractor", "desc": "Extracts date: '30-09-2026' and '15-10-2026'"},
    {"id": "U17", "module": "entity_extractor", "desc": "Extracts percentage: '40%' and '50%'"},
    {"id": "U18", "module": "entity_extractor", "desc": "Extracts monetary: 'Rs. 5,000' and 'Rs. 8,000'"},
    {"id": "U19", "module": "entity_extractor", "desc": "Returns NOT_FOUND for absent fields"},
    {"id": "U20", "module": "entity_extractor", "desc": "Does NOT infer seller/buyer from name proximity"},

    # ── Aligner ─────────────────────────────────────────────────────────────
    {"id": "U21", "module": "aligner", "desc": "Identical text → EQUIVALENT (score >= 0.95)"},
    {"id": "U22", "module": "aligner", "desc": "Reworded text → REWORDED (0.85 <= score < 0.95)"},
    {"id": "U23", "module": "aligner", "desc": "Modified text → MODIFIED (0.40 <= score < 0.85)"},
    {"id": "U24", "module": "aligner", "desc": "Unmatched old chunk → REMOVED"},
    {"id": "U25", "module": "aligner", "desc": "Unmatched new chunk → ADDED"},
    {"id": "U26", "module": "aligner", "desc": "Reordered sections aligned correctly by semantic match"},
    {"id": "U27", "module": "aligner", "desc": "Empty old doc → all new chunks marked ADDED"},
    {"id": "U28", "module": "aligner", "desc": "Empty new doc → all old chunks marked REMOVED"},

    # ── Differ ──────────────────────────────────────────────────────────────
    {"id": "U29", "module": "differ", "desc": "Identical texts → diff_ratio = 0.0"},
    {"id": "U30", "module": "differ", "desc": "Completely different texts → diff_ratio ≈ 1.0"},
    {"id": "U31", "module": "differ", "desc": "Single word changed → diff_ratio reflects proportion"},

    # ── Validator ───────────────────────────────────────────────────────────
    {"id": "U32", "module": "validator", "desc": "Evidence substring found → SUPPORTED"},
    {"id": "U33", "module": "validator", "desc": "Evidence not in source → INSUFFICIENT_EVIDENCE + source fallback"},
    {"id": "U34", "module": "validator", "desc": "NOT_PRESENT evidence passes for ADDED/REMOVED"},
    {"id": "U35", "module": "validator", "desc": "Numeric change detected → severity boosted to HIGH"},
    {"id": "U36", "module": "validator", "desc": "EQUIVALENT pairs not included in all_changes output"},
    {"id": "U37", "module": "validator", "desc": "Results sorted HIGH > MEDIUM > LOW"},

    # ── Schema ──────────────────────────────────────────────────────────────
    {"id": "U38", "module": "schemas", "desc": "DetectedChange Pydantic model validates correct data"},
    {"id": "U39", "module": "schemas", "desc": "DetectedChange rejects invalid change_type"},
    {"id": "U40", "module": "schemas", "desc": "DetectedChange rejects invalid severity"},
    {"id": "U41", "module": "schemas", "desc": "DetectedChange rejects invalid evidence_status"},

    # ── LLM Analyzer ────────────────────────────────────────────────────────
    {"id": "U42", "module": "llm_analyzer", "desc": "LLM JSON parse error → deterministic fallback returned"},
    {"id": "U43", "module": "llm_analyzer", "desc": "LLM timeout → deterministic fallback returned"},
    {"id": "U44", "module": "llm_analyzer", "desc": "Invalid category in LLM response → normalised to 'Other'"},
    {"id": "U45", "module": "llm_analyzer", "desc": "EQUIVALENT pairs skip LLM call entirely"},
]


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

INTEGRATION_TESTS = [
    {"id": "I01", "desc": "Full pipeline: demo_old_policy.pdf + demo_new_policy.pdf → 9+ changes"},
    {"id": "I02", "desc": "Full pipeline: identical PDFs → 0 meaningful changes"},
    {"id": "I03", "desc": "Full pipeline: land record old + new → field-level changes"},
    {"id": "I04", "desc": "LLM unavailable → pipeline completes with deterministic fallback"},
    {"id": "I05", "desc": "Large PDF (20+ pages) → pipeline completes without OOM"},
    {"id": "I06", "desc": "All 20 ground-truth changes detected in exhaustive comparison"},
]


# ─────────────────────────────────────────────────────────────────────────────
# API TESTS
# ─────────────────────────────────────────────────────────────────────────────

API_TESTS = [
    {"id": "A01", "method": "POST", "endpoint": "/api/compare", "case": "Valid old + new PDFs → 200, job_id returned"},
    {"id": "A02", "method": "POST", "endpoint": "/api/compare", "case": "Missing old_pdf → 422"},
    {"id": "A03", "method": "POST", "endpoint": "/api/compare", "case": "Missing new_pdf → 422"},
    {"id": "A04", "method": "POST", "endpoint": "/api/compare", "case": "Non-PDF file (PNG) → 400"},
    {"id": "A05", "method": "POST", "endpoint": "/api/compare", "case": "File > 50 MB → 400"},
    {"id": "A06", "method": "GET",  "endpoint": "/api/status/{job_id}", "case": "Valid job_id → 200 with status"},
    {"id": "A07", "method": "GET",  "endpoint": "/api/status/{job_id}", "case": "Unknown job_id → 404"},
    {"id": "A08", "method": "GET",  "endpoint": "/api/results/{job_id}", "case": "Completed job → 200 with full result"},
    {"id": "A09", "method": "GET",  "endpoint": "/api/results/{job_id}", "case": "In-progress job → 202"},
    {"id": "A10", "method": "GET",  "endpoint": "/api/results/{job_id}", "case": "Failed job → 500 with error message"},
    {"id": "A11", "method": "GET",  "endpoint": "/api/results/{job_id}/changes", "case": "Filter by category=Financial → only financial changes"},
    {"id": "A12", "method": "GET",  "endpoint": "/api/results/{job_id}/changes", "case": "Filter by severity=HIGH → only HIGH changes"},
    {"id": "A13", "method": "GET",  "endpoint": "/api/results/{job_id}/changes", "case": "view=all → all_changes list"},
    {"id": "A14", "method": "GET",  "endpoint": "/api/results/{job_id}/changes", "case": "view=impact → impact_changes list only"},
    {"id": "A15", "method": "GET",  "endpoint": "/api/health", "case": "Health check → 200 {status: ok}"},
]


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURE / TEST DATA CASES (T01–T20)
# ─────────────────────────────────────────────────────────────────────────────

FIXTURE_CASES = [
    {"id": "T01", "name": "Identical Documents",         "expected": "0 meaningful changes"},
    {"id": "T02", "name": "Addition",                    "expected": "ADDED change detected"},
    {"id": "T03", "name": "Removal",                     "expected": "REMOVED change detected"},
    {"id": "T04", "name": "Modification",                "expected": "MODIFIED change detected"},
    {"id": "T05", "name": "Semantic Equivalent",         "expected": "SEMANTICALLY_EQUIVALENT, not MODIFIED"},
    {"id": "T06", "name": "Numeric: 2 acres → 4 acres",  "expected": "MODIFIED, field=land_area, HIGH severity"},
    {"id": "T07", "name": "Date: 30-09 → 15-10",        "expected": "MODIFIED, field=deadline, HIGH severity"},
    {"id": "T08", "name": "Percentage: 40% → 50%",       "expected": "MODIFIED, field=subsidy_pct, HIGH severity"},
    {"id": "T09", "name": "Survey: 123 → 123/2",         "expected": "MODIFIED, field=survey_number"},
    {"id": "T10", "name": "Owner: ABC → XYZ",            "expected": "MODIFIED, field=holder"},
    {"id": "T11", "name": "Verifier: RI → Tahsildar",    "expected": "MODIFIED, field=verifier_designation"},
    {"id": "T12", "name": "Added parcel (area)",         "expected": "ADDED field=land_parcel"},
    {"id": "T13", "name": "Explicit transaction",        "expected": "Only source-supported facts shown"},
    {"id": "T14", "name": "Missing verifier in NEW",     "expected": "NOT_FOUND for verifier in new"},
    {"id": "T15", "name": "Ambiguous ownership",         "expected": "UNCERTAIN evidence_status"},
    {"id": "T16", "name": "Reordered sections",          "expected": "Sections still semantically aligned"},
    {"id": "T17", "name": "20+ changes",                 "expected": "All 20 changes in all_changes (exhaustive)"},
    {"id": "T18", "name": "Malformed LLM response",      "expected": "Schema retry → fallback, no crash"},
    {"id": "T19", "name": "Scanned/OCR PDF",             "expected": "OCR fallback used, text extracted"},
    {"id": "T20", "name": "LLM failure injection",       "expected": "Deterministic fallback, no crash"},
]


# ─────────────────────────────────────────────────────────────────────────────
# E2E WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────

E2E_STEPS = [
    "1. Open application at localhost:3000",
    "2. Verify Upload page loads with two drop zones",
    "3. Upload demo_old_policy.pdf to OLD zone",
    "4. Upload demo_new_policy.pdf to NEW zone",
    "5. Click 'Compare Documents'",
    "6. Verify Processing page shows pipeline stage progress",
    "7. Verify progress reaches 100% and transitions to Results",
    "8. Verify Stats Bar shows correct change counts",
    "9. Open 'All Changes' tab — verify ALL detected changes present",
    "10. Open 'Impact View' tab — verify only HIGH/MEDIUM shown",
    "11. Filter by category=Financial — verify only financial changes",
    "12. Filter by severity=HIGH — verify only HIGH severity shown",
    "13. Click 'View Evidence' on any MODIFIED change",
    "14. Verify Evidence Modal opens with side-by-side old/new text",
    "15. Verify evidence quote is highlighted within source passage",
    "16. Verify old_page and new_page references displayed",
    "17. Verify evidence_status badge shown (SUPPORTED / INSUFFICIENT_EVIDENCE)",
    "18. Close modal and click 'Export JSON'",
    "19. Verify JSON file downloaded with valid structure",
    "20. Click 'New Comparison' — verify Upload page resets cleanly",
]

if __name__ == "__main__":
    print(f"Unit tests:       {len(UNIT_TESTS)}")
    print(f"Integration tests:{len(INTEGRATION_TESTS)}")
    print(f"API tests:        {len(API_TESTS)}")
    print(f"Fixture cases:    {len(FIXTURE_CASES)}")
    print(f"E2E steps:        {len(E2E_STEPS)}")
    print(f"Total test items: {len(UNIT_TESTS)+len(INTEGRATION_TESTS)+len(API_TESTS)+len(FIXTURE_CASES)}")
