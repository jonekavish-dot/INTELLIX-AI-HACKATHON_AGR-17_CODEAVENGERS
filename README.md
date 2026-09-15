# 🌾 AgriDiff AI
### "Don't just compare documents. Understand what changed."

> **Hackathon:** BIT-AI-001 | **Problem:** AGR-17 | **Team:** CODEAVENGERS  
> **Institution:** Bannari Amman Institute of Technology  
> **Domain:** Agriculture & Rural Development

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-27%2F27%20Passed-brightgreen)](tests/)
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
  EVIDENCE VALIDATION            ← Strict quote verification (Anti-hallucination)
            ↓
  SEMANTIC INTERPRETATION        ← Distinguishes rewording from meaning change
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
| **Level 1 — Textual** | Literal additions, removals, deletions | `difflib` word-level opcodes |
| **Level 2 — Semantic** | Meaning-changing vs wording-only changes | Cosine similarity + Semantic embeddings |
| **Level 3 — Impact** | Domain priority & farmer impact analysis | Gemini 1.5 Flash + Deterministic rules |
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

## 📊 Benchmark Evaluation Results (22 Known Changes)

Tested against the 22-change controlled ground-truth benchmark (`data/ground_truth.json`):

| Evaluation Metric | Score | Benchmark Requirement |
|---|---|---|
| **True Positives** | **18 / 22** | Exhaustive coverage |
| **Recall** | **81.8%** | High sensitivity across clauses |
| **Category Accuracy** | **100.0%** | Domain classification |
| **Evidence Grounding Rate** | **100.0%** | 36 / 36 passages verified |
| **Average Confidence** | **91.4%** | Bounded reasoning |
| **Automated Test Suite** | **27 / 27 Passed (100%)** | Unit, API & Integration |

---

## 📁 Project Structure

```
INTELLIX-AI-HACKATHON_AGR-17_CODEAVENGERS/
├── backend/
│   ├── main.py                  # FastAPI app + routes + demo presets
│   ├── pipeline/
│   │   ├── extractor.py         # PyMuPDF + pdfplumber + OCR
│   │   ├── chunker.py           # Clause-level section detection
│   │   ├── embedder.py          # Unified pair embedding & sentence-transformers
│   │   ├── aligner.py           # Cosine greedy alignment (Exhaustive)
│   │   ├── differ.py            # Word-level textual differ
│   │   ├── entity_extractor.py  # Patta & land record field comparator
│   │   ├── llm_analyzer.py      # Gemini 1.5 Flash with strict grounding
│   │   └── validator.py         # Dual-view aggregator & quote verifier
│   ├── models/
│   │   └── schemas.py           # Canonical Pydantic contracts
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChangeCard.jsx   # Canonical cards with clause & evidence tags
│   │   │   ├── EvidenceModal.jsx# Side-by-side evidence with yellow highlights
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
│   ├── land_record_old.pdf      # Synthetic Patta record 2023
│   ├── land_record_new.pdf      # Synthetic Patta record 2024
│   ├── ground_truth.json        # 22 labeled ground-truth changes
│   └── generate_demo_pdfs.py    # Reproducible benchmark generator
├── evaluation/
│   └── eval.py                  # Precision, recall, and grounding evaluator
├── tests/
│   ├── test_unit.py             # 17 unit tests
│   ├── test_api.py              # 5 FastAPI integration tests
│   ├── test_exhaustive.py       # 2 end-to-end benchmark tests
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
