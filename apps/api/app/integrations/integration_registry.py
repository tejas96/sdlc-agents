"""Registry for all integrations. Every integration must be registered here."""

from collections.abc import Callable

from app.integrations.clients.base import IntegrationClientContract
from app.integrations.enum import IntegrationProvider
from app.integrations.oauth.providers.base import OAuthProviderContract


class IntegrationRegistry:
    """Registry for all integrations."""

    def __init__(self) -> None:
        self._providers: dict[IntegrationProvider, type[IntegrationClientContract]] = {}
        self._providers_oauth: dict[IntegrationProvider, type[OAuthProviderContract]] = {}

    def register_provider(
        self, provider: IntegrationProvider
    ) -> Callable[[type[IntegrationClientContract]], type[IntegrationClientContract]]:
        """Register a new integration client."""

        def decorator(cls: type[IntegrationClientContract]) -> type[IntegrationClientContract]:
            if provider in self._providers:
                raise ValueError(f"Integration client for {provider} already registered")
            self._providers[provider] = cls
            return cls

        return decorator

    def register_oauth_provider(
        self, provider: IntegrationProvider
    ) -> Callable[[type[OAuthProviderContract]], type[OAuthProviderContract]]:
        """Register a new OAuth provider."""

        def decorator(cls: type[OAuthProviderContract]) -> type[OAuthProviderContract]:
            if provider in self._providers_oauth:
                raise ValueError(f"OAuth provider for {provider} already registered")
            self._providers_oauth[provider] = cls
            return cls

        return decorator

    def resolve(
        self, provider: IntegrationProvider, is_oauth: bool = False
    ) -> type[IntegrationClientContract | OAuthProviderContract]:
        """Resolve a provider."""

        if is_oauth and provider not in self._providers_oauth:
            raise ValueError(f"OAuth provider for {provider} not registered")
        if not is_oauth and provider not in self._providers:
            raise ValueError(f"Integration client for {provider} not registered")
        if is_oauth:
            return self._providers_oauth[provider]
        return self._providers[provider]


# Singleton instance of the registry
integration_registry = IntegrationRegistry()

# Aliases for the register functions
register_provider = integration_registry.register_provider

# Aliases for the register functions
register_oauth_provider = integration_registry.register_oauth_provider
