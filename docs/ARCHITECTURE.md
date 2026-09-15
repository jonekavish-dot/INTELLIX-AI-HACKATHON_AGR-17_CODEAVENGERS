# AgriDiff AI — Architecture Reference
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

> This document is the frozen architecture reference for the hackathon build.
> Do NOT modify the architecture without team consensus.

---

## Core Product Principle

> **Don't just compare documents. Understand what changed.**

The system performs an **EXHAUSTIVE COMPARISON** first.
The **IMPACT VIEW** is a secondary prioritization layer on top — it never hides information.

```
OLD DOCUMENT + NEW DOCUMENT
        ↓
EXHAUSTIVE COMPARISON         ← every detectable difference
        ↓
ALL DETECTED CHANGES
        ↓
EVIDENCE VALIDATION           ← source-supported only
        ↓
SEMANTIC INTERPRETATION       ← meaning vs wording
        ↓
IMPACT CLASSIFICATION         ← domain priority
        ↓
┌──────────────────────┐   ┌──────────────────────┐
│  ALL CHANGES VIEW    │   │  IMPACT VIEW          │
│  Every change        │   │  Consequential only   │
└──────────────────────┘   └──────────────────────┘
```

---

## Three Intelligence Layers

| Layer | What | How |
|---|---|---|
| **TEXTUAL** | Literal additions, removals, edits | `difflib` — deterministic |
| **SEMANTIC** | Meaning change vs wording only | Cosine similarity — deterministic threshold |
| **IMPACT** | Priority classification + explanation | LLM (Gemini 1.5 Flash) — bounded by evidence |

Plus an orthogonal **EVIDENCE** layer:
- Every result carries `old_evidence`, `new_evidence`, `old_page`, `new_page`
- Evidence is validated as a source substring before display
- If not found: `INSUFFICIENT_EVIDENCE` — never silently dropped

---

## Full Pipeline

```
PDF Upload (old + new)
     ↓
Page-Aware Extraction         extractor.py   [PyMuPDF → pdfplumber → OCR]
     ↓
Structure Detection           chunker.py     [regex headers + paragraph split]
     ↓
Chunking (400 tokens, 50 overlap)
     ↓
Sentence Embeddings           embedder.py    [all-MiniLM-L6-v2 | TF-IDF fallback]
     ↓
Semantic Alignment            aligner.py     [cosine similarity matrix, greedy match]
     ↓
Textual Diff                  differ.py      [difflib word-level]
     ↓
Entity Extraction             [TO BUILD]     [numeric, date, name, survey, area]
     ↓
Exhaustive Change Detection   [TO BUILD]     [ALL pairs → change records]
     ↓
LLM Semantic Analysis         llm_analyzer.py [Gemini 1.5 Flash, 3 prompts]
     ↓
Evidence Validation           validator.py   [substring check, NOT_FOUND/UNCERTAIN]
     ↓
Impact Classification         [LLM output + deterministic boost]
     ↓
Canonical JSON                schemas.py     [Pydantic]
     ↓
Dashboard                     React          [All Changes + Impact View]
```

---

## Canonical Change Object

This is the SINGLE shared contract. Backend, frontend, tests, and evaluation all use this.

```json
{
  "change_id":       "CH-001",
  "section":         "ELIGIBILITY CRITERIA",
  "subsection":      "1.1",
  "change_type":     "MODIFIED | ADDED | REMOVED | UNCHANGED | SEMANTICALLY_EQUIVALENT",
  "category":        "Eligibility | Financial | Deadline | Documentation | Procedure | Beneficiary | LandRecord | Other",
  "field":           "land_area | survey_number | holder | verifier | deadline | subsidy_amount | ...",
  "old_value":       "2 acres",
  "new_value":       "4 acres",
  "old_text":        "Full source passage from old document",
  "new_text":        "Full source passage from new document",
  "old_page":        1,
  "new_page":        1,
  "summary":         "Land area increased from 2 acres to 4 acres",
  "interpretation":  "The stated holding increased. The system does not infer ownership.",
  "impact":          "HIGH | MEDIUM | LOW",
  "evidence_status": "SUPPORTED | INSUFFICIENT_EVIDENCE | NOT_FOUND | UNCERTAIN",
  "confidence":      0.97
}
```

### Evidence Status Semantics

| Value | Meaning |
|---|---|
| `SUPPORTED` | Evidence quote verified as substring of source text |
| `INSUFFICIENT_EVIDENCE` | LLM could not cite specific supporting text |
| `NOT_FOUND` | Field is completely absent from the document |
| `UNCERTAIN` | Information present but relationship/meaning is ambiguous |

