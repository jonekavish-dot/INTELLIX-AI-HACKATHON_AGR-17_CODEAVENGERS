# AgriDiff AI — Complete Reproducible Setup Guide

**Project:** AgriDiff AI — Agricultural Document Comparison & Change Intelligence Engine  
**Team:** CODEAVENGERS | BIT-AI-001 | AGR-17  
**Version:** 1.1.0  
**Last Updated:** September 2026

This guide provides clean, deterministic setup instructions for developers, reviewers, and evaluators cloning the AgriDiff AI repository.

---

## 1. System Prerequisites

Before installation, verify your local development environment:

| Requirement | Minimum Supported | Recommended | Verification Command |
| :--- | :--- | :--- | :--- |
| **Python** | `3.10` | `3.11` – `3.14` | `python --version` |
| **Node.js** | `18.0.0` | `20.x` or `22.x` | `node --version` |
| **npm** | `9.0.0` | `10.x` | `npm --version` |
| **Git** | `2.30+` | Latest | `git --version` |

*Optional:* Google Tesseract OCR (`tesseract-ocr`) for scanned deed images. (If absent, digital PDF text extraction operates via PyMuPDF with 0 dependencies).

---

## 2. Environment Configuration

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jonekavish-dot/agridiff-ai.git
   cd agridiff-ai
   ```

2. **Create your `.env` configuration from the canonical template:**
   - **Windows:**
     ```cmd
     copy .env.example.txt .env
     ```
   - **Linux / macOS:**
     ```bash
     cp .env.example.txt .env
     ```

3. **Configure environment parameters (Optional):**
   - Open `.env`.
   - To enable remote Gemini LLM reasoning: set `GEMINI_API_KEY=AIzaSy...`.
   - *Note:* If you leave `GEMINI_API_KEY` empty or omitted, AgriDiff AI automatically activates its **Deterministic Semantic Alignment & Extraction Engine** — the entire pipeline runs locally with 100% test passing and zero failures.

---

## 3. Backend Setup & Startup

### Step 3.1: Create & Activate Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3.2: Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Step 3.3: Start FastAPI Backend Service
```bash
# Option A: Direct Python runner (reads PORT from .env or defaults to 8000)
python backend/main.py

# Option B: Uvicorn with auto-reload (Development)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Health Endpoint:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **OpenAPI JSON Schema:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 4. Frontend Setup & Startup

In a second terminal window:

### Step 4.1: Install Node Dependencies
```bash
cd frontend
npm install
```

### Step 4.2: Start Vite Development Server
```bash
npm run dev
```

- **Local Frontend Portal:** [http://localhost:3000](http://localhost:3000)
- Vite proxies `/api` calls directly to `http://localhost:8000`.

---

## 5. Demonstration & Evaluation Walkthrough

1. Open [http://localhost:3000](http://localhost:3000) in any modern browser (Chrome, Edge, Firefox, Safari, or mobile browser).
2. **Authenticate:** Use any of the pre-configured demo evaluation accounts:
   - **🌾 Farmer Demo:** `farmer` / `demo123`
   - **🛡️ Agriculture Officer Demo:** `officer` / `demo123`
   - **🔍 Reviewer / Auditor Demo:** `reviewer` / `demo123`
   *(Or click any 1-click quick login button).*
3. **Execute Comparison:**
   - Click **Load Preset: Fertilizer & Irrigation Policy** (or drag & drop custom agricultural PDFs).
   - Observe the multi-stage progress indicator: Text Extraction ➔ Clause Detection ➔ Semantic Alignment ➔ Differencing ➔ Grounding.
4. **Explore Intelligence Views:**
   - **Tab 1: All Changes (Exhaustive Comparison):** Retains 100% of source differences (24 detected units) with highlighted Shift statements and Administrative Action Directives.
   - **Tab 2: Impact View (Consequential Shifts):** High/Medium priority changes categorized for immediate field action.
   - **Tab 3: Structured Land Records:** Strict tabular view comparing Survey Numbers, Holding Areas, Landholder names, and Verifier stamps.
5. **Inspect Grounding Evidence:**
   - Click **View Evidence** on any change card to inspect side-by-side exact source document quotes and page numbers.

---

## 6. Automated Testing & Benchmark Validation

Run these commands from the repository root:

### Run Full Test Suite (48 Tests)
```bash
python -m pytest -v
```
*Expected: 48 passed (100% pass rate).*

### Run Benchmark Evaluation Metric Script
```bash
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json
```
*Expected Output: Recall: 100.0%, Precision: 91.7%, F1: 95.7%, Evidence Grounding Rate: 100.0%.*

### Verify Production Frontend Build
```bash
cd frontend
npm run build
```
*Expected Output: Clean Vite build to `frontend/dist/` in < 4 seconds.*

---

## 7. Documentation Cross-References

- **[docs/DEPENDENCIES.md](file:///d:/INTELLIX/repo/docs/DEPENDENCIES.md):** Complete inventory of packages, versions, and sizes.
- **[docs/DEPLOYMENT.md](file:///d:/INTELLIX/repo/docs/DEPLOYMENT.md):** Production deployment to Render (Backend) and Vercel (Frontend).
- **[docs/INSTALLATION_TROUBLESHOOTING.md](file:///d:/INTELLIX/repo/docs/INSTALLATION_TROUBLESHOOTING.md):** Resolving venv recreation, port conflicts, OCR, and fallbacks.
- **[project_inventory/NON_GIT_ARTIFACTS.txt](file:///d:/INTELLIX/repo/project_inventory/NON_GIT_ARTIFACTS.txt):** Excluded artifacts, reasons, and recreation steps.
- **[project_inventory/CONFIGURATION_INVENTORY.txt](file:///d:/INTELLIX/repo/project_inventory/CONFIGURATION_INVENTORY.txt):** Environment variables and configuration catalog.
