"""Project database model."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import AuditedModel

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.user import User
    from app.models.workflow import Workflow


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class ProjectType(str, Enum):
    """Project type enumeration."""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    LIBRARY = "library"
    API = "api"
    MICROSERVICE = "microservice"
    DATA_PIPELINE = "data_pipeline"
    ML_PROJECT = "ml_project"
    OTHER = "other"


class Project(AuditedModel, table=True):
    """Project model for managing software projects."""

    __tablename__ = "projects"

    name: str = Field(index=True, description="Project name")
    slug: str = Field(unique=True, index=True, description="Project URL slug")
    description: str | None = Field(default=None, description="Project description")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, description="Project status")
    project_type: ProjectType = Field(default=ProjectType.OTHER, description="Project type")

    # Repository information
    repository_url: str | None = Field(default=None, description="Git repository URL")
    repository_branch: str = Field(default="main", description="Default branch")
    local_path: str | None = Field(default=None, description="Local repository path")

    # Project metadata
    tech_stack: str | None = Field(default=None, description="Technology stack (JSON array)")
    tags: str | None = Field(default=None, description="Project tags (JSON array)")

    # Configuration
    environment_config: str | None = Field(default=None, description="Environment configuration (JSON)")
    build_config: str | None = Field(default=None, description="Build configuration (JSON)")
    deployment_config: str | None = Field(default=None, description="Deployment configuration (JSON)")

    # External integrations
    jira_project_key: str | None = Field(default=None, description="Jira project key")
    slack_channel_id: str | None = Field(default=None, description="Slack channel ID")

    # Relationships
    owner_id: int = Field(foreign_key="users.id", description="Project owner")
    owner: "User" = Relationship(back_populates="owned_projects")
    agents: list["Agent"] = Relationship(back_populates="project")
    workflows: list["Workflow"] = Relationship(back_populates="project")


class ProjectBase(SQLModel):
    """Base project schema for shared properties."""
    name: str
    slug: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    project_type: ProjectType = ProjectType.OTHER
    repository_url: str | None = None
    repository_branch: str = "main"
    local_path: str | None = None
    tech_stack: str | None = None
    tags: str | None = None
    environment_config: str | None = None
    build_config: str | None = None
    deployment_config: str | None = None
    jira_project_key: str | None = None
    slack_channel_id: str | None = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(SQLModel):
    """Schema for updating a project."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    project_type: ProjectType | None = None
    repository_url: str | None = None
    repository_branch: str | None = None
    local_path: str | None = None
    tech_stack: str | None = None
    tags: str | None = None
    environment_config: str | None = None
    build_config: str | None = None
    deployment_config: str | None = None
    jira_project_key: str | None = None
    slack_channel_id: str | None = None
