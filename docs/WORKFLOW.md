# 🔄 AgriDiff AI — System & Demonstration Workflow
**Problem Statement:** AGR-17 — Agricultural Document Comparison System  
**Institution:** Bannari Amman Institute of Technology  
**Team:** CODEAVENGERS (Team ID: BIT-AI-001)

---

## 1. System Operational Pipeline Workflow

```
[ INPUT ]
Old Document PDF + New Document PDF
     │
     ▼
[ STAGE 1: Page-Aware Extraction (extractor.py) ]
Extract text while preserving exact page boundaries (p.1, p.2).
PyMuPDF (fitz) primary ➔ pdfplumber fallback ➔ Tesseract OCR fallback if scanned.
     │
     ▼
[ STAGE 2: Clause-Level Structuring (chunker.py) ]
Detect headers ('1. ELIGIBILITY', 'CHAPTER', 'SECTION', ALL CAPS).
Granular splitting on numbered subclauses (1.1, 1.2, 2.1) and list items (a, b).
     │
     ▼
[ STAGE 3: Structured Entity Extraction (entity_extractor.py) ]
Extract land area (acres/ha), survey numbers (123, 123/2), recorded holders, verifiers.
Enforce strict anti-hallucination: absent fields = NOT_FOUND; ambiguous = UNCERTAIN; direct = SUPPORTED.
     │
     ▼
[ STAGE 4: Semantic Alignment (aligner.py & embedder.py) ]
Generate joint sentence embeddings in identical feature spaces.
Greedy cosine similarity matching:
  • Similarity >= 0.95 ➔ SEMANTICALLY_EQUIVALENT (reworded, same meaning)
  • Exact text match   ➔ UNCHANGED
  • Similarity < 0.95  ➔ MODIFIED
  • Unmatched old      ➔ REMOVED
  • Unmatched new      ➔ ADDED
     │
     ▼
[ STAGE 5: Textual Differencing (differ.py) ]
Compute word-level diff opcodes using Python difflib (Level 1 intelligence).
     │
     ▼
[ STAGE 6: Bounded LLM Interpretation (llm_analyzer.py) ]
Gemini 1.5 Flash provides domain categorization, impact explanation, and evidence quotes.
Strict prompt bounds: LLM only sees isolated text; deterministic fallback on timeout.
     │
     ▼
[ STAGE 7: Evidence Verification & Assembly (validator.py) ]
Verify cited evidence quotes as literal substrings of source text.
Replace hallucinated quotes with raw source text and tag UNCERTAIN.
Construct dual views:
  • all_changes: Complete exhaustive difference record.
  • impact_changes: Prioritized consequential (HIGH/MEDIUM) changes.
  • field_changes: Tabular structured land record differences.
     │
     ▼
[ OUTPUT ]
Interactive React 18 Dashboard with Tri-Tab Navigation & Side-by-Side Evidence Modal
```

---

## 2. Judge Demonstration Workflow (3-Minute Script)

Use this exact sequence during judging for maximum technical credibility:

### Minute 0:00 – 0:45: The Problem & The Core Innovation
* **Hook:** *"Most document diff tools merely highlight colored text, while generic RAG systems hallucinate when comparing contracts or policies. AgriDiff AI introduces three-level intelligence: Textual, Semantic, and Impact."*
* **Core Rule:** *"Judges, our most important architectural rule: We never hide information. AgriDiff AI first performs an **Exhaustive Comparison** capturing every source difference, and then provides an **Impact View** on top for decision-makers."*

### Minute 0:45 – 1:45: Live Demonstration — 22-Change Policy Scheme
1. Open `http://localhost:3000`.
2. Click **🌾 Policy Scheme (22 Changes)**.
3. Highlight the live pipeline stepper moving through extraction, alignment, and evidence verification.
4. On the **Results Dashboard**, show:
   * **Stats Bar:** 36 exhaustive differences detected, 100% evidence grounding verified.
   * **Exhaustive Comparison Tab:** Show every granular subclause (e.g. Clause 1.1 land holding, Clause 1.2 income ceiling, Clause 1.4 age limit, Clause 2.1 seasonal subsidy).
   * **Impact View Tab:** Click tab — show only HIGH/MEDIUM consequential items (tenant farmers added, solar subsidy raised from 40% to 50%, deadline extended from 30-09 to 15-10).
   * **Evidence Modal:** Click **View Source Evidence** on any change. Point out:
     * Side-by-side Old vs New passage.
     * **Yellow highlight** showing exact verified quote in source text.
     * Page number badges (`Page 1 ➔ Page 1`).
     * `SUPPORTED` evidence status badge.

### Minute 1:45 – 2:30: Live Demonstration — Patta & Land Record Intelligence
1. Click **New Comparison** ➔ Click **📜 Patta & Land Record Pair**.
2. Click the **Structured & Land Records** tab.
3. Show the tabular output:
   * **Survey Number:** `123 → 123/2` (Subdivision tracked).
   * **Land Area:** `2 acres → 4 acres` (Consolidation tracked).
   * **Patta Holder:** `ABC → XYZ` (Recorded title change).
   * **Verifier Designation:** `Revenue Inspector → Tahsildar`.
   * **Verification Date:** `NOT_FOUND → 15-10-2026`.
4. Emphasize: *"Notice that our system flags absent dates as `NOT_FOUND` and never hallucinates a transaction or buyer/seller relationship. It strictly reports what is supported by evidence."*

### Minute 2:30 – 3:00: Verification & Technical Rigor
* Point to the evaluation report: **81.8% Recall, 100% Grounding Rate**.
* Point to test suite: **27 / 27 Automated Tests Passing** in under 5 seconds.
* Conclude: *"AgriDiff AI is dependable, exhaustive, evidence-grounded, and hackathon-ready."*

---

## 3. Testing & Evaluation Workflow

### Run All 27 Automated Tests
```bash
python -m pytest tests/ -v
```

### Run Benchmark Evaluation Script
```bash
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json
```

### Regenerate Benchmark PDF Datasets
```bash
python data/generate_demo_pdfs.py
```

### Verify Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 4. Git & Branching Strategy

| Branch | Purpose | Role |
|---|---|---|
| `main` | Production / Demo Release | Protected stable baseline |
| `dev` | Team Integration | Fast-forward merge from feature branches |
| `feature/backend-pipeline` | Backend & AI Pipeline | KAVISH S R |
| `feature/frontend-ui` | React UI & Interaction | GOWSHIKGUNAL R |
| `feature/data-eval` | Benchmark & Tests | PRANESH K V |
| `feature/integration-deploy` | API & Documentation | DINESH B |
