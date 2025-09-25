"""OAuth authentication system for external service integrations."""

import secrets
import urllib.parse
from typing import Any, Optional

import httpx
from loguru import logger

from app.core.config import get_settings
from app.models.integration import IntegrationType


class OAuthProvider:
    """Base OAuth provider class."""

    def __init__(self, provider_type: IntegrationType):
        self.provider_type = provider_type
        self.settings = get_settings()

    def get_authorization_url(self, redirect_uri: str, scopes: list[str], state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self._get_client_id(),
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "response_type": "code"
        }

        auth_url = self._get_auth_url()
        return f"{auth_url}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> dict[str, Any]:
        """Exchange authorization code for access token."""
        try:
            data = {
                "client_id": self._get_client_id(),
                "client_secret": self._get_client_secret(),
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._get_token_url(),
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                token_data = response.json()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
                "token_type": token_data.get("token_type", "Bearer"),
                "scope": token_data.get("scope")
            }
        except Exception as e:
            logger.error(f"OAuth token exchange failed: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token."""
        try:
            data = {
                "client_id": self._get_client_id(),
                "client_secret": self._get_client_secret(),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._get_token_url(),
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                token_data = response.json()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token", refresh_token),
                "expires_in": token_data.get("expires_in"),
                "token_type": token_data.get("token_type", "Bearer"),
                "scope": token_data.get("scope")
            }
        except Exception as e:
            logger.error(f"OAuth token refresh failed: {e}")
            raise

    def _get_client_id(self) -> str:
        """Get OAuth client ID for the provider."""
        raise NotImplementedError

    def _get_client_secret(self) -> str:
        """Get OAuth client secret for the provider."""
        raise NotImplementedError

    def _get_auth_url(self) -> str:
        """Get OAuth authorization URL for the provider."""
        raise NotImplementedError

    def _get_token_url(self) -> str:
        """Get OAuth token exchange URL for the provider."""
        raise NotImplementedError


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth provider."""

    def __init__(self):
        super().__init__(IntegrationType.GITHUB)

    def _get_client_id(self) -> str:
        return self.settings.GITHUB_CLIENT_ID or ""

    def _get_client_secret(self) -> str:
        return self.settings.GITHUB_CLIENT_SECRET or ""

    def _get_auth_url(self) -> str:
        return "https://github.com/login/oauth/authorize"

    def _get_token_url(self) -> str:
        return "https://github.com/login/oauth/access_token"


class JiraOAuthProvider(OAuthProvider):
    """Jira OAuth provider (OAuth 2.0)."""

    def __init__(self):
        super().__init__(IntegrationType.JIRA)

    def _get_client_id(self) -> str:
        return self.settings.JIRA_CLIENT_ID or ""

    def _get_client_secret(self) -> str:
        return self.settings.JIRA_CLIENT_SECRET or ""

    def _get_auth_url(self) -> str:
        return "https://auth.atlassian.com/authorize"

    def _get_token_url(self) -> str:
        return "https://auth.atlassian.com/oauth/token"

    def get_authorization_url(self, redirect_uri: str, scopes: list[str], state: Optional[str] = None) -> str:
        """Generate Jira OAuth authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "audience": "api.atlassian.com",
            "client_id": self._get_client_id(),
            "scope": " ".join(scopes),
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent"
        }

        return f"{self._get_auth_url()}?{urllib.parse.urlencode(params)}"


class SlackOAuthProvider(OAuthProvider):
    """Slack OAuth provider."""

    def __init__(self):
        super().__init__(IntegrationType.SLACK)

    def _get_client_id(self) -> str:
        return self.settings.SLACK_CLIENT_ID or ""

    def _get_client_secret(self) -> str:
        return self.settings.SLACK_CLIENT_SECRET or ""

    def _get_auth_url(self) -> str:
        return "https://slack.com/oauth/v2/authorize"

    def _get_token_url(self) -> str:
        return "https://slack.com/api/oauth.v2.access"


class OAuthManager:
    """Manages OAuth flows for different providers."""

    def __init__(self):
        self.providers = {
            IntegrationType.GITHUB: GitHubOAuthProvider(),
            IntegrationType.JIRA: JiraOAuthProvider(),
            IntegrationType.SLACK: SlackOAuthProvider(),
        }

    def get_provider(self, provider_type: IntegrationType) -> OAuthProvider:
        """Get OAuth provider for the given type."""
        provider = self.providers.get(provider_type)
        if not provider:
            raise ValueError(f"OAuth provider not supported: {provider_type}")
        return provider

    def get_authorization_url(
        self,
        provider_type: IntegrationType,
        redirect_uri: str,
        scopes: list[str],
        state: Optional[str] = None
    ) -> str:
        """Get authorization URL for a provider."""
        provider = self.get_provider(provider_type)
        return provider.get_authorization_url(redirect_uri, scopes, state)

    async def exchange_code_for_token(
        self,
        provider_type: IntegrationType,
        code: str,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> dict[str, Any]:
        """Exchange authorization code for access token."""
        provider = self.get_provider(provider_type)
        return await provider.exchange_code_for_token(code, redirect_uri, state)

    async def refresh_access_token(
        self,
        provider_type: IntegrationType,
        refresh_token: str
    ) -> dict[str, Any]:
        """Refresh an access token."""
        provider = self.get_provider(provider_type)
        return await provider.refresh_access_token(refresh_token)

    def get_default_scopes(self, provider_type: IntegrationType) -> list[str]:
        """Get default scopes for a provider."""
        default_scopes = {
            IntegrationType.GITHUB: ["repo", "user:email", "read:org"],
            IntegrationType.JIRA: ["read:jira-user", "read:jira-work", "write:jira-work"],
            IntegrationType.SLACK: ["channels:read", "chat:write", "files:write"],
        }
        return default_scopes.get(provider_type, [])


# Global OAuth manager instance
oauth_manager = OAuthManager()
