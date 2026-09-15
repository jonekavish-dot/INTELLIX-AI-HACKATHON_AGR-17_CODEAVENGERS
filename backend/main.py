"""
AgriDiff AI — FastAPI Backend Entry Point
Team: CODEAVENGERS | BIT-AI-001 | AGR-17
"""

import uuid
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pipeline.extractor import extract_pdf
from pipeline.chunker import detect_sections_and_chunks
from pipeline.embedder import get_embedder, embed_chunks
from pipeline.aligner import align_chunks
from pipeline.differ import compute_textual_diff
from pipeline.llm_analyzer import analyze_changes
from pipeline.validator import validate_and_assemble
from models.schemas import (
    CompareResponse,
    StatusResponse,
    ResultsResponse,
    HealthResponse,
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agridiff")

# ── In-memory job store (dict → no DB needed for hackathon) ────────────────────
job_store: dict[str, dict] = {}


# ── Lifespan: warm up embedder on startup ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌾 AgriDiff AI starting — warming up embedder...")
    get_embedder()  # download / cache model on first start
    logger.info("✅ Embedder ready.")
    yield
    logger.info("AgriDiff AI shutting down.")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgriDiff AI",
    description="Agricultural Document Comparison System — AGR-17 | CODEAVENGERS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for hackathon; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper: background comparison job ─────────────────────────────────────────
async def run_comparison(job_id: str, old_bytes: bytes, new_bytes: bytes,
                          old_name: str, new_name: str):
    try:
        store = job_store[job_id]

        def update(pct: int, msg: str):
            store["progress"] = pct
            store["message"] = msg
            logger.info(f"[{job_id}] {pct}% — {msg}")

        update(5, "Extracting text from PDFs...")
        old_pages = extract_pdf(old_bytes, old_name)
        new_pages = extract_pdf(new_bytes, new_name)

        update(20, "Detecting sections and chunking...")
        old_chunks = detect_sections_and_chunks(old_pages)
        new_chunks = detect_sections_and_chunks(new_pages)

        update(35, "Generating semantic embeddings...")
        old_embeddings = embed_chunks([c["text"] for c in old_chunks])
        new_embeddings = embed_chunks([c["text"] for c in new_chunks])

        update(50, "Aligning document sections semantically...")
        aligned_pairs = align_chunks(old_chunks, new_chunks, old_embeddings, new_embeddings)

        update(60, "Computing textual differences...")
        pairs_with_diff = compute_textual_diff(aligned_pairs)

        update(70, "Running AI analysis on meaningful changes...")
        analyzed_pairs = await analyze_changes(pairs_with_diff)

        update(90, "Validating evidence and assembling results...")
        result = validate_and_assemble(
            analyzed_pairs,
            old_doc_meta={"filename": old_name, "pages": len(old_pages), "chunks": len(old_chunks)},
            new_doc_meta={"filename": new_name, "pages": len(new_pages), "chunks": len(new_chunks)},
            job_id=job_id,
        )

        store["status"] = "completed"
        store["progress"] = 100
        store["message"] = "Analysis complete"
        store["result"] = result
        logger.info(f"[{job_id}] ✅ Done — {result['summary']['total_meaningful_changes']} meaningful changes found.")

    except Exception as e:
        logger.exception(f"[{job_id}] ❌ Pipeline failed: {e}")
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["message"] = str(e)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "service": "AgriDiff AI", "version": "1.0.0"}


@app.post("/api/compare", response_model=CompareResponse)
async def compare(
    background_tasks: BackgroundTasks,
    old_pdf: UploadFile = File(..., description="Old version PDF"),
    new_pdf: UploadFile = File(..., description="New version PDF"),
):
    # Validate file types
    for f in [old_pdf, new_pdf]:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File '{f.filename}' is not a PDF.")

    old_bytes = await old_pdf.read()
    new_bytes = await new_pdf.read()

    # Size check (50 MB)
    max_bytes = 50 * 1024 * 1024
    for name, data in [(old_pdf.filename, old_bytes), (new_pdf.filename, new_bytes)]:
        if len(data) > max_bytes:
            raise HTTPException(status_code=400, detail=f"File '{name}' exceeds 50 MB limit.")

    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Job queued",
        "result": None,
    }

    background_tasks.add_task(
        run_comparison, job_id, old_bytes, new_bytes, old_pdf.filename, new_pdf.filename
    )

    return {"job_id": job_id, "status": "processing", "message": "Comparison started"}


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
    }


@app.get("/api/results/{job_id}", response_model=ResultsResponse)
async def results(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "processing":
        raise HTTPException(status_code=202, detail="Still processing")
    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=job.get("message", "Pipeline failed"))
    return job["result"]


@app.get("/api/results/{job_id}/changes")
async def filtered_changes(
    job_id: str,
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
):
    job = job_store.get(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(status_code=404, detail="Results not available")

    changes = job["result"]["changes"]

    if category:
        changes = [c for c in changes if c.get("category", "").lower() == category.lower()]
    if severity:
        changes = [c for c in changes if c.get("severity", "").upper() == severity.upper()]
    if change_type:
        changes = [c for c in changes if c.get("change_type", "").upper() == change_type.upper()]

    return {"job_id": job_id, "count": len(changes), "changes": changes}

