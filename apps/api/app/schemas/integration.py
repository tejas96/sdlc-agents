"""Integration schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.models.integration import IntegrationType, IntegrationStatus


class IntegrationResponse(BaseModel):
    """Integration response schema."""
    id: int
    name: str
    slug: str
    description: str | None = None
    integration_type: IntegrationType
    status: IntegrationStatus
    config: str | None = None
    api_url: str | None = None
    api_version: str | None = None
    rate_limit: int | None = None
    oauth_client_id: str | None = None
    oauth_scopes: str | None = None
    oauth_expires_at: str | None = None
    webhook_url: str | None = None
    webhook_events: str | None = None
    last_health_check_at: str | None = None
    health_check_status: str | None = None
    total_requests: int
    failed_requests: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True


class IntegrationListResponse(BaseModel):
    """Integration list response schema."""
    integrations: list[IntegrationResponse]
    total: int
    page: int
    size: int
    pages: int
