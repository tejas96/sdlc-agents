"""Test configuration settings."""

import pytest
from app.core.config import get_settings


def test_get_settings():
    """Test that settings can be loaded."""
    settings = get_settings()
    assert settings is not None
    assert settings.PROJECT_NAME is not None
    assert settings.VERSION is not None
    assert settings.API_V1_STR == "/api/v1"


def test_cors_origins():
    """Test CORS origins parsing."""
    settings = get_settings()
    
    # Test wildcard
    settings.BACKEND_CORS_ORIGINS = "*"
    assert settings.get_cors_origins() == ["*"]
    
    # Test comma-separated
    settings.BACKEND_CORS_ORIGINS = "http://localhost:3000,https://example.com"
    expected = ["http://localhost:3000", "https://example.com"]
    assert settings.get_cors_origins() == expected
    
    # Test JSON array
    settings.BACKEND_CORS_ORIGINS = '["http://localhost:3000", "https://example.com"]'
    assert settings.get_cors_origins() == expected
    
    # Test empty
    settings.BACKEND_CORS_ORIGINS = ""
    assert settings.get_cors_origins() == []
