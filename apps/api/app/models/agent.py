"""Agent database model."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import AuditedModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class AgentType(str, Enum):
    """Agent type enumeration."""
    CODE_REVIEWER = "code_reviewer"
    TEST_GENERATOR = "test_generator"
    DOCUMENTATION_WRITER = "documentation_writer"
    BUG_HUNTER = "bug_hunter"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    SECURITY_SCANNER = "security_scanner"
    DEPLOYMENT_MANAGER = "deployment_manager"
    MONITORING_AGENT = "monitoring_agent"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class Agent(AuditedModel, table=True):
    """Agent model for managing AI agents in the system."""

    __tablename__ = "agents"

    name: str = Field(index=True, description="Agent name")
    slug: str = Field(unique=True, index=True, description="Agent URL slug")
    description: str | None = Field(default=None, description="Agent description")
    agent_type: AgentType = Field(description="Type of agent")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Agent status")

    # Agent configuration
    config: str | None = Field(default=None, description="Agent configuration (JSON)")
    prompt_template: str | None = Field(default=None, description="Agent prompt template")
    model_name: str = Field(default="claude-3-haiku", description="LLM model to use")

    # Execution parameters
    max_tokens: int = Field(default=4000, description="Maximum tokens per request")
    temperature: float = Field(default=0.1, description="Model temperature")
    timeout_seconds: int = Field(default=300, description="Request timeout in seconds")

    # Scheduling and triggers
    schedule_cron: str | None = Field(default=None, description="Cron schedule for agent")
    trigger_events: str | None = Field(default=None, description="Trigger events (JSON array)")

    # Metrics and monitoring
    total_executions: int = Field(default=0, description="Total number of executions")
    successful_executions: int = Field(default=0, description="Number of successful executions")
    last_execution_at: str | None = Field(default=None, description="Last execution timestamp")

    # Project association
    project_id: int | None = Field(foreign_key="projects.id", description="Associated project")
    project: "Project" = Relationship(back_populates="agents")

    # Owner
    owner_id: int = Field(foreign_key="users.id", description="Agent owner")
    owner: "User" = Relationship(back_populates="agents")


class AgentBase(SQLModel):
    """Base agent schema for shared properties."""
    name: str
    slug: str
    description: str | None = None
    agent_type: AgentType
    status: AgentStatus = AgentStatus.ACTIVE
    config: str | None = None
    prompt_template: str | None = None
    model_name: str = "claude-3-haiku"
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout_seconds: int = 300
    schedule_cron: str | None = None
    trigger_events: str | None = None
    project_id: int | None = None


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    pass


class AgentUpdate(SQLModel):
    """Schema for updating an agent."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    agent_type: AgentType | None = None
    status: AgentStatus | None = None
    config: str | None = None
    prompt_template: str | None = None
    model_name: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    timeout_seconds: int | None = None
    schedule_cron: str | None = None
    trigger_events: str | None = None
    project_id: int | None = None
