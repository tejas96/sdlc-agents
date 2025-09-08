from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, agents, workflows, integrations, monitoring

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad request"},
        422: {"description": "Validation error"},
    },
)

# Project endpoints
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Project not found"},
        422: {"description": "Validation error"},
    },
)

# Agent endpoints
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["Agents"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Agent not found"},
        422: {"description": "Validation error"},
    },
)

# Workflow endpoints
api_router.include_router(
    workflows.router,
    prefix="/workflows",
    tags=["Workflows"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Workflow not found"},
        422: {"description": "Validation error"},
    },
)

# Integration endpoints
api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["Integrations"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad request"},
        404: {"description": "Integration not found"},
        403: {"description": "Forbidden"},
        422: {"description": "Validation error"},
    },
)

# Monitoring endpoints
api_router.include_router(
    monitoring.router,
    prefix="/monitoring",
    tags=["Monitoring"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad request"},
        404: {"description": "Resource not found"},
        502: {"description": "Upstream service error"},
        422: {"description": "Validation error"},
    },
)
