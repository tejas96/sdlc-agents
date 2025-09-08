"""Workflow schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.models.workflow import WorkflowStatus, WorkflowTrigger


class WorkflowResponse(BaseModel):
    """Workflow response schema."""
    id: int
    name: str
    slug: str
    description: str | None = None
    status: WorkflowStatus
    trigger_type: WorkflowTrigger
    trigger_config: str | None = None
    steps: str
    schedule_cron: str | None = None
    timezone: str
    timeout_minutes: int
    max_retries: int
    parallel_execution: bool
    total_runs: int
    successful_runs: int
    failed_runs: int
    last_run_at: str | None = None
    last_run_status: str | None = None
    average_duration_seconds: float | None = None
    project_id: int | None = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    """Workflow list response schema."""
    workflows: list[WorkflowResponse]
    total: int
    page: int
    size: int
    pages: int
