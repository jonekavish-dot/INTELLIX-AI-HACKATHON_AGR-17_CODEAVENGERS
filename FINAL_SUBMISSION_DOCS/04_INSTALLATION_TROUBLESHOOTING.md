# AgriDiff AI — Installation & Runtime Troubleshooting Guide

**Project:** AgriDiff AI — Agricultural Document Comparison & Change Intelligence  
**Team:** CODEAVENGERS | BIT-AI-001 | AGR-17  
**Version:** 1.1.0  
**Last Updated:** September 2026

This guide addresses common installation, configuration, networking, and runtime issues encountered when setting up AgriDiff AI on local workstations or cloud environments.

---

## 1. Python Package Installation Failures

### Symptom: `pip install -r backend/requirements.txt` fails or shows compilation errors.

#### Root Cause:
- Outdated `pip`, corrupted cached wheel packages, or Python version mismatches (AgriDiff AI requires Python 3.10 to 3.14).

#### Resolution: Clean Virtual Environment Recreation

**Windows (PowerShell):**
```powershell
# Deactivate and delete existing virtual environment
deactivate
Remove-Item -Recurse -Force .venv

# Recreate fresh virtual environment
python -m venv .venv
.venv\Scripts\activate

# Upgrade pip and reinstall dependencies cleanly
python -m pip install --upgrade pip
pip install -r backend/requirements.txt --no-cache-dir
```

**Linux / macOS (Bash):**
```bash
# Deactivate and delete existing virtual environment
deactivate 2>/dev/null || true
rm -rf .venv

# Recreate fresh virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and reinstall dependencies cleanly
python -m pip install --upgrade pip
pip install -r backend/requirements.txt --no-cache-dir
```

---

## 2. Node / React Dependency Failures

### Symptom: `npm install` throws `ERESOLVE` or peer dependency conflicts, or `npm run build` fails with missing modules.

#### Root Cause:
- Corrupted `node_modules/` or stale npm package caches.

#### Resolution: Clean Node Dependencies

**Windows (PowerShell):**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json  # Only if lockfile has corrupted entries
npm cache clean --force
npm install
npm run build
```

**Linux / macOS (Bash):**
```bash
cd frontend
rm -rf node_modules
npm cache clean --force
npm install
npm run build
```

---

## 3. Port Already in Use (`8000` or `3000`)

### Symptom: `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)` or Vite reporting `Port 3000 is in use, trying another port...`

#### Root Cause:
- A previous backend or frontend instance is still running in the background.

#### Resolution:

**Backend Port 8000:**

*Windows (PowerShell):*
```powershell
# Identify process ID listening on port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Terminate the process (replace <PID> with the actual number)
Stop-Process -Id <PID> -Force
```

*Linux / macOS (Bash):*
```bash
lsof -i :8000
kill -9 $(lsof -t -i:8000)
```

**Frontend Port 3000:**

*Windows (PowerShell):*
```powershell
Get-NetTCPConnection -LocalPort 3000 | Select-Object OwningProcess
Stop-Process -Id <PID> -Force
```

*Linux / macOS (Bash):*
```bash
lsof -i :3000
kill -9 $(lsof -t -i:3000)
```

---

## 4. Missing or Invalid Environment Variables

### Symptom: LLM analysis is skipped or backend logs report `GEMINI_API_KEY not configured`.

#### Root Cause:
- `.env` file does not exist or `GEMINI_API_KEY` is not populated.

#### Graceful Fallback Behavior:
- **AgriDiff AI is resilient by design.** If `GEMINI_API_KEY` is missing or invalid:
  1. The backend automatically switches to its **Deterministic Rule-Based Alignment & Extraction Pipeline**.
  2. All numeric changes, date shifts, clause additions, deletions, and tabular field updates are still 100% extracted.
  3. Grounding evidence verification and canonical diffing continue to operate with 0% downtime.

#### Resolution:
1. Create your `.env` file from the template:
   ```bash
   cp .env.example.txt .env   # Linux/macOS
   copy .env.example.txt .env # Windows
   ```
2. Open `.env` and set:
   ```ini
   GEMINI_API_KEY=AIzaSy...your_real_key_here
   ```
3. Restart the backend server.

---

## 5. OCR Dependency Missing (`pytesseract` / Tesseract-OCR)

### Symptom: Warning in logs: `TesseractNotFoundError: tesseract is not installed or it's not in your PATH`.

#### Root Cause:
- The system lacks the optional Google Tesseract binary executable.

#### Graceful Fallback Behavior:
- Digital PDFs with text streams (99% of government policy gazettes) are extracted at microsecond speeds using **PyMuPDF (`pymupdf`)**.
- Tesseract is only invoked if a PDF contains scanned raster images without a selectable text layer.

#### Optional Installation:
- **Windows:** Download the installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add `C:\Program Files\Tesseract-OCR` to your System `PATH`.
- **Ubuntu/Debian:** `sudo apt-get install -y tesseract-ocr`
- **macOS:** `brew install tesseract`

---

## 6. Remote LLM / API Unavailable or Rate Limited

### Symptom: `google.api_core.exceptions.ResourceExhausted` or HTTP 429 / 503 from Gemini API.

#### Built-in Fault Tolerance:
- AgriDiff AI enforces:
  - Configurable request timeouts via `LLM_TIMEOUT_SECONDS` (default: 30s).
  - Concurrency throttling via `LLM_MAX_CONCURRENT` (default: 5).
  - Immediate failover to deterministic comparison logic if the API returns an error or times out.
- The user will still receive full comparison results without an application crash or broken UI.

---

## 7. Fast Self-Test & Diagnostic Commands

Run this sequence to verify the health of your environment:

```bash
# 1. Backend Health & Unit/Regression Test Suite (48 tests)
python -m pytest -v

# 2. Benchmark Precision & Recall Validation
python evaluation/eval.py --results data/benchmark_results.json --ground_truth data/ground_truth.json

# 3. Frontend Production Build Check
cd frontend
npm run build
```
