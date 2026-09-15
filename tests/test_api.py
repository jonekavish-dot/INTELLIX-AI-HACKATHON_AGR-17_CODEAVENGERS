"""
AgriDiff AI — API Test Suite
Tests FastAPI endpoints: /health, /presets, /compare, /status, /results, and /changes.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def test_a01_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AgriDiff AI"


def test_a02_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 2
    preset_ids = [p["id"] for p in presets]
    assert "preset_policy_20" in preset_ids
    assert "preset_land_record" in preset_ids


def test_a04_compare_invalid_filetype():
    files = {
        "old_pdf": ("test.png", b"fake image bytes", "image/png"),
        "new_pdf": ("test.pdf", b"%PDF-fake", "application/pdf"),
    }
    response = client.post("/api/compare", files=files)
    assert response.status_code == 400
    assert "not a valid PDF" in response.json()["detail"]


def test_a07_status_unknown_job():
    response = client.get("/api/status/invalid-uuid-12345")
    assert response.status_code == 404


def test_a10_results_unknown_job():
    response = client.get("/api/results/non-existent-job-id")
    assert response.status_code == 404
