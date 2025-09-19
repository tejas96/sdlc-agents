"""Test main application endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_read_root(client: TestClient, mock_settings):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to" in data["message"]
    assert data["version"] == "1.0.0"


def test_health_check(client: TestClient, mock_settings):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "API" in data["service"]
    assert data["version"] == "1.0.0"
    assert data["environment"] in ["test", "development"]
    assert data["debug_mode"] is True
