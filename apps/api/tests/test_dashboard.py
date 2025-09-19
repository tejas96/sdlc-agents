"""Tests for dashboard endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.models.user import User


class TestDashboardEndpoints:
    """Test dashboard API endpoints."""

    def test_get_dashboard_stats_unauthorized(self, client: TestClient):
        """Test getting dashboard stats without authentication."""
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting dashboard statistics."""
        response = client.get(
            "/api/v1/dashboard/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        required_fields = [
            "active_agents", "total_agents", "tasks_completed", 
            "total_executions", "success_rate", "avg_response_time",
            "system_uptime", "active_projects", "total_projects",
            "completed_projects", "total_workflows", "workflow_executions"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Verify trends data
        assert "trends" in data
        assert isinstance(data["trends"], dict)

    @pytest.mark.asyncio
    async def test_get_recent_activity(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting recent activity."""
        response = client.get(
            "/api/v1/dashboard/activity",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If there's activity data, verify structure
        if data:
            activity = data[0]
            required_fields = ["id", "type", "title", "description", "timestamp"]
            for field in required_fields:
                assert field in activity

    @pytest.mark.asyncio
    async def test_get_dashboard_metrics(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting dashboard metrics."""
        response = client.get(
            "/api/v1/dashboard/metrics?timeframe=7d",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify metrics structure
        expected_fields = ["agent_executions", "success_rates", "project_progress", "timeframe"]
        for field in expected_fields:
            assert field in data
        
        assert data["timeframe"] == "7d"
