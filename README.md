# 🌾 AgriDiff AI
### "Don't just compare documents. Understand what changed."

> **Hackathon:** BIT-AI-001 | **Problem:** AGR-17 | **Team:** CODEAVENGERS  
> **Institution:** Bannari Amman Institute of Technology  
> **Domain:** Agriculture & Rural Development

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passed-brightgreen)](tests/)
[![Precision](https://img.shields.io/badge/Precision-91.7%25-brightgreen)](evaluation/)
[![Recall](https://img.shields.io/badge/Recall-100.0%25-brightgreen)](evaluation/)
[![F1 Score](https://img.shields.io/badge/F1%20Score-95.7%25-brightgreen)](evaluation/)
[![Evidence Grounding](https://img.shields.io/badge/Grounding-100%25%20Verified-blue)](backend/pipeline/validator.py)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Problem Statement (AGR-17)

Develop an LLM application capable of comparing two versions of agricultural policies, guidelines, advisories, and administrative land records. Retrieve and identify changed sections, additions, removals, and modified conditions without hallucination.

---

## 🚀 Core Product Innovation: Dual-View Intelligence

The core product rule of **AgriDiff AI**:
> The comparison engine first performs an **EXHAUSTIVE COMPARISON** preserving every source-supported difference. Then, as a secondary layer, the system provides an **IMPACT VIEW** prioritizing consequential changes without hiding complete comparison data.

```
OLD DOCUMENT + NEW DOCUMENT
            ↓
  EXHAUSTIVE COMPARISON          ← Zero omitted source differences
            ↓
  SAFE NORMALIZATION             ← Whitespace/punctuation cleanup without token loss
            ↓
  STRUCTURAL & SEMANTIC ALIGN    ← Multi-pass pairing (subclauses + high cosine)
            ↓
  EVIDENCE VALIDATION            ← Strict quote verification & multi-span grounding
            ↓
  IMPACT CLASSIFICATION          ← Domain prioritization (Eligibility, Financial, etc.)
            ↓
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│    EXHAUSTIVE COMPARISON     │         IMPACT VIEW          │   STRUCTURED & LAND RECORD   │
│ Every detected difference    │ High/Medium priority changes │ Patta, Survey No, Land Area  │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

### Three Intelligence Layers

| Level | Intelligence Type | Implementation |
|---|---|---|
| **Level 1 — Textual** | Literal additions, removals, deletions | `difflib` word-level opcodes + safe normalizer |
| **Level 2 — Semantic** | Meaning-changing vs wording-only changes | Structural clause pairing + Sentence-Transformers |
| **Level 3 — Impact** | Domain priority & farmer impact analysis | Gemini 1.5 Flash + Deterministic domain rules |
| **Orthogonal — Evidence** | Quote verification against source text | Substring match (`SUPPORTED`, `UNCERTAIN`, `NOT_FOUND`) |

---

## 📜 Land Record & Patta Administrative Intelligence

AgriDiff AI features a dedicated structured entity extractor for land administration:
* **Land Area:** Identifies acre / hectare holding limit changes (e.g. `2 acres → 4 acres`, `2 ha → 5 ha`).
* **Survey Numbers:** Tracks subdivision changes (e.g. `123 → 123/2`).
* **Patta Holders:** Tracks recorded name changes (`ABC → XYZ`).
* **Verifying Authorities:** Identifies authority changes (`Revenue Inspector → Tahsildar`).
* **Strict Anti-Hallucination:**
  * Absent fields are marked `NOT_FOUND`.
  * Ambiguous relations are marked `UNCERTAIN`.
  * Directly cited quotes are marked `SUPPORTED`.
  * **Never infers buyer/seller or legal ownership unless explicitly stated in document text.**

---

## 📊 Benchmark Optimization & Evaluation (v1.0.0 vs v1.1.0)

Tested against the 22-change controlled ground-truth benchmark (`data/ground_truth.json`):

| Evaluation Metric | Baseline (v1.0.0) | Optimized (v1.1.0) | Absolute Improvement |
|---|---|---|---|
| **Ground Truth Changes** | 22 | **22** | 100% evaluated |
| **Detected Changes** | 36 | **24** | -12 (removed section-header & micro-split FPs) |
| **True Positives** | 18 | **22** | **+4 (100% of ground truth detected)** |
| **False Positives** | 18 | **2** | **-16 (-88.9% FP reduction)** |
| **False Negatives** | 4 | **0** | **-4 (Zero missed changes!)** |
| **Precision** | 50.0% | **91.7%** | **+41.7% gain** |
| **Recall** | 81.8% | **100.0%** | **+18.2% gain** |
| **F1 Score** | 62.1% | **95.7%** | **+33.6% gain** |
| **Category Accuracy** | 100.0% | **100.0%** | 100% preserved |
| **Change Type Accuracy** | 22.2% | **100.0%** | **+77.8% gain** |
| **Impact Accuracy** | 38.9% | **100.0%** | **+61.1% gain** |
| **Evidence Grounding Rate** | 100.0% | **100.0%** | 24 / 24 passages grounded |
| **Automated Test Suite** | 27 / 27 Passed | **40 / 40 Passed** | **+13 new regression & E2E tests** |

> **Note on the 2 Remaining Unmatched Detections:** The 2 detections not in the 22 ground-truth items are genuine textual changes in Section 7 of the source PDFs (the addition of the *Grievance Redressal Portal* and removal of the *90-day Utilization Voucher*). AgriDiff AI preserves them under its **EXHAUSTIVE** comparison mandate.

---

## 📁 Project Structure

```
INTELLIX-AI-HACKATHON_AGR-17_CODEAVENGERS/
├── backend/
│   ├── main.py                  # FastAPI app + routes + demo presets
│   ├── pipeline/
│   │   ├── extractor.py         # PyMuPDF + pdfplumber + OCR
│   │   ├── normalizer.py        # Safe whitespace/punctuation normalizer & token extractor
│   │   ├── chunker.py           # Top-level section detector & clause-level chunker
│   │   ├── embedder.py          # Unified pair embedding & sentence-transformers
│   │   ├── aligner.py           # Multi-pass structural & cosine alignment (Exhaustive)
│   │   ├── differ.py            # Word-level textual differ
│   │   ├── entity_extractor.py  # Patta & land record field comparator
│   │   ├── llm_analyzer.py      # Gemini 1.5 Flash + deterministic domain fallback
│   │   └── validator.py         # Dual-view aggregator, quote verifier & multi-spans
│   ├── models/
│   │   └── schemas.py           # Canonical Pydantic contracts & EvidenceSpan
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChangeCard.jsx   # Canonical cards with clause & evidence tags
│   │   │   ├── EvidenceModal.jsx# Multi-span evidence with yellow highlights
│   │   │   ├── FilterBar.jsx    # Category, severity & type filters
│   │   │   └── StatsBar.jsx     # Dual-view summary counters
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx   # 1-Click demo presets + drag & drop
│   │   │   ├── ProcessingPage.jsx # Multi-stage pipeline stepper
│   │   │   └── ResultsPage.jsx  # Exhaustive, Impact, & Land Record tabs
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── demo_old_policy.pdf      # 22-change old policy benchmark
│   ├── demo_new_policy.pdf      # 22-change new policy benchmark
│   ├── unseen_advisory_old.pdf  # Unseen generalization test document (old)
│   ├── unseen_advisory_new.pdf  # Unseen generalization test document (new)
│   ├── land_record_old.pdf      # Synthetic Patta record 2023
│   ├── land_record_new.pdf      # Synthetic Patta record 2024
│   ├── ground_truth.json        # 22 labeled ground-truth changes
│   ├── benchmark_results.json   # Canonical benchmark results payload
│   └── generate_demo_pdfs.py    # Reproducible benchmark generator
├── evaluation/
│   └── eval.py                  # Precision, recall, and grounding evaluator
├── tests/
│   ├── test_unit.py             # 17 unit tests
│   ├── test_regression.py       # 11 safe normalization & structural alignment tests
│   ├── test_exhaustive.py       # 2 end-to-end benchmark tests
│   ├── test_unseen.py           # Generalization test on unseen advisory document pair
│   ├── test_e2e_workflow.py     # Complete end-to-end API lifecycle workflow test
│   ├── test_api.py              # 5 FastAPI integration tests
│   └── test_strategy.py         # T01-T20 test strategy matrix
├── docs/
│   ├── ARCHITECTURE.md          # Frozen architecture & data contracts
│   ├── SETUP.md                 # Developer setup guide
│   └── AgriDiff_AI_Enhanced_SRS_Presentation.pptx
├── CHANGELOG.md                 # Milestone changelog
├── CONTRIBUTIONS.md             # Verified team contribution model
└── README.md
```


---

## ⚙️ Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows (or source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt

cp .env.example .env        # Add GEMINI_API_KEY if available (has automatic fallback)
uvicorn main:app --reload --port 8000
```
Health Check: `http://localhost:8000/api/health`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open: `http://localhost:3000`

### 3. Run Automated Tests
```bash
python -m pytest tests/ -v
```

### 4. Run Benchmark Evaluation
```bash
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json
```

---

## 🧑‍💻 Team CODEAVENGERS (BIT-AI-001)

| Member | Department | Role | Ownership |
|---|---|---|---|
| **KAVISH S R** | CSE | Team Leader | Architecture, AI/LLM Pipeline, Comparison Engine |
| **GOWSHIKGUNAL R** | CSE | Frontend Lead | React Dashboard, Dual-View Tabs, Evidence UI |
| **PRANESH K V** | AIDS | Data & Evaluation | 22-Change Benchmark, Patta Dataset, Testing |
| **DINESH B** | AIDS | Integration & Release | FastAPI API, Deployment, Documentation, PPT |

---

## 📄 License

MIT License — see [LICENSE](LICENSE)
