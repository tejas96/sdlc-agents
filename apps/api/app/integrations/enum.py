"""Integrations enum."""

from enum import Enum


class IntegrationProvider(str, Enum):
    """Integration provider enumeration."""

    # Code repositories
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    # Project management
    JIRA = "jira"
    CLICKUP = "clickup"
    # Communication
    SLACK = "slack"
    DISCORD = "discord"
    # Monitoring
    SENTRY = "sentry"
    DATADOG = "datadog"
    PAGERDUTY = "pagerduty"
    NEW_RELIC = "newrelic"
    GRAFANA = "grafana"
    CLOUDWATCH = "cloudwatch"
    # Deployment
    HEROKU = "heroku"
    AWS = "aws"


class IntegrationFeature(str, Enum):
    """Integration feature enumeration."""

    CODE_REPOSITORY = "code_repository"
    BRANCHES = "branches"
    PULL_REQUESTS = "pull_requests"
    ISSUES = "issues"
    WIKI = "wiki"
    PROJECT_MANAGEMENT = "project_management"
    COMMUNICATION = "communication"
    SPACES = "spaces"
    INCIDENTS = "incidents"
    TICKETS = "tickets"
    METRICS = "metrics"
    ALERTS = "alerts"
    LOGS = "logs"
    MONITORING = "monitoring"
    MESSAGING = "messaging"
    STORAGE = "storage"
    ANALYTICS = "analytics"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    OTHER = "other"


class AuthType(str, Enum):
    """Authentication type enumeration."""

    BASIC = "basic"
    OAUTH = "oauth"
    API_KEY = "api_key"
    PAT = "pat"
