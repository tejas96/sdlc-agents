"""Authentication endpoints."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DatabaseSession, get_current_user
from app.core.auth import create_access_token, create_refresh_token
from app.core.config import get_settings
from app.crud.user import user_crud
from app.models.user import UserCreate
from app.schemas.auth import Token, UserLogin, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin, db: DatabaseSession
) -> dict[str, Any]:
    """Login endpoint that returns access and refresh tokens."""
    user = await user_crud.authenticate(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data=token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, db: DatabaseSession
) -> Any:
    """Register a new user."""
    # Check if user already exists
    user = await user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    user = await user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )
    
    # Create user
    user = await user_crud.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> Any:
    """Get current user information."""
    return current_user


@router.get("/refresh", response_model=Token)
async def refresh_access_token() -> dict[str, Any]:
    """Refresh access token using refresh token."""
    # TODO: Implement refresh token logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token endpoint not implemented",
    )
