# 🌾 AgriDiff AI
### "Don't just compare documents. Understand what changed."

> **Hackathon:** BIT-AI-001 | **Problem:** AGR-17 | **Team:** CODEAVENGERS  
> **Institution:** Bannari Amman Institute of Technology  
> **Domain:** Agriculture & Rural Development  
> **Status:** Production Release v1.2.0 (Codebase Frozen)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-48%2F48%20Passed-brightgreen)](tests/)
[![Precision](https://img.shields.io/badge/Precision-91.7%25-brightgreen)](evaluation/)
[![Recall](https://img.shields.io/badge/Recall-100.0%25-brightgreen)](evaluation/)
[![F1 Score](https://img.shields.io/badge/F1%20Score-95.7%25-brightgreen)](evaluation/)
[![Evidence Grounding](https://img.shields.io/badge/Grounding-100%25%20Verified-blue)](backend/pipeline/validator.py)
[![Responsive](https://img.shields.io/badge/Cross--Device-Android%20%7C%20iOS%20%7C%20PC-orange)](#-responsive-cross-device-architecture)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Problem Statement (AGR-17)

Agricultural governance documents—including subsidy policy guidelines, operational schemes, seasonal advisories, and revenue land records (patta/chitta)—undergo frequent administrative revisions. Field verification squads, revenue officers, and farmers struggle to locate exact modifications amidst dozens of pages.

**AgriDiff AI** is an evidence-grounded agricultural document comparison and change intelligence system. It does not simply highlight raw diffs; it detects, understands semantic implications, prioritizes field impacts, and proves every claim with verified source quotes.

---

## 🚀 Core Product Innovation: Compare Everything First

Our non-negotiable architectural invariant:
> **The system first performs an EXHAUSTIVE COMPARISON preserving every source-supported difference. Then, as a secondary layer, the IMPACT VIEW prioritizes consequential changes without ever hiding the complete comparison data.**

```
                DOCUMENT PAIR
                     ↓
             EXHAUSTIVE ANALYSIS
                     ↓
               ALL CHANGES
                     ↓
             EVIDENCE VALIDATION
                     ↓
            SEMANTIC INTERPRETATION
                     ↓
              IMPACT CLASSIFICATION
                     ↓
          ┌──────────┴──────────┐
          ↓                     ↓
   ALL CHANGES             IMPACT VIEW
(Every difference)       (Prioritized items)
```

### Three Intelligence Layers + Evidence Grounding

| Level | Intelligence Type | Implementation |
|---|---|---|
| **Level 1 — Textual** | Literal additions, removals, modifications | `difflib` token opcodes + safe whitespace/punctuation normalizer |
| **Level 2 — Semantic** | Meaning-changing vs phrasing equivalence | Structural clause pairing + Sentence-Transformers cosine similarity |
| **Level 3 — Impact** | Domain priority & operational guidance | Bounded Gemini 1.5 Flash analysis + deterministic domain rules |
| **Orthogonal — Evidence** | Quote verification against source text | Exact substring verification (`SUPPORTED`, `UNCERTAIN`, `NOT_FOUND`) |

---

## 🔑 Safe Demo Authentication (Hackathon Layer)

AgriDiff AI includes a lightweight, safe demo authentication mechanism with 1-click access designed specifically for judging evaluation:

| Role | Username | Password | Purpose & Focus |
|---|---|---|---|
| **🌾 Farmer Demo** | `farmer` | `demo123` | Direct access to land-record comparison, subsidy ceilings, and eligibility criteria. |
| **🛡️ Agriculture Officer Demo** | `officer` | `demo123` | Impact priority views, field verification directives, and administrative compliance checklists. |
| **🔍 Reviewer / Auditor Demo** | `reviewer` | `demo123` | Complete audit trail, multi-span grounding verification, and benchmark evaluation metrics. |

> **Safety Notice:** These accounts are synthetic demo profiles intended solely for hackathon demonstration. No real personal identities, government records, or plain-text credentials are used or stored.

---

## 📱 Responsive Cross-Device Architecture

AgriDiff AI is engineered as a unified, fluid web application that automatically reflows across all viewports without horizontal scrolling or clipped content:

* **Mobile Phones (320px – 767px):** Android & iOS touch-optimized UI. Compact header, stacked upload zones, touch-friendly file replace/remove controls, mobile drawer filters, card reflow for land records, and toggleable evidence viewing.
* **Tablets (768px – 1023px):** Fluid multi-column layout with touch targets ≥ 44px.
* **Desktops & Large Monitors (1024px – 1920px+):** Full side-by-side comparative views, persistent sticky filter sidebar, detailed 6-column land record table, and side-by-side evidence inspection.

---

## 📜 Structured Land Record Intelligence

AgriDiff AI features a specialized, deterministic extractor for agricultural land records and patta documents:
* **Land Area / Holding Limit:** Tracks acre/hectare modifications (e.g., `2 acres → 4 acres`, `2 ha → 5 ha`).
* **Survey / Subdivision Numbers:** Identifies land partition changes (e.g., `123 → 123/2`).
* **Patta / Recorded Holders:** Tracks ownership name updates (`ABC → XYZ`).
* **Verifying Authorities:** Identifies authority changes (`Revenue Inspector → Tahsildar`).
* **Verification & Transaction Dates:** Detects added or revised attestation dates (`15-10-2026`).

---

## 📊 Benchmark Evaluation Matrix

Evaluated using [`evaluation/eval.py`](evaluation/eval.py) against the canonical [`data/ground_truth.json`](data/ground_truth.json) (22 ground-truth policy changes):

| Metric | v1.0.0 Baseline | v1.2.0 Final Release | Status |
|---|---|---|---|
| **Ground Truth Changes** | 22 | 22 | Canonical baseline |
| **Detected Changes** | 36 | 24 | Complete comparison |
| **True Positives (TP)** | 18 | **22** | **100.0% Recall** |
| **False Positives (FP)** | 18 | **2** | **88.9% Reduction** |
| **False Negatives (FN)** | 4 | **0** | **Zero Missed Changes** |
| **Precision** | 50.0% | **91.7%** | **+41.7% Absolute Gain** |
| **Recall** | 81.8% | **100.0%** | **100.0% Detection** |
| **F1 Score** | 62.1% | **95.7%** | **+33.6% Absolute Gain** |
| **Category Accuracy** | 100.0% | **100.0%** | Perfect Score |
| **Impact Accuracy** | 38.9% | **100.0%** | Perfect Score |
| **Change Type Accuracy**| 22.2% | **100.0%** | Perfect Score |
| **Evidence Grounding** | 100.0% | **100.0%** | 24/24 Verified Grounded |
| **Automated Test Suite** | 27 / 27 | **48 / 48 Passed** | **100% Pass Rate** |

---

## 🛠️ Quick Run Instructions

### 1. Backend Server (FastAPI)
```bash
# From project root:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
* Health check: `http://127.0.0.1:8000/api/health`
* Interactive docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Application (React + Vite)
```bash
# In frontend directory:
cd frontend
npm install
npm run dev
```
* Application URL: `http://localhost:3000`

### 3. Run Automated Tests
```bash
python -m pytest -v
```

### 4. Run Benchmark Evaluation
```bash
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json
```

---

## 👥 Team CODEAVENGERS (BIT-AI-001)

| Member | Role & Department | Ownership |
|---|---|---|
| **KAVISH S R** | Team Leader / CSE | System Architecture, Comparison Pipeline, Safe Normalizer, Auth API |
| **GOWSHIKGUNAL R** | Frontend Lead / CSE | Responsive UI, Dual Views, Demo Login, Evidence Modal, Land Record Cards |
| **PRANESH K V** | Data & Evaluation / AIDS | 48-Test Pytest Suite, Benchmark Ground Truth, Unseen Generalization Dataset |
| **DINESH B** | Integration & Release / AIDS | FastAPI Services, Failure Mode Hardening, Build Verification, Documentation |

---

## ⚠️ Known Limitations
1. Scanned PDFs containing solely low-resolution handwritten text depend on local Tesseract OCR; complex cursive scripts may have lower character confidence.
2. Large PDFs exceeding 50 MB are rejected at intake to preserve system responsiveness in concurrent hackathon environments.
