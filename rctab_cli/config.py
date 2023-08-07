from functools import lru_cache
from uuid import UUID

from pydantic import BaseSettings, HttpUrl

APP_NAME = "RCTab-CLI"


class CLIConfig(BaseSettings):

    # e.g. "https://myapp.azurewebsites.net"
    base_url: str

    # Typically 443 for https and 80 for http and 8000 for local development
    port: int

    @property
    def base_url_full(self) -> str:
        return f"{self.base_url}:{self.port}/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AuthSettings(BaseSettings):
    """Settings class"""

    client_id: UUID
    auth_base_url: HttpUrl = "https://login.microsoftonline.com/"  # type: ignore
    tenant_id: UUID

    @property
    def authority(self) -> str:
        """Makes authorized URL"""
        return self.auth_base_url + str(self.tenant_id)

    class Config:
        env_file = ".auth.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_auth_settings() -> AuthSettings:

    return AuthSettings()


@lru_cache()
def get_cli_settings() -> CLIConfig:

    return CLIConfig()
