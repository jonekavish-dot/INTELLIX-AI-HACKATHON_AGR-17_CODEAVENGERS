# CHANGELOG — AgriDiff AI
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

All notable changes to this project are documented here.
Format: `[version] YYYY-MM-DD — description`

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
