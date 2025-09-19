"""Workflow database model."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import AuditedModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class WorkflowTrigger(str, Enum):
    """Workflow trigger enumeration."""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    GIT_PUSH = "git_push"
    GIT_PR = "git_pr"
    FILE_CHANGE = "file_change"
    API_CALL = "api_call"


class Workflow(AuditedModel, table=True):
    """Workflow model for managing automated SDLC processes."""

    __tablename__ = "workflows"

    name: str = Field(index=True, description="Workflow name")
    slug: str = Field(unique=True, index=True, description="Workflow URL slug")
    description: str | None = Field(default=None, description="Workflow description")
    status: WorkflowStatus = Field(default=WorkflowStatus.ACTIVE, description="Workflow status")

    # Workflow configuration
    trigger_type: WorkflowTrigger = Field(description="How the workflow is triggered")
    trigger_config: str | None = Field(default=None, description="Trigger configuration (JSON)")
    steps: str = Field(description="Workflow steps definition (JSON)")

    # Scheduling (for scheduled workflows)
    schedule_cron: str | None = Field(default=None, description="Cron schedule")
    timezone: str = Field(default="UTC", description="Timezone for scheduling")

    # Execution settings
    timeout_minutes: int = Field(default=60, description="Workflow timeout in minutes")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    parallel_execution: bool = Field(default=False, description="Allow parallel execution")

    # Metrics and monitoring
    total_runs: int = Field(default=0, description="Total number of runs")
    successful_runs: int = Field(default=0, description="Number of successful runs")
    failed_runs: int = Field(default=0, description="Number of failed runs")
    last_run_at: str | None = Field(default=None, description="Last run timestamp")
    last_run_status: str | None = Field(default=None, description="Last run status")
    average_duration_seconds: float | None = Field(default=None, description="Average execution duration")

    # Project association
    project_id: int | None = Field(foreign_key="projects.id", description="Associated project")
    project: "Project" = Relationship(back_populates="workflows")

    # Owner
    owner_id: int = Field(foreign_key="users.id", description="Workflow owner")
    owner: "User" = Relationship(back_populates="workflows")


class WorkflowBase(SQLModel):
    """Base workflow schema for shared properties."""
    name: str
    slug: str
    description: str | None = None
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    trigger_type: WorkflowTrigger
    trigger_config: str | None = None
    steps: str
    schedule_cron: str | None = None
    timezone: str = "UTC"
    timeout_minutes: int = 60
    max_retries: int = 3
    parallel_execution: bool = False
    project_id: int | None = None


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new workflow."""
    pass


class WorkflowUpdate(SQLModel):
    """Schema for updating a workflow."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    status: WorkflowStatus | None = None
    trigger_type: WorkflowTrigger | None = None
    trigger_config: str | None = None
    steps: str | None = None
    schedule_cron: str | None = None
    timezone: str | None = None
    timeout_minutes: int | None = None
    max_retries: int | None = None
    parallel_execution: bool | None = None
    project_id: int | None = None
