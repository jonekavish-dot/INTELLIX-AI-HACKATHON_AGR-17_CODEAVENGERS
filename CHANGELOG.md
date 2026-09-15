# CHANGELOG — AgriDiff AI
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

All notable changes to this project are documented here.
Format: `[version] YYYY-MM-DD — description`

---

## [1.1.0] 2026-09-15 — Comparison Quality Optimization & False Positive Reduction

### Added
- **Safe Normalization Layer (`backend/pipeline/normalizer.py`):**
  - Canonical whitespace and linebreak collapsing without token destruction (`normalize_whitespace`).
  - Critical pattern preservation for numbers, dates, survey numbers, currencies, percentages, and units (`extract_critical_tokens`).
  - Strict whitespace/punctuation-only difference detection (`is_formatting_only_diff`).
  - Subclause identifier extractor and stripper (`extract_clause_identifier`, `strip_clause_identifier`).
  - Supporting evidence span deduplicator (`deduplicate_evidence_spans`).
- **Multi-Pass Structural & Semantic Alignment (`backend/pipeline/aligner.py`):**
  - Pass 1: Structural clause pairing by subsection ID (e.g. `4.2 Physical Verification` paired with `4.2 Online Upload` as `MODIFIED` rather than split into `ADDED` + `REMOVED`).
  - Pass 2: Cosine similarity matching with greedy thresholding.
  - Pass 3: Residual novel clause tracking (`ADDED`).
  - Deterministic natural document reading flow sorting.
- **Granular Chunker & Section Detector Enhancements (`backend/pipeline/chunker.py`):**
  - Separated top-level numbered sections (`1.`, `2.`, `CHAPTER`, `ALL CAPS`) from subclauses (`1.1`, `4.1`).
  - Prevented top-level section headers from polluting substantive clause content lines.
- **Evidence Spans Data Contract (`backend/models/schemas.py`, `backend/pipeline/validator.py`):**
  - Added `EvidenceSpan` schema modeling individual quote fragments.
  - Extended `DetectedChange` with `evidence_spans: List[EvidenceSpan]`, cleanly separating semantic change units from supporting grounding fragments.
- **Comprehensive New Test Suites (`tests/`):**
  - `test_regression.py` (11 tests): safe normalization, numeric token preservation, date preservation, survey number preservation, structural clause pairing, evidence spans.
  - `test_unseen.py` (1 test): generalization test on an entirely unseen pest & fertilizer advisory document pair (`unseen_advisory_old.pdf` vs `unseen_advisory_new.pdf`).
  - `test_e2e_workflow.py` (1 test): complete end-to-end API lifecycle test with quote grounding and tab counter consistency.
  - **Total automated tests: 40 / 40 passed (100%).**
- **Frontend Multi-Span Evidence Display (`frontend/src/components/EvidenceModal.jsx`):**
  - Rendered grounding fragments panel displaying individual evidence spans with page references and verified quote badges.

### Optimized
- **Benchmark Evaluation Performance (`evaluation/eval.py` on 22-change benchmark):**
  - Precision: **50.0% → 91.7%** (+41.7% absolute gain).
  - Recall: **81.8% → 100.0%** (all 22 ground-truth changes detected).
  - F1 Score: **62.1% → 95.7%** (+33.6% absolute gain).
  - False Positives: **18 → 2** (88.9% FP reduction; eliminated all section-header and split-clause FPs).
  - False Negatives: **4 → 0** (Zero missed changes).
  - Category Accuracy: **100.0%**.
  - Change Type Accuracy: **22.2% → 100.0%**.
  - Impact Accuracy: **38.9% → 100.0%**.
  - Evidence Grounding Rate: **100.0%** (24 / 24 changes verified against source text).

---

## [1.0.0] 2026-09-15 — Full AGR-17 System Implementation & Benchmark Release


### Added
- **Canonical Data Contract (`models/schemas.py`):**
  - Frozen canonical schema with `change_id` (`CH-001`), `section`, `subsection`, `change_type`, `category`, `field`, `old_value`, `new_value`, `summary`, `interpretation`, `impact`, `evidence_status` (`SUPPORTED` | `UNCERTAIN` | `NOT_FOUND`), and `confidence`.
- **Exhaustive Comparison Engine (`pipeline/aligner.py`, `pipeline/differ.py`):**
  - Clause-level granularity for subclauses and list items.
  - Zero dropped differences in `all_changes` mode.
  - Semantic similarity classification (`SEMANTICALLY_EQUIVALENT` vs `MODIFIED` vs `UNCHANGED`).
- **Secondary Impact View (`pipeline/validator.py`):**
  - Prioritizes HIGH and MEDIUM consequential changes in `impact_changes` without hiding exhaustive data.
- **Land Record & Patta Field Extractor (`pipeline/entity_extractor.py`):**
  - Extracts and compares land area (acres/ha), survey numbers (`123 → 123/2`), recorded holders (`ABC → XYZ`), and verifying authorities (`Revenue Inspector → Tahsildar`).
  - Strict anti-hallucination: absent fields marked `NOT_FOUND`; ambiguous relations marked `UNCERTAIN`; direct evidence marked `SUPPORTED`. Never infers ownership or buyer/seller.
- **Benchmark Benchmark Datasets (`data/`):**
  - 22-change agricultural policy benchmark (`demo_old_policy.pdf` vs `demo_new_policy.pdf`).
  - Synthetic land administration pair (`land_record_old.pdf` vs `land_record_new.pdf`).
  - `ground_truth.json` synchronized with 22 labeled changes.
- **Comprehensive Automated Test Suite (`tests/`):**
  - `test_unit.py` (17 unit tests): parser, chunker, entity extraction, aligner, differ, validator, schemas.
  - `test_api.py` (5 API tests): health, presets, validation errors, job status.
  - `test_exhaustive.py` (2 integration tests): 20+ change policy verification and land record entity verification.
  - **Result: 27 / 27 tests passed (100%).**
- **Frontend Dashboard Enhancements (`frontend/src/`):**
  - 1-Click judge demo preset buttons on `UploadPage.jsx`.
  - Tri-tab navigation on `ResultsPage.jsx`:
    * **Tab 1: Exhaustive Comparison** (all detected changes).
    * **Tab 2: Impact View** (consequential changes).
    * **Tab 3: Structured & Land Records** (tabular entity comparison).
  - Side-by-side evidence viewer with exact substring yellow highlights in `EvidenceModal.jsx`.
  - Canonical change cards with clause numbers and evidence assurance in `ChangeCard.jsx`.
  - Production bundle verified with Vite (`npm run build`).

---

## [0.2.0] 2026-09-15 — Engineering audit + architecture freeze

### Added
- `CHANGELOG.md` and `CONTRIBUTIONS.md`
- Canonical change object schema documented in `docs/ARCHITECTURE.md`
- Test strategy matrix (T01–T20) defined in `tests/test_strategy.py`

---

## [0.1.0] 2026-09-15 — Initial project scaffold

### Added
- FastAPI backend scaffold with `/api/compare`, `/api/status`, `/api/results`, `/api/health`
- Initial React + Tailwind frontend
- Demo PDFs and initial evaluation script
