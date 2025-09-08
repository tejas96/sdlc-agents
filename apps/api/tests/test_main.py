"""Test main application endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_read_root(client: TestClient, mock_settings):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to SDLC Agents API"
    assert data["description"] == "SDLC Agents API for software development lifecycle management"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "test"


def test_health_check(client: TestClient, mock_settings):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SDLC Agents API"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "test"
    assert data["debug_mode"] is True
