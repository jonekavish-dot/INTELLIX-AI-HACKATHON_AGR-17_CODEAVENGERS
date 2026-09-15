"""
AgriDiff AI — FastAPI Backend Service
Agricultural Document Comparison & Change Intelligence
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import sys

# Ensure backend directory is in sys.path regardless of working directory
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

import uuid
import time
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pipeline.extractor import extract_pdf
from pipeline.chunker import detect_sections_and_chunks
from pipeline.embedder import get_embedder, embed_chunks, embed_pair
from pipeline.aligner import align_chunks
from pipeline.differ import compute_textual_diff
from pipeline.llm_analyzer import analyze_changes
from pipeline.validator import validate_and_assemble_results
from models.schemas import (
    CompareResponse,
    StatusResponse,
    ResultsResponse,
    HealthResponse,
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agridiff")

# ── In-Memory Job Store ────────────────────────────────────────────────────────
job_store: dict[str, dict] = {}


# ── Lifespan Startup ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AgriDiff AI starting — warming up embedder...")
    get_embedder()
    logger.info("AgriDiff AI embedder ready.")
    yield
    logger.info("AgriDiff AI shutting down.")


# ── App Definition ────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgriDiff AI",
    description="Agricultural Document Comparison & Intelligence Engine (AGR-17 | CODEAVENGERS)",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pipeline Worker ───────────────────────────────────────────────────────────
async def run_comparison_job(job_id: str, old_bytes: bytes, new_bytes: bytes,
                             old_name: str, new_name: str):
    start_time = time.time()
    store = job_store[job_id]

    def update(pct: int, msg: str):
        store["progress"] = pct
        store["message"] = msg
        logger.info(f"[{job_id}] {pct}% — {msg}")

    try:
        update(10, "Extracting page-aware text from documents...")
        old_pages = extract_pdf(old_bytes, old_name)
        new_pages = extract_pdf(new_bytes, new_name)

        if not old_pages or not new_pages:
            raise ValueError("Unable to extract text from one or both documents.")

        update(25, "Detecting sections and structure...")
        old_chunks = detect_sections_and_chunks(old_pages)
        new_chunks = detect_sections_and_chunks(new_pages)

        update(40, "Generating semantic embeddings...")
        old_texts = [c["text"] for c in old_chunks]
        new_texts = [c["text"] for c in new_chunks]
        old_embeddings, new_embeddings = embed_pair(old_texts, new_texts)

        update(55, "Aligning document passages semantically...")
        aligned_pairs = align_chunks(old_chunks, new_chunks, old_embeddings, new_embeddings)

        update(70, "Computing exhaustive textual and semantic differences...")
        pairs_with_diff = compute_textual_diff(aligned_pairs)

        update(85, "Performing bounded AI interpretation & impact classification...")
        analyzed_pairs = await analyze_changes(pairs_with_diff)

        update(95, "Validating evidence grounding & structuring dual views...")
        result_response = validate_and_assemble_results(
            analyzed_pairs=analyzed_pairs,
            old_pages=old_pages,
            new_pages=new_pages,
            old_doc_meta={"filename": old_name, "pages": len(old_pages), "chunks": len(old_chunks)},
            new_doc_meta={"filename": new_name, "pages": len(new_pages), "chunks": len(new_chunks)},
            job_id=job_id,
            start_time=start_time,
        )

        store["status"] = "completed"
        store["progress"] = 100
        store["message"] = "Analysis complete"
        store["result"] = result_response.model_dump()
        logger.info(
            f"[{job_id}] Finished: {result_response.summary.total_all_changes} total changes, "
            f"{result_response.summary.total_impact_changes} impact changes, "
            f"{result_response.summary.total_field_changes} field changes."
        )

    except Exception as e:
        logger.exception(f"[{job_id}] Pipeline execution error: {e}")
        store["status"] = "failed"
        store["message"] = str(e)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "service": "AgriDiff AI", "version": "1.1.0"}


@app.post("/api/auth/login")
async def demo_login(payload: dict):
    """Demo authentication endpoint for hackathon evaluation."""
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required.")

    demo_accounts = {
        "farmer": {"role": "farmer", "displayName": "Farmer Demo", "badge": "Land Records & Subsidies"},
        "officer": {"role": "officer", "displayName": "Agriculture Officer Demo", "badge": "Impact & Compliance"},
        "reviewer": {"role": "reviewer", "displayName": "Reviewer / Auditor Demo", "badge": "Full Audit & Grounding"},
    }

    user_info = demo_accounts.get(username.lower())
    if not user_info or password != "demo123":
        raise HTTPException(status_code=401, detail="Invalid username or password. Use demo accounts: farmer, officer, reviewer with password 'demo123'.")

    return {
        "status": "authenticated",
        "username": username.lower(),
        "role": user_info["role"],
        "displayName": user_info["displayName"],
        "badge": user_info["badge"],
        "token": f"demo-session-{uuid.uuid4().hex[:12]}",
    }


@app.post("/api/compare", response_model=CompareResponse)
async def compare_documents(
    background_tasks: BackgroundTasks,
    old_pdf: UploadFile = File(..., description="Old version PDF"),
    new_pdf: UploadFile = File(..., description="New version PDF"),
):
    for f in [old_pdf, new_pdf]:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File '{f.filename}' is not a valid PDF.")

    old_bytes = await old_pdf.read()
    new_bytes = await new_pdf.read()

    if len(old_bytes) == 0 or len(new_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes). Please upload a valid document.")

    max_bytes = 50 * 1024 * 1024
    if len(old_bytes) > max_bytes or len(new_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 50 MB.")

    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Job queued",
        "result": None,
    }

    background_tasks.add_task(
        run_comparison_job, job_id, old_bytes, new_bytes, old_pdf.filename, new_pdf.filename
    )

    return {"job_id": job_id, "status": "processing", "message": "Comparison initiated."}


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
    }


@app.get("/api/results/{job_id}", response_model=ResultsResponse)
async def get_job_results(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    if job["status"] == "processing":
        raise HTTPException(status_code=202, detail="Comparison is still processing.")
    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=job.get("message", "Pipeline failed."))
    return job["result"]


@app.get("/api/results/{job_id}/changes")
async def get_filtered_changes(
    job_id: str,
    view: str = Query("all", description="View mode: 'all' (exhaustive) | 'impact' (priority) | 'fields' (land record/structured)"),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
):
    job = job_store.get(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(status_code=404, detail="Completed results not available for this job ID.")

    result = job["result"]

    if view == "fields":
        return {"job_id": job_id, "view": "fields", "count": len(result["field_changes"]), "items": result["field_changes"]}

    items = result["impact_changes"] if view == "impact" else result["all_changes"]

    if category:
        items = [c for c in items if c.get("category", "").lower() == category.lower()]
    if severity:
        items = [c for c in items if c.get("impact", "").upper() == severity.upper()]
    if change_type:
        items = [c for c in items if c.get("change_type", "").upper() == change_type.upper()]

    return {"job_id": job_id, "view": view, "count": len(items), "items": items}


@app.get("/api/presets")
async def get_available_presets():
    """Provides pre-loaded document pairs for instant judge testing."""
    return [
        {
            "id": "preset_policy_20",
            "name": "Agricultural Scheme Guidelines (20+ Changes)",
            "description": "Comprehensive 20+ change policy test pair with eligibility, financial, deadline, documentation, and procedural changes.",
            "old_filename": "demo_old_policy.pdf",
            "new_filename": "demo_new_policy.pdf"
        },
        {
            "id": "preset_land_record",
            "name": "Patta & Land Record Administration Pair",
            "description": "Synthetic patta / land record document pair demonstrating structured survey number, area, holder, and verifier comparison.",
            "old_filename": "land_record_old.pdf",
            "new_filename": "land_record_new.pdf"
        }
    ]


@app.post("/api/presets/{preset_id}/run", response_model=CompareResponse)
async def run_preset_comparison(preset_id: str, background_tasks: BackgroundTasks):
    """Launches comparison on a built-in demo document pair."""
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    if preset_id == "preset_land_record":
        old_path = os.path.join(base_data_dir, "land_record_old.pdf")
        new_path = os.path.join(base_data_dir, "land_record_new.pdf")
        old_name = "Patta_Record_2023.pdf"
        new_name = "Patta_Record_2024.pdf"
    else:
        old_path = os.path.join(base_data_dir, "demo_old_policy.pdf")
        new_path = os.path.join(base_data_dir, "demo_new_policy.pdf")
        old_name = "Agri_Policy_2023.pdf"
        new_name = "Agri_Policy_2024.pdf"

    if not os.path.exists(old_path) or not os.path.exists(new_path):
        raise HTTPException(status_code=404, detail="Preset demo document files not found on server.")

    with open(old_path, "rb") as f:
        old_bytes = f.read()
    with open(new_path, "rb") as f:
        new_bytes = f.read()

    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": f"Preset '{preset_id}' queued",
        "result": None,
    }

    background_tasks.add_task(
        run_comparison_job, job_id, old_bytes, new_bytes, old_name, new_name
    )

    return {"job_id": job_id, "status": "processing", "message": f"Preset '{preset_id}' started."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
