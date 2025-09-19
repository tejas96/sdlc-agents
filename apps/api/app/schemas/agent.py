"""Agent schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.models.agent import AgentStatus, AgentType


class AgentResponse(BaseModel):
    """Agent response schema."""
    id: int
    name: str
    slug: str
    description: str | None = None
    agent_type: AgentType
    status: AgentStatus
    config: str | None = None
    prompt_template: str | None = None
    model_name: str
    max_tokens: int
    temperature: float
    timeout_seconds: int
    schedule_cron: str | None = None
    trigger_events: str | None = None
    total_executions: int
    successful_executions: int
    last_execution_at: str | None = None
    project_id: int | None = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Agent list response schema."""
    agents: list[AgentResponse]
    total: int
    page: int
    size: int
    pages: int
