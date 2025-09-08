"""User database model."""

from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.agent import Agent
    from app.models.workflow import Workflow
    from app.models.integration import Integration


class User(BaseModel, table=True):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    email: str = Field(unique=True, index=True, description="User email address")
    username: str = Field(unique=True, index=True, description="Username")
    full_name: str | None = Field(default=None, description="Full name")
    hashed_password: str = Field(description="Hashed password")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_superuser: bool = Field(default=False, description="Whether user has superuser privileges")
    avatar_url: str | None = Field(default=None, description="Avatar URL")
    bio: str | None = Field(default=None, description="User biography")
    
    # Organization fields
    organization: str | None = Field(default=None, description="Organization name")
    role: str | None = Field(default=None, description="User role in organization")
    
    # Preferences
    timezone: str = Field(default="UTC", description="User timezone")
    theme: str = Field(default="light", description="UI theme preference")
    
    # External integrations
    github_username: str | None = Field(default=None, description="GitHub username")
    slack_user_id: str | None = Field(default=None, description="Slack user ID")
    
    # Relationships
    owned_projects: List["Project"] = Relationship(back_populates="owner")
    agents: List["Agent"] = Relationship(back_populates="owner")
    workflows: List["Workflow"] = Relationship(back_populates="owner")
    integrations: List["Integration"] = Relationship(back_populates="owner")


class UserBase(SQLModel):
    """Base user schema for shared properties."""
    email: str
    username: str
    full_name: str | None = None
    is_active: bool = True
    avatar_url: str | None = None
    bio: str | None = None
    organization: str | None = None
    role: str | None = None
    timezone: str = "UTC"
    theme: str = "light"
    github_username: str | None = None
    slack_user_id: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserUpdate(SQLModel):
    """Schema for updating a user."""
    email: str | None = None
    username: str | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    avatar_url: str | None = None
    bio: str | None = None
    organization: str | None = None
    role: str | None = None
    timezone: str | None = None
    theme: str | None = None
    github_username: str | None = None
    slack_user_id: str | None = None
