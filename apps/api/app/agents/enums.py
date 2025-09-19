"""Agent enums and identifiers."""

from enum import Enum


class AgentIdentifier(str, Enum):
    """Agent workflow identifiers."""
    CODE_ANALYSIS = "code_analysis"
    TEST_CASE_GENERATION = "test_case_generation"
    REQUIREMENTS_TO_TICKETS = "requirements_to_tickets"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    CODE_REVIEWER = "code_reviewer"


class AgentModule(str, Enum):
    """Agent module categories."""
    DEVELOPMENT = "development"
    PROJECT_MANAGEMENT = "project_management"
    QUALITY_ASSURANCE = "quality_assurance"


class ExecutionStatus(str, Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(str, Enum):
    """Workflow execution steps."""
    PREPARE = "prepare"
    EXECUTE = "execute"
    FINALIZE = "finalize"
