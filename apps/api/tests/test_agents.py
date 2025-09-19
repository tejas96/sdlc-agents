"""Tests for agent endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.agent import AgentType, AgentStatus


class TestAgentEndpoints:
    """Test agent API endpoints."""

    def test_get_agents_unauthorized(self, client: TestClient):
        """Test getting agents without authentication."""
        response = client.get("/api/v1/agents/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_agent(self, client: TestClient, test_user, auth_headers: dict):
        """Test creating a new agent."""
        agent_data = {
            "name": "Test Code Reviewer",
            "slug": "test-code-reviewer",
            "description": "A test agent for code review",
            "agent_type": AgentType.CODE_REVIEWER,
            "status": AgentStatus.ACTIVE,
            "model_name": "claude-3-haiku",
            "max_tokens": 4000,
            "temperature": 0.1,
            "timeout_seconds": 300,
        }

        response = client.post(
            "/api/v1/agents/",
            json=agent_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["slug"] == agent_data["slug"]
        assert data["agent_type"] == agent_data["agent_type"]
        assert data["owner_id"] == test_user.id

    @pytest.mark.asyncio
    async def test_get_agent_by_id(self, client: TestClient, test_agent, auth_headers: dict):
        """Test getting a specific agent by ID."""
        response = client.get(
            f"/api/v1/agents/{test_agent.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_agent.id
        assert data["name"] == test_agent.name

    @pytest.mark.asyncio
    async def test_update_agent(self, client: TestClient, test_agent: Agent, auth_headers: dict):
        """Test updating an agent."""
        update_data = {
            "name": "Updated Agent Name",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/v1/agents/{test_agent.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_delete_agent(self, client: TestClient, test_agent: Agent, auth_headers: dict):
        """Test deleting an agent."""
        response = client.delete(
            f"/api/v1/agents/{test_agent.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_execute_agent(self, client: TestClient, test_agent: Agent, auth_headers: dict):
        """Test executing an agent."""
        execution_data = {
            "messages": [
                {
                    "type": "user_input",
                    "content": "Analyze this code",
                    "timestamp": "2024-01-15T10:00:00Z"
                }
            ],
            "mcp_configs": {}
        }

        response = client.post(
            f"/api/v1/agents/{test_agent.id}/execute",
            json=execution_data,
            headers=auth_headers
        )
        
        # Should return a streaming response
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/event-stream; charset=utf-8"

    @pytest.mark.asyncio
    async def test_get_agent_executions(self, client: TestClient, test_agent: Agent, auth_headers: dict):
        """Test getting agent execution history."""
        response = client.get(
            f"/api/v1/agents/{test_agent.id}/executions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_agent_not_found(self, client: TestClient, auth_headers: dict):
        """Test accessing non-existent agent."""
        response = client.get(
            "/api/v1/agents/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_duplicate_agent_slug(self, client: TestClient, test_agent: Agent, auth_headers: dict):
        """Test creating agent with duplicate slug."""
        agent_data = {
            "name": "Another Agent",
            "slug": test_agent.slug,  # Same slug as existing agent
            "agent_type": AgentType.CODE_REVIEWER,
        }

        response = client.post(
            "/api/v1/agents/",
            json=agent_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
