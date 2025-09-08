"""Authentication schemas."""

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    username: str
    full_name: str | None = None
    is_active: bool
    avatar_url: str | None = None
    bio: str | None = None
    organization: str | None = None
    role: str | None = None
    timezone: str = "UTC"
    theme: str = "light"
    github_username: str | None = None
    slack_user_id: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema."""
    user_id: int | None = None
    email: str | None = None
