# AgriDiff AI — Setup & Run Guide (v1.2.0)
**BIT-AI-001 | AGR-17 | Team CODEAVENGERS**

---

## 📋 Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher (with npm)
- **Git**

---

## 🚀 Quick Start (Local Development)

### Step 1: Start Backend (FastAPI)
From the repository root:
```bash
# Optional: create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# Install dependencies
pip install -r backend/requirements.txt

# Launch FastAPI server with auto-reload
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend Health: `http://127.0.0.1:8000/api/health`
* Interactive API Documentation: `http://127.0.0.1:8000/docs`

---

### Step 2: Start Frontend (React + Vite)
In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
* Frontend Dashboard: `http://localhost:3000`

---

## 🔑 Demo Login Credentials

For judging demonstration, use any of the safe synthetic demo accounts:

| Profile | Username | Password | Access Highlights |
|---|---|---|---|
| **🌾 Farmer Demo** | `farmer` | `demo123` | Structured land-record comparison, holding limits, subsidy caps |
| **🛡️ Agriculture Officer Demo** | `officer` | `demo123` | Priority impact view, operational notes, sanction thresholds |
| **🔍 Reviewer / Auditor Demo** | `reviewer` | `demo123` | Full audit trail, multi-span grounding verification, metrics |

*Or simply click any **"Quick Sign In"** button on the login screen.*

---

## 🧪 Running Tests & Evaluation

### Run Full Pytest Suite (48 Tests)
```bash
python -m pytest -v
```

### Run Benchmark Evaluation Script
```bash
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json
```

### Production Build Verification
```bash
cd frontend
npm run build
```
