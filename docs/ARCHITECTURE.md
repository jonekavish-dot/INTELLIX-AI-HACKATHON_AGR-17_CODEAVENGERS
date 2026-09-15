# AgriDiff AI — Architecture Reference (FROZEN v1.2.0)
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

> This document is the finalized, frozen architecture reference for the AgriDiff AI platform.
> All components have been implemented, tested, and released.

---

## Core Product Principle

> **Don't just compare documents. Understand what changed.**

The system performs an **EXHAUSTIVE COMPARISON** first.
The **IMPACT VIEW** is a secondary prioritization layer on top — it never hides information.

```
OLD DOCUMENT + NEW DOCUMENT
        ↓
EXHAUSTIVE COMPARISON         ← Every detectable difference (24 changes)
        ↓
ALL DETECTED CHANGES
        ↓
EVIDENCE VALIDATION           ← Source-supported substring verification
        ↓
SEMANTIC INTERPRETATION       ← Meaning vs phrasing equivalence
        ↓
IMPACT CLASSIFICATION         ← Domain priority (High / Medium / Low)
        ↓
┌──────────────────────┬──────────────────────┬──────────────────────┐
│  ALL CHANGES VIEW    │     IMPACT VIEW      │ STRUCTURED & PATTA   │
│  Every change        │  Consequential only  │ Land record cards    │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

---

## Three Intelligence Layers + Evidence Grounding

| Layer | What | How |
|---|---|---|
| **TEXTUAL** | Literal additions, removals, edits | `difflib` + safe whitespace/punctuation normalizer |
| **SEMANTIC** | Meaning change vs wording only | Cosine similarity with Sentence-Transformers embeddings |
| **IMPACT** | Priority classification + explanation | Bounded Gemini 1.5 Flash + deterministic agricultural rules |
| **EVIDENCE** | Grounding verification against source text | Deterministic quote substring verification (`SUPPORTED`) |

---

## Technology Stack (COMPLETED & FROZEN)

| Layer | Technology | Status |
|---|---|---|
| **Backend Framework** | Python 3.10+ & FastAPI | ✅ Completed |
| **Frontend Client** | React 18, Tailwind CSS, Vite | ✅ Completed |
| **Authentication Layer** | Demo Auth (`/api/auth/login`) + Role Sessions | ✅ Completed |
| **Responsive Design** | Fluid CSS / Flex / Grid (320px – 1920px+) | ✅ Completed |
| **PDF Extraction** | PyMuPDF + pdfplumber | ✅ Completed |
| **OCR Fallback** | pytesseract | ✅ Completed |
| **Embeddings** | sentence-transformers `all-MiniLM-L6-v2` | ✅ Completed |
| **Semantic Alignment** | Structural Clause Pairing + Cosine Match | ✅ Completed |
| **Textual Diff** | Python `difflib` + Safe Normalization | ✅ Completed |
| **LLM Analysis** | Google Gemini 1.5 Flash (Deterministic Rules fallback) | ✅ Completed |
| **Land Record Extraction**| Deterministic regex & administrative entity parser | ✅ Completed |
| **Evidence Validation** | Deterministic substring grounding & multi-span fragments | ✅ Completed |
| **Dual View Presentation**| Exhaustive, Impact, and Structured Land Record Views | ✅ Completed |
| **Automated Test Suite** | Pytest (48 / 48 tests passing) | ✅ Completed |
| **Benchmark Evaluation** | Canonical ground-truth evaluation script (`eval.py`) | ✅ Completed |

---

## Data Contract (Schemas)

All API responses conform to strict Pydantic schemas in `backend/models/schemas.py`:

```json
{
  "job_id": "test-job-sync-01",
  "status": "completed",
  "processing_time_seconds": 0.12,
  "documents": {
    "old": { "filename": "demo_old_policy.pdf", "pages": 2, "chunks": 23 },
    "new": { "filename": "demo_new_policy.pdf", "pages": 2, "chunks": 26 }
  },
  "summary": {
    "total_all_changes": 24,
    "total_impact_changes": 19,
    "total_field_changes": 6,
    "by_severity": { "HIGH": 8, "MEDIUM": 11, "LOW": 5 },
    "by_category": { "Eligibility": 5, "Financial": 4, ... }
  },
  "all_changes": [
    {
      "change_id": "CH-001",
      "section": "1. ELIGIBILITY CRITERIA",
      "change_type": "MODIFIED",
      "category": "Eligibility",
      "field": "land_area",
      "old_value": "2 hectares",
      "new_value": "5 hectares",
      "summary": "Land holding ceiling expanded from 2 hectares to 5 hectares.",
      "operational_note": "Land Area / Holding Limit changed from '2 hectares' to '5 hectares'.",
      "impact": "HIGH",
      "evidence_status": "SUPPORTED",
      "confidence": 0.98,
      "evidence_spans": [...]
    }
  ],
  "impact_changes": [ ... ],
  "field_changes": [ ... ],
  "evaluation": { ... }
}
```
