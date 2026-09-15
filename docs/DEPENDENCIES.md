# AgriDiff AI — Dependency Inventory & Specifications

**Project:** AgriDiff AI — Agricultural Document Comparison & Change Intelligence Engine  
**Team:** CODEAVENGERS | BIT-AI-001 | AGR-17  
**Version:** 1.1.0  
**Last Updated:** September 2026

This document provides a comprehensive, reproducible inventory of all direct runtime, development, and testing dependencies across the AgriDiff AI ecosystem.

---

## 1. Backend Dependencies (Python)

All backend dependencies are defined in [backend/requirements.txt](file:///d:/INTELLIX/repo/backend/requirements.txt) with exact pinned versions.

| Package | Version | Purpose | Required |
| :--- | :--- | :--- | :--- |
| `fastapi` | `0.111.0` | Core high-performance ASGI web framework providing OpenAPI specifications and routing | **YES** |
| `uvicorn[standard]` | `0.30.1` | High-throughput production ASGI web server implementation with uvloop & httptools | **YES** |
| `python-multipart` | `0.0.9` | Streaming multipart/form-data parser for handling dual PDF file uploads | **YES** |
| `pydantic` | `2.7.1` | Rigorous schema definition, data validation, and serialization for comparison outputs | **YES** |
| `pydantic-settings` | `2.3.1` | Configuration and environment variable management for Pydantic v2 models | **YES** |
| `pymupdf` | `1.24.5` | PyMuPDF (fitz) — ultra-fast PDF text extraction, layout detection, and page-aware offsets | **YES** |
| `pdfplumber` | `0.11.0` | Tabular PDF extraction and character bounding-box geometry parsing | **YES** |
| `pytesseract` | `0.3.13` | Optical Character Recognition (OCR) bridge for scanned agricultural land deeds | **OPTIONAL** (Fallback to text parsing) |
| `Pillow` | `10.3.0` | Python Imaging Library (PIL) for image rasterization and page rendering | **YES** |
| `sentence-transformers` | `3.0.1` | Heavy transformer embeddings (`all-MiniLM-L6-v2`) | **OPTIONAL** (Omitted on cloud hosts to stay under 512MB RAM) |
| `scikit-learn` | `1.5.0` | Default lightweight semantic vectorizer & TF-IDF cosine similarity matrix (<70MB RAM) | **YES** |
| `numpy` | `1.26.4` | High-performance numerical linear algebra and vector operations | **YES** |
| `google-generativeai` | `0.7.2` | Official Google GenAI SDK for Gemini 1.5 Flash / Pro LLM analysis & change synthesis | **YES** |
| `python-dotenv` | `1.0.1` | Automatic loading of `.env` configuration variables into process environment | **YES** |
| `httpx` | `0.27.0` | Modern HTTP client supporting async network requests and test client emulation | **YES** |
| `aiofiles` | `23.2.1` | Non-blocking asynchronous file system I/O operations | **YES** |

---

## 2. Frontend Dependencies (Node.js / React)

All frontend dependencies are defined in [frontend/package.json](file:///d:/INTELLIX/repo/frontend/package.json) with exact resolution locked in [frontend/package-lock.json](file:///d:/INTELLIX/repo/frontend/package-lock.json).

| Package | Version | Purpose | Required |
| :--- | :--- | :--- | :--- |
| `react` | `^18.3.1` | Core reactive user interface library | **YES** |
| `react-dom` | `^18.3.1` | React DOM renderer for browser environments | **YES** |
| `react-router-dom` | `^6.24.0` | Client-side routing for multi-page SPA navigation | **YES** |
| `axios` | `^1.7.2` | Promise-based HTTP client for calling comparison and preset endpoints | **YES** |
| `lucide-react` | `^0.395.0` | Scalable SVG icon toolkit with agricultural and operational iconography | **YES** |
| `clsx` | `^2.1.1` | Conditional CSS className construction helper | **YES** |

---

## 3. Development, Build & Testing Dependencies

| Package | Ecosystem | Version | Purpose |
| :--- | :--- | :--- | :--- |
| `vite` | Node.js | `^5.3.1` | Modern frontend bundler, HMR dev server, and production compiler |
| `@vitejs/plugin-react` | Node.js | `^4.3.1` | Babel/Fast Refresh integration for React in Vite |
| `tailwindcss` | Node.js | `^3.4.4` | Utility-first CSS framework for responsive layout design |
| `postcss` | Node.js | `^8.4.39` | Tool for transforming CSS styles with JavaScript plugins |
| `autoprefixer` | Node.js | `^10.4.19` | Automatically adds CSS vendor prefixes for cross-browser compatibility |
| `pytest` | Python | `9.1.1` | Test discovery and test runner for 48 unit, regression, and e2e test cases |
| `pytest-asyncio` | Python | `1.4.0` | Asynchronous test execution plugin for pytest |
| `anyio` | Python | `4.13.0` | Async concurrency library powering Starlette/FastAPI asynchronous fixtures |

---

## 4. Large Artifacts & Heavy Packages Analysis

AgriDiff AI was explicitly engineered to prevent large repository bloat. Model weights and massive binary packages are **never stored in Git**.

| Artifact / Package | Approx. Size | Purpose | Source | How Developer Obtains | Runtime Requirement & Lightweight Fallback |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `sentence-transformers` & `all-MiniLM-L6-v2` | ~90 MB - 300 MB | Dense vector embeddings for semantic clause alignment | Hugging Face Hub | Downloaded automatically via `pip install -r requirements.txt` and cached locally in user cache (`~/.cache/huggingface/`) | **Optional:** AgriDiff AI implements an automatic **TF-IDF Vectorizer fallback** (`scikit-learn`). If transformer models are absent or slow, the engine runs locally with 0 network latency. |
| `pytesseract` / Tesseract OCR Binary | ~50 MB - 100 MB | OCR text extraction from scanned physical land pattas | Google Tesseract Open Source Project | OS package manager (`apt-get install tesseract-ocr` or Windows installer) | **Optional:** PyMuPDF extracts embedded digital text directly. OCR is only invoked for pure scan/raster pages. |
| Node Dependencies (`node_modules/`) | ~120 MB | Transpilation, bundling, React libraries | npm Registry | Generated locally via `npm install` | **Never committed to Git.** Regenerated deterministically via `package-lock.json`. |
| Python Environment (`.venv/`) | ~250 MB | Isolated Python binary and site-packages | PyPI | Generated locally via `python -m venv .venv && pip install -r backend/requirements.txt` | **Never committed to Git.** |
| Frontend Build Output (`dist/`) | ~300 KB | Production bundled JavaScript and CSS | Generated locally via Vite | Built via `npm run build` | **Never committed to Git.** |

---

## 5. Dependency Manifest Integrity

- **Python Manifest:** [backend/requirements.txt](file:///d:/INTELLIX/repo/backend/requirements.txt)
- **Node Manifest:** [frontend/package.json](file:///d:/INTELLIX/repo/frontend/package.json)
- **Node Lock File:** [frontend/package-lock.json](file:///d:/INTELLIX/repo/frontend/package-lock.json) (Tracked in Git for 100% deterministic builds)
