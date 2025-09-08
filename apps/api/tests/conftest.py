import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# Set environment variable before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.core.database import get_db_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Database session fixture for testing."""
    # Create test database engine using SQLite for testing
    test_database_url = "sqlite+aiosqlite:///:memory:"
    test_engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True,
    )

    # Create test session factory
    TestingSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session
    async with TestingSessionLocal() as session:
        yield session

    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
def override_get_async_session(db_session: AsyncSession) -> Generator[None, None, None]:
    """Override database session dependency for testing."""

    async def _override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    """Mock settings fixture"""
    from unittest.mock import patch
    
    with patch("app.core.config.get_settings") as mock_get_settings:
        mock_settings_obj = MagicMock()
        mock_settings_obj.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        mock_settings_obj.SECRET_KEY = "test-secret-key"
        mock_settings_obj.ALGORITHM = "HS256"
        mock_settings_obj.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_settings_obj.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_settings_obj.PROJECT_NAME = "SDLC Agents API"
        mock_settings_obj.VERSION = "1.0.0"
        mock_settings_obj.API_V1_STR = "/api/v1"
        mock_settings_obj.ENVIRONMENT = "test"
        mock_settings_obj.DEBUG = True
        mock_settings_obj.LOG_LEVEL = "DEBUG"
        mock_settings_obj.PORT = 8000
        mock_settings_obj.ENABLE_DOCS = True
        mock_settings_obj.ENABLE_REDOC = True
        mock_get_settings.return_value = mock_settings_obj
        yield mock_settings_obj


# Configure pytest for async tests
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
