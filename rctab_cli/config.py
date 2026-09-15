"""Configuration settings for the CLI.

Attributes:
    APP_NAME: Name of the CLI application.
"""

from functools import lru_cache
from uuid import UUID

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "RCTab-CLI"


class CLIConfig(BaseSettings):
    """CLI configuration settings class.

    Attributes:
        base_url: Base URL of the API.
        port: Port of the API.
    """

    # e.g. "https://myapp.azurewebsites.net"
    base_url: str

    # Typically 443 for https and 80 for http and 8000 for local development
    port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def base_url_full(self) -> str:
        """Create full URL from base URL and port.

        Returns:
            Full URL of the API.
        """
        return f"{self.base_url}:{self.port}/"


class AuthSettings(BaseSettings):
    """Settings class for authentication.

    Attributes:
        client_id: Client ID from Azure.
        auth_base_url: Base URL of the EU authentication endpoint.
        tenant_id: The tenant ID from Azure.
    """

    client_id: UUID
    auth_base_url: HttpUrl = "https://login.microsoftonline.com/"  # type: ignore
    tenant_id: UUID

    model_config = SettingsConfigDict(env_file=".auth.env", env_file_encoding="utf-8")

    @property
    def authority(self) -> str:
        """Make authorized URL.

        Returns:
            Authorized URL.
        """
        return str(self.auth_base_url) + str(self.tenant_id)


@lru_cache()
def get_auth_settings() -> AuthSettings:
    """Create instance of AuthSettings.

    Returns:
        Instance of AuthSettings.
    """
    return AuthSettings()


@lru_cache()
def get_cli_settings() -> CLIConfig:
    """Create instance of CLIConfig.

    Attributes:
        Instance of CLIConfig.
    """
    return CLIConfig()
