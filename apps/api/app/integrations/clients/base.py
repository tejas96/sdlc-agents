"""Contract for all integrations. Every integration must implement this contract."""

from abc import ABC, abstractmethod
from typing import Any

from app.integrations.enum import IntegrationFeature


class IntegrationClientContract(ABC):
    """Contract for all integrations. Every integration must implement this contract."""

    @abstractmethod
    def validate_credentials(self, *, credentials: dict[str, Any]) -> bool:
        """Validate the credentials for the integration."""
        pass

    @abstractmethod
    def features(self) -> list[IntegrationFeature]:
        """Get the features of the integration."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the integration."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the integration."""
        pass
