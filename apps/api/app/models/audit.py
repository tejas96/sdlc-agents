"""Audit logging models for security and compliance tracking."""

from enum import Enum
from typing import Any, Optional

from app.models.base import BaseModel
from sqlmodel import Field, SQLModel


class AuditEventType(str, Enum):
    """Types of audit events."""

    # Authentication events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    PASSWORD_CHANGE = "auth.password.change"
    PASSWORD_RESET = "auth.password.reset"
    TOKEN_REFRESH = "auth.token.refresh"

    # User management events
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_ACTIVATE = "user.activate"
    USER_DEACTIVATE = "user.deactivate"

    # Role and permission events
    ROLE_ASSIGN = "rbac.role.assign"
    ROLE_REVOKE = "rbac.role.revoke"
    PERMISSION_GRANT = "rbac.permission.grant"
    PERMISSION_REVOKE = "rbac.permission.revoke"

    # Project events
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"
    PROJECT_VIEW = "project.view"

    # Agent events
    AGENT_CREATE = "agent.create"
    AGENT_UPDATE = "agent.update"
    AGENT_DELETE = "agent.delete"
    AGENT_EXECUTE = "agent.execute"
    AGENT_VIEW = "agent.view"

    # Workflow events
    WORKFLOW_CREATE = "workflow.create"
    WORKFLOW_UPDATE = "workflow.update"
    WORKFLOW_DELETE = "workflow.delete"
    WORKFLOW_EXECUTE = "workflow.execute"
    WORKFLOW_VIEW = "workflow.view"

    # Integration events
    INTEGRATION_CREATE = "integration.create"
    INTEGRATION_UPDATE = "integration.update"
    INTEGRATION_DELETE = "integration.delete"
    INTEGRATION_TEST = "integration.test"
    INTEGRATION_OAUTH = "integration.oauth"

    # File events
    FILE_UPLOAD = "file.upload"
    FILE_DOWNLOAD = "file.download"
    FILE_DELETE = "file.delete"

    # System events
    SYSTEM_CONFIG_CHANGE = "system.config.change"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_RESTORE = "system.restore"
    SYSTEM_MAINTENANCE = "system.maintenance"

    # Security events
    UNAUTHORIZED_ACCESS = "security.unauthorized.access"
    RATE_LIMIT_EXCEEDED = "security.rate_limit.exceeded"
    SUSPICIOUS_ACTIVITY = "security.suspicious.activity"
    DATA_EXPORT = "security.data.export"
    ADMIN_ACTION = "security.admin.action"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(BaseModel, table=True):
    """Audit log model for tracking all system activities."""

    __tablename__ = "audit_logs"

    # Event information
    event_type: AuditEventType = Field(index=True, description="Type of audit event")
    event_category: str = Field(index=True, description="Category of the event (auth, user, project, etc.)")
    severity: AuditSeverity = Field(default=AuditSeverity.LOW, description="Event severity level")

    # User and session information
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", description="User who performed the action")
    username: Optional[str] = Field(default=None, description="Username at time of action")
    session_id: Optional[str] = Field(default=None, description="Session ID")

    # Request information
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    request_method: Optional[str] = Field(default=None, description="HTTP request method")
    request_path: Optional[str] = Field(default=None, description="Request path")

    # Resource information
    resource_type: Optional[str] = Field(default=None, description="Type of resource affected")
    resource_id: Optional[str] = Field(default=None, description="ID of the resource affected")
    resource_name: Optional[str] = Field(default=None, description="Name of the resource affected")

    # Event details
    action: str = Field(description="Action performed")
    description: str = Field(description="Human-readable description of the event")

    # Additional context
    event_metadata: Optional[str] = Field(default=None, description="Additional event metadata as JSON")
    request_data: Optional[str] = Field(default=None, description="Request data (sanitized)")
    response_status: Optional[int] = Field(default=None, description="HTTP response status code")

    # Result information
    success: bool = Field(default=True, description="Whether the action was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if action failed")

    # Timing information
    duration_ms: Optional[int] = Field(default=None, description="Action duration in milliseconds")

    # Compliance and security
    compliance_tags: Optional[str] = Field(default=None, description="Compliance-related tags as JSON")
    risk_score: Optional[int] = Field(default=0, description="Risk score for the event (0-100)")


class AuditLogCreate(SQLModel):
    """Schema for creating audit log entries."""

    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.LOW
    user_id: Optional[int] = None
    username: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    action: str
    description: str
    event_metadata: Optional[dict[str, Any]] = None
    request_data: Optional[dict[str, Any]] = None
    response_status: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    compliance_tags: Optional[list[str]] = None
    risk_score: Optional[int] = 0


class AuditLogResponse(SQLModel):
    """Schema for audit log responses."""

    id: int
    event_type: AuditEventType
    event_category: str
    severity: AuditSeverity
    user_id: Optional[int]
    username: Optional[str]
    ip_address: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    resource_name: Optional[str]
    action: str
    description: str
    success: bool
    error_message: Optional[str]
    created_at: str
    risk_score: Optional[int]


class AuditLogFilter(SQLModel):
    """Schema for filtering audit logs."""

    event_type: Optional[AuditEventType] = None
    event_category: Optional[str] = None
    severity: Optional[AuditSeverity] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    success: Optional[bool] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    ip_address: Optional[str] = None
    min_risk_score: Optional[int] = None
    max_risk_score: Optional[int] = None
