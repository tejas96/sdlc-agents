"""Test database models."""

import pytest
from datetime import datetime
from app.models.user import User, UserCreate
from app.models.project import Project, ProjectCreate, ProjectStatus, ProjectType
from app.models.agent import Agent, AgentCreate, AgentType, AgentStatus


def test_user_model():
    """Test User model creation."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
    )
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.timezone == "UTC"
    assert user.theme == "light"


def test_project_model():
    """Test Project model creation."""
    project = Project(
        name="Test Project",
        slug="test-project",
        description="A test project",
        status=ProjectStatus.ACTIVE,
        project_type=ProjectType.WEB_APP,
        repository_url="https://github.com/user/repo",
        repository_branch="main",
        owner_id=1,
        created_by=1,
        updated_by=1,
    )
    assert project.name == "Test Project"
    assert project.slug == "test-project"
    assert project.status == ProjectStatus.ACTIVE
    assert project.project_type == ProjectType.WEB_APP
    assert project.repository_branch == "main"
    assert project.owner_id == 1


def test_agent_model():
    """Test Agent model creation."""
    agent = Agent(
        name="Test Agent",
        slug="test-agent",
        description="A test agent",
        agent_type=AgentType.CODE_REVIEWER,
        status=AgentStatus.ACTIVE,
        model_name="claude-3-haiku",
        max_tokens=4000,
        temperature=0.1,
        timeout_seconds=300,
        owner_id=1,
        created_by=1,
        updated_by=1,
    )
    assert agent.name == "Test Agent"
    assert agent.slug == "test-agent"
    assert agent.agent_type == AgentType.CODE_REVIEWER
    assert agent.status == AgentStatus.ACTIVE
    assert agent.model_name == "claude-3-haiku"
    assert agent.max_tokens == 4000
    assert agent.temperature == 0.1
    assert agent.owner_id == 1


def test_user_create_schema():
    """Test UserCreate schema."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User",
    }
    user_create = UserCreate(**user_data)
    assert user_create.email == "test@example.com"
    assert user_create.username == "testuser"
    assert user_create.password == "password123"
    assert user_create.full_name == "Test User"
    assert user_create.is_active is True


def test_project_create_schema():
    """Test ProjectCreate schema."""
    project_data = {
        "name": "Test Project",
        "slug": "test-project",
        "description": "A test project",
        "status": ProjectStatus.ACTIVE,
        "project_type": ProjectType.WEB_APP,
        "repository_url": "https://github.com/user/repo",
    }
    project_create = ProjectCreate(**project_data)
    assert project_create.name == "Test Project"
    assert project_create.slug == "test-project"
    assert project_create.status == ProjectStatus.ACTIVE
    assert project_create.project_type == ProjectType.WEB_APP


def test_agent_create_schema():
    """Test AgentCreate schema."""
    agent_data = {
        "name": "Test Agent",
        "slug": "test-agent",
        "agent_type": AgentType.CODE_REVIEWER,
        "description": "A test agent",
        "model_name": "claude-3-haiku",
    }
    agent_create = AgentCreate(**agent_data)
    assert agent_create.name == "Test Agent"
    assert agent_create.slug == "test-agent"
    assert agent_create.agent_type == AgentType.CODE_REVIEWER
    assert agent_create.model_name == "claude-3-haiku"
    assert agent_create.status == AgentStatus.ACTIVE  # default
