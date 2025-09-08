"""Workflow endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, DatabaseSession
from app.crud.workflow import workflow_crud
from app.models.workflow import WorkflowCreate, WorkflowUpdate
from app.schemas.workflow import WorkflowListResponse, WorkflowResponse

router = APIRouter()


@router.get("/", response_model=WorkflowListResponse)
async def get_workflows(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to retrieve"),
    project_id: int | None = Query(default=None, description="Filter by project ID"),
    trigger_type: str | None = Query(default=None, description="Filter by trigger type"),
) -> Any:
    """Get all workflows for the current user."""
    if project_id:
        workflows = await workflow_crud.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
    elif trigger_type:
        workflows = await workflow_crud.get_by_trigger_type(
            db, trigger_type=trigger_type, skip=skip, limit=limit
        )
    else:
        workflows = await workflow_crud.get_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    
    total = await workflow_crud.count(db)
    
    return {
        "workflows": workflows,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Get a specific workflow by ID."""
    workflow = await workflow_crud.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    
    # Check if user owns the workflow (or is superuser)
    if workflow.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this workflow",
        )
    
    return workflow


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_in: WorkflowCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Create a new workflow."""
    # Check if workflow slug already exists
    existing_workflow = await workflow_crud.get_by_slug(db, slug=workflow_in.slug)
    if existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A workflow with this slug already exists",
        )
    
    workflow = await workflow_crud.create(
        db,
        obj_in=workflow_in,
        owner_id=current_user.id,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Update a workflow."""
    workflow = await workflow_crud.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    
    # Check if user owns the workflow (or is superuser)
    if workflow.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this workflow",
        )
    
    # Check slug uniqueness if being updated
    if workflow_update.slug and workflow_update.slug != workflow.slug:
        existing_workflow = await workflow_crud.get_by_slug(db, slug=workflow_update.slug)
        if existing_workflow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A workflow with this slug already exists",
            )
    
    workflow = await workflow_crud.update(
        db,
        db_obj=workflow,
        obj_in=workflow_update.dict(exclude_unset=True) | {"updated_by": current_user.id},
    )
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Delete a workflow."""
    workflow = await workflow_crud.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    
    # Check if user owns the workflow (or is superuser)
    if workflow.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this workflow",
        )
    
    await workflow_crud.remove(db, id=workflow_id)
    return {"message": "Workflow deleted successfully"}


@router.post("/{workflow_id}/trigger")
async def trigger_workflow(
    workflow_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Trigger a workflow manually."""
    workflow = await workflow_crud.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    
    # Check if user owns the workflow (or is superuser)
    if workflow.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to trigger this workflow",
        )
    
    # TODO: Implement workflow execution logic
    return {"message": "Workflow triggered successfully"}
