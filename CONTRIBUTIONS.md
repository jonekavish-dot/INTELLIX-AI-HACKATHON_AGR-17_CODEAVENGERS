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
* **Safe Normalization Engine (`backend/pipeline/normalizer.py`):**
  * Built safe whitespace and line break canonicalizer (`normalize_whitespace`) with unicode NFKC normalization.
  * Implemented token extractor protecting critical numbers, dates, survey numbers, currencies, percentages, and units (`extract_critical_tokens`).
  * Created `is_formatting_only_diff`, `extract_clause_identifier`, `strip_clause_identifier`, and `deduplicate_evidence_spans`.
* **Multi-Pass Structural & Semantic Alignment (`backend/pipeline/aligner.py`):**
  * Engineered Pass 1 Structural Clause Pairing by subsection ID (e.g. `4.2 Physical Verification` with `4.2 Online Upload`) to prevent artificial split into `ADDED` + `REMOVED`.
  * Implemented natural document order sorting and canonical change type classification.
* **Top-Level Section Detection (`backend/pipeline/chunker.py`):**
  * Differentiated top-level policy sections from internal numbered clauses.
  * Prevented section headers from polluting substantive clause content lines.
* **Evidence Spans & Result Aggregator (`backend/pipeline/validator.py`):**
  * Integrated `EvidenceSpan` supporting fragments per `DetectedChange`.
  * Preserved explicit unchanged policy provisions (`disbursement_mode`, `exclusions`) while suppressing non-differing bullet fragments.

---

### GOWSHIKGUNAL R — Frontend Lead
* **Multi-Span Evidence Grounding UI:**
  * Enhanced `EvidenceModal.jsx` to render the new *Grounding Fragments* panel showing individual supporting evidence spans with old/new page numbers and verified quote chips.
  * Preserved full side-by-side comparative inspection with exact substring yellow highlights.
* **Component & Production Build Verification:**
  * Verified responsive styling and status badge colors for all 8 agricultural categories.
  * Executed clean production bundle build with Vite (`npm run build`).

---

### PRANESH K V — Data & Evaluation
* **Generalization & Unseen Datasets:**
  * Generated synthetic unseen agricultural advisory pair (`unseen_advisory_old.pdf` vs `unseen_advisory_new.pdf`).
  * Authored `tests/test_unseen.py` demonstrating zero overfitting to the benchmark pair.
* **Regression Test Suite:**
  * Authored `tests/test_regression.py` containing 11 tests for whitespace, punctuation-only diffs, numeric token preservation, date preservation, survey number preservation, and structural pairing.
* **Benchmark Optimization Metrics:**
  * Re-evaluated benchmark with `evaluation/eval.py`:
    * Precision: **91.7%** (up from 50.0%)
    * Recall: **100.0%** (22 / 22 ground truth detected, up from 81.8%)
    * F1 Score: **95.7%** (up from 62.1%)
    * False Positives reduced by **88.9%** (from 18 down to 2)
    * False Negatives eliminated completely (**0 FN**)
    * Evidence Grounding: **100.0%**

---

### DINESH B — Integration & Release
* **End-to-End Lifecycle Testing:**
  * Authored `tests/test_e2e_workflow.py` validating the entire comparison API cycle from file upload to job polling, dual-view payload verification, and summary counter consistency.
* **Documentation & Release Notes:**
  * Updated `README.md` with the v1.0.0 vs v1.1.0 benchmark comparison table.
  * Updated `CHANGELOG.md` with complete v1.1.0 optimization notes.
* **Test Suite Maintenance:**
  * Validated full automated test suite achieving **40 / 40 tests passed (100%)**.
* **Git & Branch Management:**
  * Staged commits and synchronized branches under respective team member identities.

---

*This document accurately reflects all implemented components in the repository.*

