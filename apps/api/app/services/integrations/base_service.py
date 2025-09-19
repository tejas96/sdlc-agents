"""Base integration service class."""

from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
from loguru import logger

from app.core.config import get_settings
from app.models.integration import Integration, IntegrationStatus


class BaseIntegrationService(ABC):
    """Base class for all integration services."""

    def __init__(self, integration: Integration):
        """Initialize the integration service."""
        self.integration = integration
        self.settings = get_settings()
        self.client = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    @abstractmethod
    async def test_connection(self) -> dict[str, Any]:
        """Test the integration connection."""
        pass

    @abstractmethod
    async def get_service_info(self) -> dict[str, Any]:
        """Get service information and capabilities."""
        pass

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        headers = {"Content-Type": "application/json"}

        if self.integration.oauth_token:
            # OAuth token authentication
            headers["Authorization"] = f"Bearer {self.integration.oauth_token}"
        elif hasattr(self, '_get_api_token') and self._get_api_token():
            # API token authentication
            headers["Authorization"] = f"token {self._get_api_token()}"

        return headers

    def _get_base_url(self) -> str:
        """Get the base API URL for the service."""
        return self.integration.api_url or self._get_default_api_url()

    @abstractmethod
    def _get_default_api_url(self) -> str:
        """Get the default API URL for the service."""
        pass

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make an authenticated API request."""
        if not self.client:
            raise RuntimeError("Service must be used as async context manager")

        url = f"{self._get_base_url()}{endpoint}"
        headers = self._get_auth_headers()

        try:
            logger.debug(f"Making {method} request to {url}")

            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method.upper() in ["POST", "PUT", "PATCH"] else None,
                params=params
            )

            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"text": response.text, "status_code": response.status_code}

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed for {url}: {e!s}")
            raise

    def _decrypt_credentials(self) -> dict[str, Any]:
        """Decrypt stored credentials."""
        # TODO: Implement proper decryption
        # For now, assume credentials are stored as JSON
        import json

        if self.integration.credentials:
            try:
                return json.loads(self.integration.credentials)
            except json.JSONDecodeError:
                logger.warning("Failed to parse integration credentials")
                return {}
        return {}

    def _encrypt_credentials(self, credentials: dict[str, Any]) -> str:
        """Encrypt credentials for storage."""
        # TODO: Implement proper encryption
        # For now, just store as JSON (not secure for production)
        import json
        return json.dumps(credentials)

    async def update_integration_status(self, status: IntegrationStatus, message: str = "") -> None:
        """Update the integration status."""
        self.integration.status = status
        # TODO: Update in database
        logger.info(f"Integration {self.integration.name} status updated to {status}: {message}")

    def is_authenticated(self) -> bool:
        """Check if the integration is properly authenticated."""
        return bool(
            self.integration.oauth_token or
            self.integration.credentials or
            (hasattr(self, '_get_api_token') and self._get_api_token())
        )

    def get_rate_limit_info(self) -> dict[str, Any]:
        """Get rate limit information."""
        return {
            "rate_limit": self.integration.rate_limit,
            "rate_limit_remaining": None,  # TODO: Track rate limit usage
            "rate_limit_reset": None
        }
