"""Test authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user_crud
from app.models.user import UserCreate


@pytest.mark.asyncio
async def test_register_user(client: TestClient, db_session: AsyncSession, override_get_async_session, mock_settings):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: TestClient, db_session: AsyncSession, override_get_async_session, mock_settings):
    """Test registration with duplicate email."""
    # Create initial user
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123",
    )
    await user_crud.create(db_session, obj_in=user_in)
    
    # Try to register with same email
    user_data = {
        "email": "test@example.com",
        "username": "differentuser",
        "password": "testpassword123",
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "email already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_user(client: TestClient, db_session: AsyncSession, override_get_async_session, mock_settings):
    """Test user login."""
    # Create user
    user_in = UserCreate(
        email="test@example.com",
        username="testuser", 
        password="testpassword123",
    )
    await user_crud.create(db_session, obj_in=user_in)
    
    # Login
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123",
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800  # 30 minutes in seconds


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient, db_session: AsyncSession, override_get_async_session, mock_settings):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client: TestClient, db_session: AsyncSession, override_get_async_session, mock_settings):
    """Test getting current user info."""
    # Create user and get token
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123",
    )
    user = await user_crud.create(db_session, obj_in=user_in)
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["id"] == user.id
