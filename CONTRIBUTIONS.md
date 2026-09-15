# CONTRIBUTIONS — AgriDiff AI
**BIT-AI-001 | AGR-17 | Team CODEAVENGERS**

This file records verified work performed by each team member during the hackathon.

---

## Team Roster

| Member | Department | Role | GitHub | Primary Ownership |
|---|---|---|---|---|
| **KAVISH S R** | CSE | Team Leader | [@jonekavish-dot](https://github.com/jonekavish-dot) | Architecture, Comparison Engine, Normalization, Auth API |
| **GOWSHIKGUNAL R** | CSE | Frontend Lead | [@gowshikgunal22](https://github.com/gowshikgunal22) | Responsive React UI, Demo Login, Dual Views, Mobile Cards |
| **PRANESH K V** | AIDS | Data & Evaluation | [@kvpranesh](https://github.com/kvpranesh) | Benchmark Ground Truth, 48-Test Pytest Suite, Unseen Data |
| **DINESH B** | AIDS | Integration & Release | [@dineshbalu7f-glitch](https://github.com/dineshbalu7f-glitch) | FastAPI Backend, Production Builds, Docs, Release Verification |

---

## Detailed Contribution Log

### KAVISH S R — Lead Architect & Backend
* **System Architecture & Core Invariant:**
  * Enforced "Compare Everything First" — ensuring zero dropped source differences in exhaustive comparison mode before prioritizing impact.
* **Safe Normalization Engine (`backend/pipeline/normalizer.py`):**
  * Built safe whitespace and line break canonicalizer (`normalize_whitespace`) with unicode NFKC normalization.
  * Implemented token extractor protecting critical numbers, dates, survey numbers, currencies, percentages, and units (`extract_critical_tokens`).
  * Created `is_formatting_only_diff`, `extract_clause_identifier`, `strip_clause_identifier`, and `deduplicate_evidence_spans`.
* **Multi-Pass Structural & Semantic Alignment (`backend/pipeline/aligner.py`):**
  * Engineered Pass 1 Structural Clause Pairing by subsection ID (e.g., `4.2 Physical Verification` with `4.2 Online Upload`) to prevent artificial split into `ADDED` + `REMOVED`.
  * Implemented natural document order sorting and canonical change type classification.
* **Declarative Operational Notes Engine (`backend/pipeline/llm_analyzer.py`):**
  * Created `_build_exact_operational_note` producing direct factual statements of shifts from old to new documents.
* **Backend Authentication API & Validation (`backend/main.py`):**
  * Implemented `/api/auth/login` endpoint supporting synthetic demo accounts and validation.
  * Added 0-byte empty file detection and HTTP 400 error handling.

---

### GOWSHIKGUNAL R — Frontend Lead
* **Professional Demo Login Page (`frontend/src/pages/LoginPage.jsx`):**
  * Designed clean, agricultural-themed login interface with AGR-17 branding, demo account cards, and 1-click quick-fill buttons.
  * Implemented form validation for empty fields and invalid credentials.
* **Cross-Device Responsive Architecture (`frontend/src/`):**
  * Built fluid responsive layouts adapting seamlessly across 320px, 390px, 768px, 1024px, and 1920px+ viewports.
  * Created responsive `Navbar.jsx` with mobile drawer menu, active role badge, and session controls.
  * Enhanced `UploadPage.jsx` with touch-friendly dropzones, mobile file choosers, and explicit replace/remove buttons.
  * Transformed wide land-record tables into clean, touch-friendly card views on mobile screens (`ResultsPage.jsx`).
  * Implemented mobile-friendly `EvidenceModal.jsx` with tabbed `[ Old ]` / `[ New ]` toggles and sticky accessible close buttons.
  * Engineered collapsible mobile filter panel preventing layout breakage.
* **Production Build & Zero-Error QA:**
  * Verified clean compilation with Vite (`npm run build`) in < 6 seconds with 0 warnings.

---

### PRANESH K V — Data & Evaluation
* **Benchmark Ground Truth & Evaluation Metrics (`data/ground_truth.json`, `evaluation/eval.py`):**
  * Labeled canonical 22-change agricultural policy benchmark dataset.
  * Maintained evaluation harness measuring precision (91.7%), recall (100.0%), and F1 score (95.7%).
* **48-Test Automated Pytest Suite (`tests/`):**
  * Expanded test coverage across `test_api.py`, `test_unit.py`, `test_regression.py`, `test_exhaustive.py`, `test_unseen.py`, and `test_e2e_workflow.py`.
  * Authored test cases for demo authentication, invalid credentials, empty PDFs, and unknown job handling.
  * All 48 / 48 tests pass with 100% success rate.
* **Unseen Generalization Dataset:**
  * Created synthetic pest & advisory document pair proving zero overfitting to benchmark policies.

---

### DINESH B — Integration & Release
* **FastAPI Backend Services & Routing (`backend/main.py`):**
  * Structured async endpoints for compare, status, results, presets, and auth.
  * Managed background task queue and in-memory job store.
* **System Hardening & Failure Mode Testing:**
  * Validated graceful fallback handling when external AI APIs or OCR tools are unreachable.
  * Configured CORS middleware and production server bindings.
* **Release Documentation & Git Synchronization:**
  * Authored `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, and `docs/SETUP.md`.
  * Managed git branch workflows across `main`, `dev`, and feature branches.
