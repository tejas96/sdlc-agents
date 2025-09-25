import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Paths:
    ROOT_DIR = Path(__file__).resolve().parents[2]
    API_DIR = ROOT_DIR
    APP_DIR = ROOT_DIR / "app"


class Settings(BaseSettings):
    """Application settings and configuration"""

    # API Configuration
    PROJECT_NAME: str = Field(default="SDLC Agents API", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: str = Field(default="*", description="Allowed CORS origins (comma-separated)")

    def get_cors_origins(self) -> list[str]:
        """Get parsed CORS origins as list"""
        if not self.BACKEND_CORS_ORIGINS:
            return []

        # Handle wildcard case
        if self.BACKEND_CORS_ORIGINS.strip() == "*":
            return ["*"]

        if self.BACKEND_CORS_ORIGINS.startswith("[") and self.BACKEND_CORS_ORIGINS.endswith("]"):
            try:
                parsed = json.loads(self.BACKEND_CORS_ORIGINS)
                if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
                    return parsed
                return []
            except (json.JSONDecodeError, ValueError):
                return []
        return [i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",") if i.strip()]

    # Database Configuration
    DATABASE_URL: str = Field(description="Database connection URL")
    DATABASE_ECHO: bool = Field(default=True, description="Echo SQL queries for debugging")

    # Database Pool Configuration
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=40, description="Database connection pool max overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database connection pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=1800, description="Database connection pool recycle time in seconds")

    # JWT Configuration
    SECRET_KEY: str = Field(description="Secret key for JWT token generation")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")

    # Environment Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="DEBUG", description="Logging level")

    # Server Configuration
    PORT: int = Field(default=8001, description="Server port")

    # Security Configuration
    MAX_REQUEST_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum request size in bytes")  # 10MB

    # Documentation Configuration
    ENABLE_DOCS: bool = Field(default=True, description="Enable API documentation")
    ENABLE_REDOC: bool = Field(default=True, description="Enable ReDoc documentation")

    # SDLC Agents Configuration
    AGENTS_DIR: str | None = Field(default=None, description="Root directory for per-session agent workspaces")
    PROJECTS_DIR: str | None = Field(default=None, description="Root directory for project repositories")

    # External Service Configuration
    GITHUB_CLIENT_ID: str | None = Field(default=None, description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: str | None = Field(default=None, description="GitHub OAuth client secret")
    JIRA_CLIENT_ID: str | None = Field(default=None, description="Jira OAuth client ID")
    JIRA_CLIENT_SECRET: str | None = Field(default=None, description="Jira OAuth client secret")
    JIRA_API_URL: str | None = Field(default=None, description="Jira API base URL")
    JIRA_USERNAME: str | None = Field(default=None, description="Jira username")
    JIRA_API_TOKEN: str | None = Field(default=None, description="Jira API token")
    SLACK_CLIENT_ID: str | None = Field(default=None, description="Slack OAuth client ID")
    SLACK_CLIENT_SECRET: str | None = Field(default=None, description="Slack OAuth client secret")
    SLACK_BOT_TOKEN: str | None = Field(default=None, description="Slack bot token")
    CONFLUENCE_API_URL: str | None = Field(default=None, description="Confluence API base URL")
    SENTRY_DSN: str | None = Field(default=None, description="Sentry DSN for error tracking")

    # AI/LLM Configuration
    ANTHROPIC_API_KEY: str | None = Field(default=None, description="Anthropic Claude API key")
    OPENAI_API_KEY: str | None = Field(default=None, description="OpenAI API key")

    # Redis Configuration
    REDIS_URL: str | None = Field(default=None, description="Redis connection URL")

    # Celery Configuration
    CELERY_BROKER_URL: str | None = Field(default=None, description="Celery broker URL")
    CELERY_RESULT_BACKEND: str | None = Field(default=None, description="Celery result backend URL")

    # Monitoring Configuration
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    SENTRY_ENABLED: bool = Field(default=False, description="Enable Sentry error tracking")

    # Security Configuration
    ENCRYPTION_KEY: str | None = Field(default=None, description="Key for encrypting sensitive data")
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=90, description="Audit log retention period")

    # Performance Configuration
    CACHE_TTL_SECONDS: int = Field(default=900, description="Default cache TTL in seconds")
    MAX_CONCURRENT_AGENTS: int = Field(default=10, description="Maximum concurrent agent executions")
    AGENT_TIMEOUT_MINUTES: int = Field(default=30, description="Agent execution timeout")

    model_config = SettingsConfigDict(
        env_file=str(Paths.API_DIR / ".env"),  # Look for .env in API directory
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Changed from "forbid" to "ignore" to handle extra env vars
    )


@lru_cache
def get_settings() -> Settings:
    """Get the application settings"""
    return Settings()  # type: ignore
