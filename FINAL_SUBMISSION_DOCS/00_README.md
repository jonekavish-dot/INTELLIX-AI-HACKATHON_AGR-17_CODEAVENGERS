# 🌾 AgriDiff AI
### *"Don't just compare documents. Understand what changed."*

> **Hackathon:** BIT-AI-001 | **Problem:** AGR-17 | **Team:** CODEAVENGERS
> **Institution:** Bannari Amman Institute of Technology
> **Domain:** Agriculture & Rural Development
> **Status:** 🟢 Production Release v1.2.0 — Deployed & Cloud-Ready

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Vite](https://img.shields.io/badge/Build-Vite%205-646CFF?logo=vite)](https://vitejs.dev)
[![Tests](https://img.shields.io/badge/Tests-48%2F48%20Passed-brightgreen)](tests/)
[![Precision](https://img.shields.io/badge/Precision-91.7%25-brightgreen)](evaluation/)
[![Recall](https://img.shields.io/badge/Recall-100.0%25-brightgreen)](evaluation/)
[![F1 Score](https://img.shields.io/badge/F1%20Score-95.7%25-brightgreen)](evaluation/)
[![Evidence Grounding](https://img.shields.io/badge/Grounding-100%25%20Verified-blue)](backend/pipeline/validator.py)
[![Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](docs/DEPLOYMENT.md)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)](docs/DEPLOYMENT.md)
[![Responsive](https://img.shields.io/badge/Cross--Device-Android%20%7C%20iOS%20%7C%20PC-orange)](#-responsive-cross-device-architecture)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Problem Statement (AGR-17)

Agricultural governance documents — subsidy policy gazettes, seasonal operational schemes, irrigation advisories, and revenue land records (patta/chitta) — undergo frequent administrative revisions. Field verification squads, revenue officers, and farmers struggle to locate exact modifications across dozens of dense pages.

**AgriDiff AI** is an evidence-grounded agricultural document comparison and change intelligence engine. It doesn't merely highlight raw diffs — it **detects, understands semantic implications, prioritizes field impacts, and proves every claim with verified source quotes**.

---

## 🚀 Core Innovation: Exhaustive Comparison First

> **The system first performs an EXHAUSTIVE COMPARISON preserving every source-supported difference. Then, as a secondary layer, the IMPACT VIEW prioritizes consequential changes — without ever hiding the complete comparison data.**

```
              DOCUMENT PAIR (Old PDF + New PDF)
                          ↓
                 EXHAUSTIVE ANALYSIS
              (Every clause, value, date)
                          ↓
               EVIDENCE GROUNDING
           (Exact quote verification)
                          ↓
            SEMANTIC INTERPRETATION
           (Meaning-change vs reword)
                          ↓
             IMPACT CLASSIFICATION
              (HIGH / MEDIUM / LOW)
                          ↓
            ┌─────────────┴────────────┐
            ↓                          ↓
     ALL CHANGES                 IMPACT VIEW
  (Every difference)       (Prioritized field items)
            ↓
   STRUCTURED LAND RECORDS
 (Survey No, Area, Holder, Verifier)
```

### Three Intelligence Layers + Evidence Grounding

| Level | Intelligence Type | Implementation |
|---|---|---|
| **Level 1 — Textual** | Literal additions, removals, modifications | `difflib` token opcodes + safe whitespace/punctuation normalizer |
| **Level 2 — Semantic** | Meaning-changing vs phrasing equivalence | Structural clause pairing + TF-IDF cosine similarity |
| **Level 3 — Impact** | Domain priority & operational guidance | Bounded Gemini 1.5 Flash + deterministic domain rules |
| **Orthogonal — Evidence** | Quote verification against source text | Exact substring match (`SUPPORTED` / `UNCERTAIN` / `NOT_FOUND`) |

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Dual View Engine** | Tab 1: Exhaustive (all 24 changes) · Tab 2: Consequential Impact only |
| 📋 **Operational Notes** | Dual-format: Declarative Shift + ⚡ Action Required Directive |
| 📜 **Structured Land Records** | Specialized patta/chitta field extractor (Tab 3) |
| 🔬 **Evidence Modal** | Side-by-side exact source quote verification with page numbers |
| 🔑 **Demo Authentication** | 3 role-based 1-click login accounts |
| 📱 **Fully Responsive** | Android · iOS · Tablet · PC (320px → 1920px+) |
| ☁️ **Cloud-Ready** | Render (backend) + Vercel (frontend) — zero-config deploy |
| 🛡️ **Graceful Fallback** | Works without Gemini API (deterministic mode) |

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Focus |
|---|---|---|---|
| 🌾 **Farmer** | `farmer` | `demo123` | Land records, subsidy ceilings, eligibility criteria |
| 🛡️ **Agriculture Officer** | `officer` | `demo123` | Impact priority, field directives, compliance checklists |
| 🔍 **Reviewer / Auditor** | `reviewer` | `demo123` | Full audit trail, grounding verification, benchmark metrics |

> *Click any **Quick Sign In** button on the login screen — no manual typing needed.*

---

## 📊 Benchmark Evaluation Matrix

Evaluated via [`evaluation/eval.py`](evaluation/eval.py) against [`data/ground_truth.json`](data/ground_truth.json) (22 annotated ground-truth policy changes):

| Metric | v1.0.0 Baseline | v1.2.0 Final | Status |
|---|---|---|---|
| Ground Truth Changes | 22 | 22 | Canonical |
| Detected Changes | 36 | 24 | Precision-optimized |
| True Positives | 18 | **22** | ✅ |
| False Positives | 18 | **2** | 88.9% reduction |
| False Negatives | 4 | **0** | Zero missed |
| **Precision** | 50.0% | **91.7%** | +41.7% gain |
| **Recall** | 81.8% | **100.0%** | Perfect |
| **F1 Score** | 62.1% | **95.7%** | +33.6% gain |
| Category Accuracy | 100.0% | **100.0%** | ✅ |
| Impact Accuracy | 38.9% | **100.0%** | ✅ |
| Change Type Accuracy | 22.2% | **100.0%** | ✅ |
| Evidence Grounding | 100.0% | **100.0%** | 24/24 verified |
| Automated Test Suite | 27/27 | **48/48 Passed** | ✅ |

---

## 🛠️ Quick Start (Local)

### Backend (FastAPI)
```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
copy .env.example.txt .env    # Windows
cp .env.example.txt .env      # Linux / macOS
# (Optional) add your GEMINI_API_KEY to .env

# 4. Start server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Health: `http://127.0.0.1:8000/api/health`
- Swagger: `http://127.0.0.1:8000/docs`

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Tests & Evaluation
```bash
# All 48 tests
python -m pytest -v

# Benchmark precision/recall
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json

# Production build
cd frontend && npm run build
```

---

## ☁️ Cloud Deployment

| Platform | Component | Config |
|---|---|---|
| **Render** | FastAPI Backend | `render.yaml` (Blueprint included) |
| **Vercel** | React Frontend | `frontend/vercel.json` (SPA rewrites included) |

**Backend (Render):**
- Build: `pip install -r backend/requirements.txt`
- Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/health`

**Frontend (Vercel):**
- Root Directory: `frontend`
- Build Command: `npm run build`
- Env Var: `VITE_API_URL=https://your-backend.onrender.com`

📖 Full guide: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

---

## 📱 Responsive Cross-Device Architecture

| Viewport | Experience |
|---|---|
| **Mobile (320–767px)** | Touch-optimized, stacked upload zones, drawer filters, card reflow |
| **Tablet (768–1023px)** | Fluid multi-column, ≥44px touch targets |
| **Desktop (1024px+)** | Side-by-side evidence, sticky sidebar, 6-column land record table |

---

## 📜 Structured Land Record Intelligence

Specialized deterministic extractor for patta/chitta agricultural land documents:

| Field | Example Change |
|---|---|
| Land Area / Holding Limit | `2 ha → 5 ha` |
| Survey / Subdivision Number | `123 → 123/2` |
| Patta Holder Name | `ABC → XYZ` |
| Verifying Authority | `Revenue Inspector → Tahsildar` |
| Verification / Transaction Date | `(absent) → 15-10-2026` |

---

## 📚 Documentation Hub

| # | Document | Description |
|---|---|---|
| 00 | [README.md](README.md) | Project overview (this file) |
| 01 | [docs/SETUP.md](docs/SETUP.md) | Reproducible local setup |
| 02 | [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md) | Full Python + Node package inventory |
| 03 | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Render & Vercel cloud deployment |
| 04 | [docs/INSTALLATION_TROUBLESHOOTING.md](docs/INSTALLATION_TROUBLESHOOTING.md) | Fix venv, ports, OCR, API errors |
| 05 | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline architecture deep-dive |
| 06 | [docs/WORKFLOW.md](docs/WORKFLOW.md) | End-to-end workflow walkthrough |
| 07 | [project_inventory/NON_GIT_ARTIFACTS.txt](project_inventory/NON_GIT_ARTIFACTS.txt) | Non-git exclusion inventory |
| 08 | [project_inventory/CONFIGURATION_INVENTORY.txt](project_inventory/CONFIGURATION_INVENTORY.txt) | Config & env variable catalog |
| 09 | [.env.example.txt](.env.example.txt) | Environment template |
| 10 | [render.yaml](render.yaml) | Render 1-click Blueprint |
| 11 | [CHANGELOG.md](CHANGELOG.md) | Version history |
| 12 | [CONTRIBUTIONS.md](CONTRIBUTIONS.md) | Team authorship |
| 📁 | [FINAL_SUBMISSION_DOCS/](FINAL_SUBMISSION_DOCS/) | All docs in one indexed folder |

---

## 👥 Team CODEAVENGERS (BIT-AI-001)

| Member | GitHub | Role | Ownership |
|---|---|---|---|
| **KAVISH S R** | `jonekavish-dot` | Team Leader / CSE | Architecture, Backend Pipeline, Auth API, Render Deploy |
| **GOWSHIKGUNAL R** | `gowshikgunal22` | Frontend Lead / CSE | React UI, Responsive Design, Operational Notes UI |
| **PRANESH K V** | `kvpranesh` | Data & Evaluation / AIDS | 48-Test Suite, Benchmark Ground Truth, Generalization |
| **DINESH B** | `dineshbalu7f-glitch` | Integration & Release / AIDS | DevOps, Docs, Vercel Deploy, Setup Verification |

---

## ⚠️ Known Limitations

1. Scanned PDFs with handwritten text depend on optional Tesseract OCR — digital PDFs extract perfectly without it.
2. PDFs exceeding 50 MB are rejected at intake to preserve responsiveness.
3. Neural transformer embeddings (`sentence-transformers`) are disabled by default on cloud Free tier (512 MB RAM limit). The built-in TF-IDF pipeline maintains identical benchmark scores.
