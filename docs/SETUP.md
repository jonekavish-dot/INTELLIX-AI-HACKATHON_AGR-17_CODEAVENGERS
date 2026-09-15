# AgriDiff AI — Quick Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

---

## Backend Setup (Person 1 — P1)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

uvicorn main:app --reload --port 8000
```

Test: http://localhost:8000/api/health

---

## Frontend Setup (Person 2 — P2)

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

---

## Generate Demo PDFs (Person 3 — P3)

```bash
pip install reportlab
python data/generate_demo_pdfs.py
# Creates data/demo_old_policy.pdf and data/demo_new_policy.pdf
```

---

## Run Evaluation (Person 3 — P3)

After running a comparison and saving results.json:

```bash
python evaluation/eval.py \
  --results results.json \
  --ground_truth data/ground_truth.json \
  --output eval_metrics.json
```

---

## Team Branches

```
main                          ← demo/production branch
├── dev                       ← integration branch
│   ├── feature/backend-pipeline    (P1 — KAVISH)
│   ├── feature/frontend-ui         (P2 — GOWSHIKGUNAL)
│   ├── feature/data-eval           (P3 — PRANESH)
│   └── feature/integration-deploy  (P4 — DINESH)
```

### Git Workflow

```bash
# Each person works on their feature branch
git checkout -b feature/backend-pipeline

# Commit every 30-45 mins
git add .
git commit -m "[P1] Add PDF extraction with pdfplumber"
git push origin feature/backend-pipeline

# P4 merges to dev at checkpoints H3, H5, H7
# P4 merges dev → main at H7 for final freeze
```

### Code Freeze

| Time | Action |
|---|---|
| H7 | `git tag v1.0.0-demo` on main — NO new features |
| H8 | Demo runs from this exact commit |

---

## API Quick Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/compare` | Upload old + new PDFs |
| GET | `/api/status/{job_id}` | Poll job status |
| GET | `/api/results/{job_id}` | Get full results |
| GET | `/api/results/{job_id}/changes?category=Financial&severity=HIGH` | Filtered changes |

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and set:

```
GEMINI_API_KEY=your_key_here
LLM_MODEL=gemini-1.5-flash
```

---

## Fallback: If LLM API Fails

The pipeline has a deterministic fallback — it will still detect ADDED/REMOVED/MODIFIED
changes with similarity scores. The LLM only adds category + impact explanation.

For the demo: pre-compute results and cache them.

