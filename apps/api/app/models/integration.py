"""Integration database model."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import AuditedModel

if TYPE_CHECKING:
    from app.models.user import User


class IntegrationType(str, Enum):
    """Integration type enumeration."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    JIRA = "jira"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    JENKINS = "jenkins"
    DOCKER = "docker"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class IntegrationStatus(str, Enum):
    """Integration status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    EXPIRED = "expired"


class Integration(AuditedModel, table=True):
    """Integration model for external service connections."""
    
    __tablename__ = "integrations"
    
    name: str = Field(index=True, description="Integration name")
    slug: str = Field(unique=True, index=True, description="Integration URL slug")
    description: str | None = Field(default=None, description="Integration description")
    integration_type: IntegrationType = Field(description="Type of integration")
    status: IntegrationStatus = Field(default=IntegrationStatus.ACTIVE, description="Integration status")
    
    # Connection configuration
    config: str | None = Field(default=None, description="Integration configuration (JSON)")
    credentials: str | None = Field(default=None, description="Encrypted credentials (JSON)")
    
    # API settings
    api_url: str | None = Field(default=None, description="API base URL")
    api_version: str | None = Field(default=None, description="API version")
    rate_limit: int | None = Field(default=None, description="Rate limit per hour")
    
    # OAuth settings (for OAuth-based integrations)
    oauth_client_id: str | None = Field(default=None, description="OAuth client ID")
    oauth_scopes: str | None = Field(default=None, description="OAuth scopes (JSON array)")
    oauth_token: str | None = Field(default=None, description="Encrypted OAuth token")
    oauth_refresh_token: str | None = Field(default=None, description="Encrypted OAuth refresh token")
    oauth_expires_at: str | None = Field(default=None, description="OAuth token expiration")
    
    # Webhook settings
    webhook_url: str | None = Field(default=None, description="Webhook URL")
    webhook_secret: str | None = Field(default=None, description="Webhook secret")
    webhook_events: str | None = Field(default=None, description="Webhook events (JSON array)")
    
    # Monitoring and health
    last_health_check_at: str | None = Field(default=None, description="Last health check timestamp")
    health_check_status: str | None = Field(default=None, description="Health check status")
    total_requests: int = Field(default=0, description="Total API requests made")
    failed_requests: int = Field(default=0, description="Failed API requests")
    
    # Owner
    owner_id: int = Field(foreign_key="users.id", description="Integration owner")
    owner: "User" = Relationship(back_populates="integrations")


class IntegrationBase(SQLModel):
    """Base integration schema for shared properties."""
    name: str
    slug: str
    description: str | None = None
    integration_type: IntegrationType
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    config: str | None = None
    api_url: str | None = None
    api_version: str | None = None
    rate_limit: int | None = None
    oauth_client_id: str | None = None
    oauth_scopes: str | None = None
    webhook_url: str | None = None
    webhook_events: str | None = None


class IntegrationCreate(IntegrationBase):
    """Schema for creating a new integration."""
    credentials: str | None = None
    webhook_secret: str | None = None


class IntegrationUpdate(SQLModel):
    """Schema for updating an integration."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    integration_type: IntegrationType | None = None
    status: IntegrationStatus | None = None
    config: str | None = None
    credentials: str | None = None
    api_url: str | None = None
    api_version: str | None = None
    rate_limit: int | None = None
    oauth_client_id: str | None = None
    oauth_scopes: str | None = None
    oauth_token: str | None = None
    oauth_refresh_token: str | None = None
    oauth_expires_at: str | None = None
    webhook_url: str | None = None
    webhook_secret: str | None = None
    webhook_events: str | None = None
