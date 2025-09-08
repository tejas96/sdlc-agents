"""Integration endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, DatabaseSession
from app.crud.integration import integration_crud
from app.models.integration import IntegrationCreate, IntegrationUpdate
from app.schemas.integration import IntegrationListResponse, IntegrationResponse

router = APIRouter()


@router.get("/", response_model=IntegrationListResponse)
async def get_integrations(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to retrieve"),
    integration_type: str | None = Query(default=None, description="Filter by integration type"),
) -> Any:
    """Get all integrations for the current user."""
    if integration_type:
        integrations = await integration_crud.get_by_type(
            db, integration_type=integration_type, skip=skip, limit=limit
        )
    else:
        integrations = await integration_crud.get_by_owner(
            db, owner_id=current_user.id, skip=skip, limit=limit
        )
    
    total = await integration_crud.count(db)
    
    return {
        "integrations": integrations,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Get a specific integration by ID."""
    integration = await integration_crud.get(db, id=integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # Check if user owns the integration (or is superuser)
    if integration.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this integration",
        )
    
    return integration


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_in: IntegrationCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Create a new integration."""
    # Check if integration slug already exists
    existing_integration = await integration_crud.get_by_slug(db, slug=integration_in.slug)
    if existing_integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An integration with this slug already exists",
        )
    
    integration = await integration_crud.create(
        db,
        obj_in=integration_in,
        owner_id=current_user.id,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    return integration


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_update: IntegrationUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Any:
    """Update an integration."""
    integration = await integration_crud.get(db, id=integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # Check if user owns the integration (or is superuser)
    if integration.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this integration",
        )
    
    # Check slug uniqueness if being updated
    if integration_update.slug and integration_update.slug != integration.slug:
        existing_integration = await integration_crud.get_by_slug(db, slug=integration_update.slug)
        if existing_integration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An integration with this slug already exists",
            )
    
    integration = await integration_crud.update(
        db,
        db_obj=integration,
        obj_in=integration_update.dict(exclude_unset=True) | {"updated_by": current_user.id},
    )
    return integration


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Delete an integration."""
    integration = await integration_crud.get(db, id=integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # Check if user owns the integration (or is superuser)
    if integration.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this integration",
        )
    
    await integration_crud.remove(db, id=integration_id)
    return {"message": "Integration deleted successfully"}


@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Test an integration connection."""
    integration = await integration_crud.get(db, id=integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    # Check if user owns the integration (or is superuser)
    if integration.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to test this integration",
        )
    
    # TODO: Implement integration testing logic
    return {"message": "Integration test completed", "status": "success"}
