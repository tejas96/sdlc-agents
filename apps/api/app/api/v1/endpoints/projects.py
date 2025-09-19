"""Project endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DatabaseSession
from app.crud.project import project_crud
from app.models.project import ProjectCreate, ProjectUpdate
from app.schemas.project import ProjectListResponse, ProjectResponse

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to retrieve"),
) -> Any:
    """Get all projects for the current user."""
    projects = await project_crud.get_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    total = await project_crud.count(db)

    return {
        "projects": projects,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Get a specific project by ID."""
    project = await project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check if user owns the project (or is superuser)
    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project",
        )

    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Create a new project."""
    # Check if project slug already exists
    existing_project = await project_crud.get_by_slug(db, slug=project_in.slug)
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project with this slug already exists",
        )

    project = await project_crud.create(
        db,
        obj_in=project_in,
        owner_id=current_user.id,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Update a project."""
    project = await project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check if user owns the project (or is superuser)
    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this project",
        )

    # Check slug uniqueness if being updated
    if project_update.slug and project_update.slug != project.slug:
        existing_project = await project_crud.get_by_slug(db, slug=project_update.slug)
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A project with this slug already exists",
            )

    project = await project_crud.update(
        db,
        db_obj=project,
        obj_in=project_update.dict(exclude_unset=True) | {"updated_by": current_user.id},
    )
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Delete a project."""
    project = await project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check if user owns the project (or is superuser)
    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this project",
        )

    await project_crud.remove(db, id=project_id)
    return {"message": "Project deleted successfully"}
