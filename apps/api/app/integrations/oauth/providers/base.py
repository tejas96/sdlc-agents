from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TokenResult:
    """Result from token generation."""

    access_token: str | None
    credentials_updated: bool = False
    updated_credentials: dict[str, Any] | None = None
    expires_in: int | None = None
    token_type: str | None = None
    scope: str | None = None
    refresh_token: str | None = None


class OAuthProviderContract(ABC):
    """Base OAuth provider class."""

    @abstractmethod
    async def validate_credentials(self, credentials: dict[str, Any]) -> dict[str, Any]:
        """Validate the credentials for the provider."""
        pass

    @abstractmethod
    async def generate_access_token(self, credentials: dict[str, Any]) -> TokenResult:
        """Generate an access token for the provider."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the provider."""
        pass

    @abstractmethod
    def get_authorization_url(self, redirect_uri: str, scopes: list[str], state: Optional[str] = None) -> str:
        """Get authorization URL for a provider."""
        pass
