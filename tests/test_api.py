"""
AgriDiff AI — API & Authentication Test Suite
Tests FastAPI endpoints: /health, /api/auth/login, /presets, /compare, /status, /results, and failure modes.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ── Health & Presets ──────────────────────────────────────────────────────────

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


# ── Hackathon Demo Authentication ─────────────────────────────────────────────

def test_auth_valid_farmer_credentials():
    response = client.post("/api/auth/login", json={"username": "farmer", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"
    assert data["role"] == "farmer"
    assert data["displayName"] == "Farmer Demo"
    assert "token" in data


def test_auth_valid_officer_credentials():
    response = client.post("/api/auth/login", json={"username": "officer", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"
    assert data["role"] == "officer"
    assert data["displayName"] == "Agriculture Officer Demo"


def test_auth_valid_reviewer_credentials():
    response = client.post("/api/auth/login", json={"username": "reviewer", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"
    assert data["role"] == "reviewer"
    assert data["displayName"] == "Reviewer / Auditor Demo"


def test_auth_invalid_username():
    response = client.post("/api/auth/login", json={"username": "unknown_user", "password": "demo123"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_auth_invalid_password():
    response = client.post("/api/auth/login", json={"username": "farmer", "password": "wrong_password"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_auth_empty_username():
    response = client.post("/api/auth/login", json={"username": "", "password": "demo123"})
    assert response.status_code == 400
    assert "Username is required" in response.json()["detail"]


def test_auth_empty_password():
    response = client.post("/api/auth/login", json={"username": "officer", "password": ""})
    assert response.status_code == 400
    assert "Password is required" in response.json()["detail"]


# ── Failure & Edge Cases ──────────────────────────────────────────────────────

def test_compare_invalid_filetype():
    files = {
        "old_pdf": ("test.png", b"fake image bytes", "image/png"),
        "new_pdf": ("test.pdf", b"%PDF-fake", "application/pdf"),
    }
    response = client.post("/api/compare", files=files)
    assert response.status_code == 400
    assert "not a valid PDF" in response.json()["detail"]


def test_compare_empty_pdf_file():
    files = {
        "old_pdf": ("empty_old.pdf", b"", "application/pdf"),
        "new_pdf": ("empty_new.pdf", b"%PDF-1.4 header only", "application/pdf"),
    }
    response = client.post("/api/compare", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_status_unknown_job():
    response = client.get("/api/status/invalid-uuid-12345")
    assert response.status_code == 404


def test_results_unknown_job():
    response = client.get("/api/results/non-existent-job-id")
    assert response.status_code == 404
