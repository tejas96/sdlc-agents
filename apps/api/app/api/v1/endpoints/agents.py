"""Agent endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, DatabaseSession
from app.crud.agent import agent_crud
from app.models.agent import AgentCreate, AgentUpdate
from app.schemas.agent import AgentListResponse, AgentResponse

router = APIRouter()


@router.get("/", response_model=AgentListResponse)
async def get_agents(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to retrieve"),
    project_id: int | None = Query(default=None, description="Filter by project ID"),
    agent_type: str | None = Query(default=None, description="Filter by agent type"),
) -> Any:
    """Get all agents for the current user."""
    if project_id:
        agents = await agent_crud.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
    elif agent_type:
        agents = await agent_crud.get_by_type(db, agent_type=agent_type, skip=skip, limit=limit)
    else:
        agents = await agent_crud.get_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    
    total = await agent_crud.count(db)
    
    return {
        "agents": agents,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Get a specific agent by ID."""
    agent = await agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if user owns the agent (or is superuser)
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this agent",
        )
    
    return agent


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Create a new agent."""
    # Check if agent slug already exists
    existing_agent = await agent_crud.get_by_slug(db, slug=agent_in.slug)
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An agent with this slug already exists",
        )
    
    agent = await agent_crud.create(
        db,
        obj_in=agent_in,
        owner_id=current_user.id,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Update an agent."""
    agent = await agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if user owns the agent (or is superuser)
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent",
        )
    
    # Check slug uniqueness if being updated
    if agent_update.slug and agent_update.slug != agent.slug:
        existing_agent = await agent_crud.get_by_slug(db, slug=agent_update.slug)
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An agent with this slug already exists",
            )
    
    agent = await agent_crud.update(
        db,
        db_obj=agent,
        obj_in=agent_update.dict(exclude_unset=True) | {"updated_by": current_user.id},
    )
    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Delete an agent."""
    agent = await agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if user owns the agent (or is superuser)
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this agent",
        )
    
    await agent_crud.remove(db, id=agent_id)
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/execute")
async def execute_agent(
    agent_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Execute an agent manually."""
    agent = await agent_crud.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check if user owns the agent (or is superuser)
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to execute this agent",
        )
    
    # TODO: Implement agent execution logic
    return {"message": "Agent execution started"}