### Change Type Semantics

| Value | Meaning |
|---|---|
| `ADDED` | Present in new, absent in old |
| `REMOVED` | Present in old, absent in new |
| `MODIFIED` | Present in both, content meaningfully changed |
| `UNCHANGED` | Present in both, identical or equivalent |
| `SEMANTICALLY_EQUIVALENT` | Different wording, same meaning |

---

## Anti-Hallucination Controls

1. LLM receives ONLY the specific old/new text passages — no external knowledge
2. Prompt explicitly forbids inferring facts not in the text
3. If evidence is not present: return `NOT_FOUND` or `UNCERTAIN` — never fabricate
4. All LLM-cited evidence validated as source substring post-hoc
5. Failed validation → evidence replaced with actual source text
6. Numeric/date changes validated deterministically (regex) independently of LLM
7. JSON schema validated before acceptance; invalid → retry → deterministic fallback

---

## Entity Fields Supported

The system should extract and compare field-level values where present:

| Field | Type | Extraction |
|---|---|---|
| `owner / holder / patta_holder` | name | NLP / regex |
| `transferor / transferee` | name | NLP / regex (only if explicit) |
| `land_area` | numeric + unit | regex (acres, hectares, cents) |
| `survey_number` | string | regex |
| `subdivision_number` | string | regex |
| `village / taluk / district` | name | NLP |
| `verification_date` | date | regex |
| `transaction_date` | date | regex (only if explicit in source) |
| `document_number` | string | regex |
| `authority / verifier` | name | NLP |
| `verifier_designation` | string | NLP |
| `subsidy_amount` | numeric + currency | regex |
| `percentage` | numeric | regex |
| `deadline` | date | regex |
| `mandatory_documents` | list | NLP |

---

## API Contract

```
POST /api/compare          Upload old + new PDFs → job_id
GET  /api/status/{job_id}  Poll progress (0–100%)
GET  /api/results/{job_id} Full result JSON (all_changes + impact_changes)
GET  /api/results/{job_id}/changes?view=all|impact&category=X&severity=Y
GET  /api/health           Health check
```

### Result JSON Top Level

```json
{
  "job_id": "...",
  "status": "completed",
  "processing_time_seconds": 23.4,
  "documents": { "old": {...}, "new": {...} },
  "summary": {
    "total_textual_differences": 24,
    "total_all_changes": 20,
    "total_impact_changes": 9,
    "added": 2, "removed": 1, "modified": 12,
    "unchanged": 5, "semantically_equivalent": 0,
    "by_severity": { "HIGH": 3, "MEDIUM": 4, "LOW": 2 },
    "by_category": { "Eligibility": 2, ... }
  },
  "all_changes": [ ... ],
  "impact_changes": [ ... ],
  "field_changes": [ ... ],
  "evaluation": { ... }
}
```

---

## Technology Stack (FROZEN)

| Layer | Technology | Status |
|---|---|---|
| Backend | Python 3.10 + FastAPI | ✅ Implemented |
| Frontend | React 18 + Tailwind CSS + Vite | ✅ Implemented |
| PDF Extraction | PyMuPDF + pdfplumber | ✅ Implemented |
| OCR | pytesseract | ✅ Implemented (fallback) |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | ✅ Implemented |
| Semantic Alignment | scikit-learn cosine similarity | ✅ Implemented |
| Textual Diff | Python difflib | ✅ Implemented |
| LLM | Google Gemini 1.5 Flash | ✅ Implemented |
| Schema Validation | Pydantic v2 | ✅ Implemented |
| Evidence Validation | Deterministic substring check | ✅ Implemented |
| Entity Extraction | regex + rules | ⬜ TO BUILD |
| Exhaustive Comparison | All-pairs output (no filter) | ⬜ TO BUILD |
| Field-level comparison | Structured entity diff | ⬜ TO BUILD |
| All Changes / Impact tabs | Dual-mode frontend | ⬜ TO BUILD |
| Test Suite | pytest + httpx | ⬜ TO BUILD |

**DO NOT change any technology in the IMPLEMENTED column.**

---

## What NOT to Build

- Authentication / login
- Multi-format input (Word, Excel) — PDF only
- Fine-tuning any model
- Vector databases (Pinecone, Weaviate) — in-memory is sufficient
- Multi-agent systems
- Mobile responsiveness
- Real-time collaboration
- Microservices
- Blockchain
