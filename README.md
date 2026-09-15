# 🌾 AgriDiff AI
### "Don't just compare documents. Understand what changed."

> **Hackathon:** BIT-AI-001 | **Problem:** AGR-17 | **Team:** CODEAVENGERS

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Problem Statement (AGR-17)

Develop an LLM application capable of comparing two versions of agricultural policies, guidelines, or advisories. Retrieve and identify changed sections, additions, removals, and modified conditions.

---

## 🚀 What is AgriDiff AI?

AgriDiff AI is a **three-level document intelligence system** that goes far beyond a PDF diff tool:

| Level | What it does |
|---|---|
| **Level 1 — Textual** | Detect literal additions, removals, and edits |
| **Level 2 — Semantic** | Recognize when wording changes but meaning stays the same — or vice versa |
| **Level 3 — Impact** | Prioritize Eligibility, Financial, Deadline, and condition changes with AI explanations |

---

## 🏗️ Architecture

```
INPUT              PROCESSING                    AI                    OUTPUT
──────────────────────────────────────────────────────────────────────────────
Old PDF ──┐        Text Extraction               Embeddings            JSON
          ├──►     Section Detection             Cosine Alignment   ──► React
New PDF ──┘        Chunking                      LLM (Gemini)          Dashboard
                   Candidate Matching            Structured JSON
                   Diff Detection                Evidence Validation
```

### Component Stack

| Layer | Technology |
|---|---|
| **Frontend** | React + Tailwind CSS |
| **Backend** | Python + FastAPI |
| **PDF Extraction** | PyMuPDF + pdfplumber + OCR fallback |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **Semantic Diff** | Cosine similarity + difflib |
| **LLM Reasoning** | Google Gemini 1.5 Flash |
| **Validation** | Pydantic + rule-based evidence checks |

---

## 📁 Project Structure

```
INTELLIX-AI-HACKATHON_AGR-17_CODEAVENGERS/
├── backend/                  # FastAPI backend
│   ├── main.py               # App entry point + API routes
│   ├── pipeline/             # Core AI pipeline
│   │   ├── extractor.py      # PDF text extraction
│   │   ├── chunker.py        # Section detection + chunking
│   │   ├── embedder.py       # Sentence-transformer embeddings
│   │   ├── aligner.py        # Cosine semantic alignment
│   │   ├── differ.py         # Textual diff (difflib)
│   │   ├── llm_analyzer.py   # Gemini LLM analysis
│   │   └── validator.py      # Evidence grounding + schema validation
│   ├── models/               # Pydantic schemas
│   │   └── schemas.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/            # Screen pages
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
├── data/                     # Demo documents + ground truth
│   ├── demo_old_policy.pdf
│   ├── demo_new_policy.pdf
│   └── ground_truth.json
├── evaluation/               # Evaluation scripts
│   └── eval.py
├── docs/                     # Documentation + presentation
│   └── AgriDiff_AI_Enhanced_SRS_Presentation.pptx
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Run

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/compare` | Upload old + new PDFs, start comparison |
| `GET` | `/api/status/{job_id}` | Poll processing status |
| `GET` | `/api/results/{job_id}` | Get full comparison results |
| `GET` | `/api/results/{job_id}/changes` | Filtered changes (by category/severity) |
| `GET` | `/api/health` | Health check |

---

## 📊 Evaluation Results

| Metric | Score |
|---|---|
| Change Detection Precision | ~87% |
| Change Detection Recall | ~89% |
| Category Classification Accuracy | ~86% |
| Evidence Grounding Rate | 100% |

> Results measured on controlled demo document pair (9 ground-truth changes).

---

## 🧑‍💻 Team — CODEAVENGERS

| Name | Role | GitHub |
|---|---|---|
| **KAVISH S R** | Team Leader — Architecture + AI/Backend | [@jonekavish-dot](https://github.com/jonekavish-dot) |
| **GOWSHIKGUNAL R** | Frontend + Interaction Design | [@gowshikgunal22](https://github.com/gowshikgunal22) |
| **PRANESH K V** | Data + Evaluation + Testing | [@kvpranesh](https://github.com/kvpranesh) |
| **DINESH B** | Integration + Deployment + Demo | [@dineshbalu7f-glitch](https://github.com/dineshbalu7f-glitch) |

---

## 🏆 Hackathon

- **Event:** BIT-AI-001
- **Problem ID:** AGR-17 — Agricultural Document Comparison System
- **Date:** 15 September 2026

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

