"""Dashboard and analytics endpoints."""

from typing import Any

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DatabaseSession
from app.models.agent import Agent, AgentStatus
from app.models.project import Project, ProjectStatus
from app.models.workflow import Workflow

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Get dashboard statistics for the current user."""

    # Get agent statistics
    agent_stats_query = select(
        func.count(Agent.id).label("total_agents"),
        func.sum(func.case((Agent.status == AgentStatus.ACTIVE, 1), else_=0)).label("active_agents"),
        func.sum(Agent.total_executions).label("total_executions"),
        func.sum(Agent.successful_executions).label("successful_executions"),
    ).where(Agent.owner_id == current_user.id)

    agent_stats_result = await db.execute(agent_stats_query)
    agent_stats = agent_stats_result.first()

    # Get project statistics
    project_stats_query = select(
        func.count(Project.id).label("total_projects"),
        func.sum(func.case((Project.status == ProjectStatus.ACTIVE, 1), else_=0)).label("active_projects"),
        func.sum(func.case((Project.status == ProjectStatus.COMPLETED, 1), else_=0)).label("completed_projects"),
    ).where(Project.owner_id == current_user.id)

    project_stats_result = await db.execute(project_stats_query)
    project_stats = project_stats_result.first()

    # Get workflow statistics
    workflow_stats_query = select(
        func.count(Workflow.id).label("total_workflows"),
        func.sum(Workflow.total_executions).label("workflow_executions"),
    ).where(Workflow.owner_id == current_user.id)

    workflow_stats_result = await db.execute(workflow_stats_query)
    workflow_stats = workflow_stats_result.first()

    # Calculate success rate
    total_executions = agent_stats.total_executions or 0
    successful_executions = agent_stats.successful_executions or 0
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0

    # Calculate average response time (mock for now)
    avg_response_time = "2.4h"  # TODO: Calculate from actual execution data

    # Calculate system uptime (mock for now)
    system_uptime = "98.7%"  # TODO: Calculate from monitoring data

    return {
        "active_agents": agent_stats.active_agents or 0,
        "total_agents": agent_stats.total_agents or 0,
        "tasks_completed": successful_executions,
        "total_executions": total_executions,
        "success_rate": round(success_rate, 1),
        "avg_response_time": avg_response_time,
        "system_uptime": system_uptime,
        "active_projects": project_stats.active_projects or 0,
        "total_projects": project_stats.total_projects or 0,
        "completed_projects": project_stats.completed_projects or 0,
        "total_workflows": workflow_stats.total_workflows or 0,
        "workflow_executions": workflow_stats.workflow_executions or 0,
        "trends": {
            "active_agents": 24,  # TODO: Calculate from historical data
            "tasks_completed": 18,
            "avg_response_time": -12,
            "system_uptime": 31,
        }
    }


@router.get("/activity")
async def get_recent_activity(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Get recent activity for the dashboard."""

    # TODO: Implement activity tracking
    # This would typically come from an activity log table

    # Mock activity data for now
    activities = [
        {
            "id": 1,
            "type": "agent_execution",
            "title": "Code Analysis completed",
            "description": "Generated documentation for project XYZ",
            "timestamp": "2024-01-15T10:30:00Z",
            "agent_id": 1,
        },
        {
            "id": 2,
            "type": "project_created",
            "title": "New project created",
            "description": "E-commerce Platform project initialized",
            "timestamp": "2024-01-15T09:15:00Z",
            "project_id": 1,
        },
        {
            "id": 3,
            "type": "workflow_completed",
            "title": "Test generation workflow completed",
            "description": "Generated 25 test cases with 85% coverage",
            "timestamp": "2024-01-15T08:45:00Z",
            "workflow_id": 1,
        },
    ]

    return activities[:limit]


@router.get("/metrics")
async def get_dashboard_metrics(
    db: DatabaseSession,
    current_user: CurrentUser,
    timeframe: str = "7d",  # 1d, 7d, 30d, 90d
) -> dict[str, Any]:
    """Get detailed metrics for charts and analytics."""

    # TODO: Implement time-series metrics collection
    # This would typically aggregate data based on the timeframe

    # Mock metrics data for now
    metrics = {
        "agent_executions": [
            {"date": "2024-01-09", "value": 12},
            {"date": "2024-01-10", "value": 18},
            {"date": "2024-01-11", "value": 15},
            {"date": "2024-01-12", "value": 22},
            {"date": "2024-01-13", "value": 25},
            {"date": "2024-01-14", "value": 19},
            {"date": "2024-01-15", "value": 28},
        ],
        "success_rates": [
            {"agent_type": "code_analysis", "success_rate": 94.5},
            {"agent_type": "test_generation", "success_rate": 87.2},
            {"agent_type": "requirements_to_tickets", "success_rate": 91.8},
            {"agent_type": "code_reviewer", "success_rate": 89.3},
            {"agent_type": "root_cause_analysis", "success_rate": 85.7},
        ],
        "project_progress": [
            {"project": "E-commerce Platform", "progress": 78},
            {"project": "Mobile Banking App", "progress": 92},
            {"project": "Healthcare Data Pipeline", "progress": 100},
            {"project": "IoT Device Management", "progress": 25},
        ],
        "timeframe": timeframe,
    }

    return metrics
