# CONTRIBUTIONS — AgriDiff AI
**BIT-AI-001 | AGR-17 | Team CODEAVENGERS**

This file records verified work performed by each team member during the hackathon.

---

## Team Roster

| Member | Department | Role | GitHub | Primary Ownership |
|---|---|---|---|---|
| **KAVISH S R** | CSE | Team Leader | [@jonekavish-dot](https://github.com/jonekavish-dot) | Architecture, Comparison Engine, Entity Extractor, Validator |
| **GOWSHIKGUNAL R** | CSE | Frontend Lead | [@gowshikgunal22](https://github.com/gowshikgunal22) | React UI, Dual-View Tabs, Land Record Table, Evidence Modal |
| **PRANESH K V** | AIDS | Data & Evaluation | [@kvpranesh](https://github.com/kvpranesh) | 22-Change Benchmark, Patta Dataset, Ground Truth, Pytest Suite |
| **DINESH B** | AIDS | Integration & Release | [@dineshbalu7f-glitch](https://github.com/dineshbalu7f-glitch) | FastAPI Services, TestClient Tests, Docs, Vite Build |

---

## Detailed Contribution Log

### KAVISH S R — Lead Architect & Backend
* **System Architecture & Data Contracts:**
  * Defined canonical change object schema (`models/schemas.py`) with `CH-001` format, clause tracking, and `SUPPORTED`/`UNCERTAIN`/`NOT_FOUND` evidence statuses.
* **Exhaustive Comparison Engine:**
  * Implemented clause-level section chunking in `chunker.py` ensuring zero dropped differences.
  * Implemented semantic alignment in `aligner.py` with `SEMANTICALLY_EQUIVALENT` and `UNCHANGED` classifications.
  * Implemented unified pair embedding in `embedder.py` with joint feature spaces.
* **Structured Entity Extractor:**
  * Authored `pipeline/entity_extractor.py` for land records and administrative agricultural documents.
  * Built deterministic extractors for survey numbers (`123 → 123/2`), land area (`2 acres → 4 acres`), patta holders (`ABC → XYZ`), verifier designations, and deadlines.
  * Enforced strict anti-hallucination rules: absent fields flagged as `NOT_FOUND`; zero inferred ownership or buyer/seller relations.
* **Evidence Validation & Result Assembly:**
  * Built `validator.py` with strict substring quote verification against source text.
  * Implemented dual-mode output packaging: `all_changes` (exhaustive) + `impact_changes` (prioritized) + `field_changes` (structured table).

---

### GOWSHIKGUNAL R — Frontend Lead
* **Interactive Results Dashboard:**
  * Authored tri-tab navigation in `ResultsPage.jsx`:
    * *Tab 1: Exhaustive Comparison* — displays complete set of detected differences.
    * *Tab 2: Impact View* — filters strictly to consequential HIGH and MEDIUM priority changes.
    * *Tab 3: Structured & Land Records* — interactive tabular view of land administration changes.
* **Side-by-Side Evidence Modal:**
  * Updated `EvidenceModal.jsx` to render Old vs New source passages side-by-side with exact substring yellow highlights.
  * Added page number badges (`old_page` ➔ `new_page`) and evidence grounding status indicators.
* **One-Click Demo Experience:**
  * Enhanced `UploadPage.jsx` with quick-launch buttons for the 22-Change Policy Benchmark and the Patta Land Record pair, enabling instant judge demonstrations.
* **Component System:**
  * Updated `ChangeCard.jsx` to display canonical IDs, clause numbers, summaries, and impact explanations.
  * Updated `StatsBar.jsx` with real-time counters for exhaustive differences, impact changes, and structured fields.
  * Verified production bundle with Vite (`npm run build`).

---

### PRANESH K V — Data & Evaluation
* **Benchmark Datasets:**
  * Authored `data/generate_demo_pdfs.py` utilizing ReportLab.
  * Created 22-change agricultural policy benchmark pair (`demo_old_policy.pdf` vs `demo_new_policy.pdf`) covering test requirements T01 through T20.
  * Created synthetic land administration pair (`land_record_old.pdf` vs `land_record_new.pdf`).
  * Created canonical `data/ground_truth.json` with 22 labeled changes.
* **Automated Test Suite:**
  * Authored `tests/test_unit.py` (17 unit tests for parser, chunker, entity extractor, aligner, differ, validator).
  * Authored `tests/test_exhaustive.py` validating 20+ change policy coverage and land record field extraction.
  * Executed test suite achieving **27 / 27 tests passed (100%)**.
* **Evaluation Script:**
  * Authored `evaluation/eval.py` calculating precision, recall, F1, and evidence grounding rate.
  * Measured benchmark performance: **81.8% Recall, 100% Evidence Grounding Rate**.

---

### DINESH B — Integration & Release
* **API Endpoints & Presets:**
  * Updated `backend/main.py` with `/api/presets` and `/api/presets/{preset_id}/run` endpoints for immediate server-side execution.
  * Added query parameter filtering (`view=all|impact|fields`) to `/api/results/{job_id}/changes`.
* **API Testing:**
  * Authored `tests/test_api.py` using FastAPI `TestClient` covering healthcheck, presets, and validation states.
* **Documentation & Presentation:**
  * Maintained `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, and `docs/SETUP.md`.
  * Packaged `AgriDiff_AI_Enhanced_SRS_Presentation.pptx` in `docs/`.
  * Verified environment variable templates (`.env.example`).
* **Git & Release Management:**
  * Managed Git branches (`main`, `dev`, `feature/*`), staged commits, and synchronized with remote repository.

---

*This document accurately reflects all implemented components in the repository.*
