"""Monitoring endpoints."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, DatabaseSession
from app.crud.agent import agent_crud
from app.crud.integration import integration_crud
from app.crud.project import project_crud
from app.crud.workflow import workflow_crud

router = APIRouter()


@router.get("/health")
async def get_health_status() -> dict[str, str]:
    """Get overall system health status."""
    return {
        "status": "healthy",
        "service": "SDLC Agents API",
        "message": "System is operational",
    }


@router.get("/stats")
async def get_system_stats(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Get system statistics for the current user."""
    # Count user's resources
    user_projects = await project_crud.get_by_owner(db, owner_id=current_user.id)
    user_agents = await agent_crud.get_by_owner(db, owner_id=current_user.id)
    user_workflows = await workflow_crud.get_by_owner(db, owner_id=current_user.id)
    user_integrations = await integration_crud.get_by_owner(db, owner_id=current_user.id)

    # Active agents and workflows
    active_agents = await agent_crud.get_active(db)
    active_workflows = await workflow_crud.get_active(db)

    return {
        "user_stats": {
            "projects": len(user_projects),
            "agents": len(user_agents),
            "workflows": len(user_workflows),
            "integrations": len(user_integrations),
        },
        "system_stats": {
            "active_agents": len(active_agents),
            "active_workflows": len(active_workflows),
        },
        "recent_activity": {
            "last_project_created": user_projects[0].created_at if user_projects else None,
            "last_agent_created": user_agents[0].created_at if user_agents else None,
            "last_workflow_created": user_workflows[0].created_at if user_workflows else None,
        }
    }


@router.get("/metrics")
async def get_metrics(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Get detailed metrics and performance data."""
    # Agent execution metrics
    user_agents = await agent_crud.get_by_owner(db, owner_id=current_user.id)
    total_executions = sum(agent.total_executions for agent in user_agents)
    successful_executions = sum(agent.successful_executions for agent in user_agents)

    # Workflow execution metrics
    user_workflows = await workflow_crud.get_by_owner(db, owner_id=current_user.id)
    total_workflow_runs = sum(workflow.total_runs for workflow in user_workflows)
    successful_workflow_runs = sum(workflow.successful_runs for workflow in user_workflows)

    # Integration health
    user_integrations = await integration_crud.get_by_owner(db, owner_id=current_user.id)
    active_integrations = [i for i in user_integrations if i.status == "active"]

    return {
        "agent_metrics": {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
        },
        "workflow_metrics": {
            "total_runs": total_workflow_runs,
            "successful_runs": successful_workflow_runs,
            "success_rate": (successful_workflow_runs / total_workflow_runs * 100) if total_workflow_runs > 0 else 0,
        },
        "integration_metrics": {
            "total_integrations": len(user_integrations),
            "active_integrations": len(active_integrations),
            "health_rate": (len(active_integrations) / len(user_integrations) * 100) if user_integrations else 0,
        }
    }
