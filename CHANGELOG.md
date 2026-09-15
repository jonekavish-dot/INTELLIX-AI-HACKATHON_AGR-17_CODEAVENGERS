# CHANGELOG — AgriDiff AI
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

All notable changes to this project are documented here.
Format: `[version] YYYY-MM-DD — description`

---

## [0.2.0] 2026-09-15 — Engineering audit + architecture freeze

### Added
- `CHANGELOG.md` — this file
- `CONTRIBUTIONS.md` — team ownership model
- Canonical change object schema documented in `docs/ARCHITECTURE.md`
- Test strategy matrix (T01–T20) defined
- 20-change exhaustive ground truth design documented

### Identified gaps (to be addressed in next phases)
- No exhaustive comparison layer — validator currently filters to "meaningful" only (BLOCKER)
- No field-level / entity extraction (numeric, date, name, survey number)
- No COMPLETE CHANGES vs IMPACT VIEW dual-mode API
- No structured entity comparison for land records / patta documents
- No test suite (zero unit / integration / API / E2E tests)
- Ground truth has only 9 changes — needs 20+ for exhaustiveness requirement
- `change_id` format (`chg_XXXXXXXX`) diverges from canonical `CH-NNN`
- `evidence_status` literal `NOT_PRESENT` missing from schema (only `SUPPORTED` / `INSUFFICIENT_EVIDENCE`)
- `SEMANTICALLY_EQUIVALENT` change type missing (current schema uses `EQUIVALENT`)
- `field`, `old_value`, `new_value`, `interpretation`, `subsection` fields absent from change object
- `impact` field currently conflated with `severity` label — needs separation
- Frontend has no All Changes / Impact View tab separation

---

## [0.1.0] 2026-09-15 — Initial project scaffold

### Added
- FastAPI backend with `/api/compare`, `/api/status`, `/api/results`, `/api/health`
- PDF extraction pipeline: `extractor.py` (PyMuPDF + pdfplumber + pytesseract OCR)
- Section detection + chunking: `chunker.py`
- Sentence-transformer embeddings: `embedder.py` (all-MiniLM-L6-v2)
- Cosine semantic alignment: `aligner.py`
- Word-level textual diff: `differ.py` (difflib)
- Gemini 1.5 Flash LLM analysis: `llm_analyzer.py` (3 prompts + retry + fallback)
- Evidence grounding validator: `validator.py`
- Pydantic schemas: `models/schemas.py`
- React + Tailwind + Vite frontend (4 screens)
- Upload / Processing / Results / Evidence pages
- ChangeCard, FilterBar, StatsBar, EvidenceModal components
- Demo PDFs (old + new Agricultural Support Scheme Guidelines)
- Ground truth JSON (9 changes)
- Evaluation script `evaluation/eval.py`
- Presentation: `docs/AgriDiff_AI_Enhanced_SRS_Presentation.pptx`
- Team setup guide: `docs/SETUP.md`
- `.gitignore`, `LICENSE`, `README.md`

---

*Next: implement exhaustive comparison layer, entity extraction, field-level changes, expanded ground truth (20+ changes), test suite.*
