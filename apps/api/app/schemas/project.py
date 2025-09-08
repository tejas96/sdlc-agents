"""Project schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.models.project import ProjectStatus, ProjectType


class ProjectResponse(BaseModel):
    """Project response schema."""
    id: int
    name: str
    slug: str
    description: str | None = None
    status: ProjectStatus
    project_type: ProjectType
    repository_url: str | None = None
    repository_branch: str
    local_path: str | None = None
    tech_stack: str | None = None
    tags: str | None = None
    environment_config: str | None = None
    build_config: str | None = None
    deployment_config: str | None = None
    jira_project_key: str | None = None
    slack_channel_id: str | None = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Project list response schema."""
    projects: list[ProjectResponse]
    total: int
    page: int
    size: int
    pages: int
