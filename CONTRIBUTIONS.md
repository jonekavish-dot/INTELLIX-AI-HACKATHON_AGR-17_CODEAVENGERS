# CONTRIBUTIONS — AgriDiff AI
**BIT-AI-001 | AGR-17 | CODEAVENGERS**

This file records actual work done by each team member.
Entries are added at each milestone. Do NOT fabricate entries.

---

## Team

| Member | GitHub | Department | Role |
|---|---|---|---|
| KAVISH S R | [@jonekavish-dot](https://github.com/jonekavish-dot) | CSE | Team Leader — Architecture + AI/Backend |
| GOWSHIKGUNAL R | [@gowshikgunal22](https://github.com/gowshikgunal22) | CSE | Frontend + Dashboard + UX |
| PRANESH K V | [@kvpranesh](https://github.com/kvpranesh) | AIDS | Data + Evaluation + Testing |
| DINESH B | [@dineshbalu7f-glitch](https://github.com/dineshbalu7f-glitch) | AIDS | Integration + Deployment + Presentation |

---

## Ownership Model

### KAVISH S R — AI/Backend

**Owns:**
- Overall system architecture and technical decisions
- `backend/pipeline/` — all pipeline stages
- `backend/main.py` — API design
- `backend/models/schemas.py` — canonical data contract
- LLM prompt design and anti-hallucination strategy
- Comparison engine (exhaustive + semantic layers)
- Entity/field extraction logic

**Branch:** `feature/backend-pipeline`

---

### GOWSHIKGUNAL R — Frontend

**Owns:**
- `frontend/src/` — all React components and pages
- Upload page (Screen 1)
- Processing page (Screen 2)
- Results dashboard with All Changes + Impact View tabs (Screen 3)
- Evidence panel (Screen 4)
- FilterBar, ChangeCard, StatsBar, EvidenceModal components
- Frontend integration with backend API

**Branch:** `feature/frontend-ui`

---

### PRANESH K V — Data/Evaluation

**Owns:**
- `data/` — all test documents and ground truth
- `evaluation/eval.py` — evaluation script
- Expanded ground truth (20+ changes across T01–T20 test cases)
- Synthetic land-record/patta document pair
- Manual verification of evidence grounding
- Test fixture design (unit + integration test data)
- Precision/recall measurement

**Branch:** `feature/data-eval`

---

### DINESH B — Integration/Deployment

**Owns:**
- `docs/` — documentation and presentation
- `README.md`, `CONTRIBUTIONS.md`, `CHANGELOG.md`
- Environment variable setup (`.env.example`)
- End-to-end integration testing
- Demo reliability — pre-computed fallback results
- Deployment (local/ngrok/Render)
- Final demo preparation and screen recording

**Branch:** `feature/integration-deploy`

---

## Contribution Log

*Entries added after each meaningful completed phase.*

### 2026-09-15 — KAVISH S R
- Designed overall system architecture
- Implemented complete backend pipeline (extraction → chunking → embedding → alignment → diff → LLM → validation)
- Designed anti-hallucination evidence grounding strategy
- Authored all LLM prompts (MODIFIED, ADDED, REMOVED variants)
- Set up FastAPI API with job-based async processing

### 2026-09-15 — GOWSHIKGUNAL R
- Implemented all 4 frontend screens (Upload, Processing, Results, Evidence)
- Built ChangeCard, FilterBar, StatsBar, EvidenceModal components
- Integrated frontend with backend API via Axios

### 2026-09-15 — PRANESH K V
- Created controlled demo document pair (9 ground-truth changes)
- Authored ground_truth.json with labelled changes
- Authored evaluation script (precision/recall/category/grounding metrics)
- Designed PDF generation script

### 2026-09-15 — DINESH B
- Set up GitHub repository with branch structure
- Authored README.md, SETUP.md, CHANGELOG.md, CONTRIBUTIONS.md
- Configured .gitignore and .env.example
- Pushed all initial scaffold code

---

*This file must be updated with actual work — not fabricated entries.*
