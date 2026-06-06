import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_models():
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "current_model" in data
    assert "available_models" in data
