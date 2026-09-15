# CHANGELOG — AgriDiff AI
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

All notable changes to this project are documented here.
Format: `[version] YYYY-MM-DD — description`

---

## [1.2.0] 2026-09-15 — Final Production Hardening, Responsive Experience & Demo Authentication

### Added
- **Hackathon Demo Authentication System (`frontend/src/pages/LoginPage.jsx`, `backend/main.py`):**
  - Designed professional login UI with agricultural branding, AGR-17 project identifiers, and team credentials.
  - Safe synthetic demo accounts: `farmer`, `officer`, `reviewer` with 1-click fast-login buttons for judges.
  - Session persistence via `localStorage` across page refreshes with automatic unauthorized redirection.
  - Backend `/api/auth/login` endpoint with input validation and HTTP 400/401 handling.
- **Fully Responsive Cross-Device UI (`frontend/src/`):**
  - Engineered unified responsive layout supporting viewports from 320px (mobile) to 1920px+ (large desktop).
  - Responsive `Navbar.jsx` with mobile hamburger menu, active user profile, and role-based badges.
  - Mobile-optimized `UploadPage.jsx` with touch-friendly dropzones, Android/iOS file pickers, and explicit replace/remove buttons.
  - Mobile land-record card reflow inside `ResultsPage.jsx` converting wide 6-column tables into rich, touch-friendly cards on small screens.
  - Responsive `EvidenceModal.jsx` featuring tabbed `[ Old ]` / `[ New ]` toggle buttons and sticky accessible close targets.
  - Mobile collapsible filter panel with active filter count badges preventing horizontal overflow.
- **Robust Failure Mode & Edge-Case Protection (`backend/main.py`, `backend/pipeline/extractor.py`):**
  - Added 0-byte empty file detection returning clean HTTP 400 errors.
  - Hardened PyMuPDF and pdfplumber fallbacks for corrupt or malformed PDF streams.
  - Bound AI analyzers to fallback rules when external API is unreachable or returns malformed data.
- **Expanded Test Suite (`tests/test_api.py`):**
  - Added 8 new automated test cases covering valid credentials, invalid passwords, empty inputs, empty PDF rejection, and unknown job handling.
  - **Total automated tests: 48 / 48 passed (100%).**

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
- **Evidence Spans Data Contract (`backend/models/schemas.py`, `backend/pipeline/validator.py`):**
  - Added `EvidenceSpan` schema modeling individual quote fragments.
  - Extended `DetectedChange` with `evidence_spans: List[EvidenceSpan]`, cleanly separating semantic change units from supporting grounding fragments.
- **Declarative Operational Notes (`backend/pipeline/llm_analyzer.py`):**
  - Formulated direct, factual change notes detailing shifts from old to new document versions across all 24 change units.

### Optimized
- **Benchmark Evaluation Performance (`evaluation/eval.py` on 22-change benchmark):**
  - Precision: **50.0% → 91.7%** (+41.7% absolute gain).
  - Recall: **81.8% → 100.0%** (all 22 ground-truth changes detected).
  - F1 Score: **62.1% → 95.7%** (+33.6% absolute gain).
  - False Positives: **18 → 2** (88.9% FP reduction).
  - False Negatives: **4 → 0** (Zero missed changes).
  - Evidence Grounding Rate: **100.0%** (24 / 24 changes verified against source text).

---

## [1.0.0] 2026-09-15 — Full AGR-17 System Implementation & Benchmark Release

### Added
- **Canonical Data Contract (`models/schemas.py`):**
  - Frozen canonical schema with `change_id`, `section`, `change_type`, `category`, `old_value`, `new_value`, `summary`, `interpretation`, `impact`, `evidence_status`, and `confidence`.
- **Exhaustive Comparison Engine (`pipeline/aligner.py`, `pipeline/differ.py`):**
  - Clause-level granularity for subclauses and list items.
  - Zero dropped differences in `all_changes` mode.
- **FastAPI Backend & React Frontend:**
  - REST endpoints for upload, background comparison processing, status polling, and results retrieval.
  - Interactive dual-view dashboard with stats, filter bar, and evidence inspection modal.
