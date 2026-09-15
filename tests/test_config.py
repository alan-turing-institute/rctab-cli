"""Regression tests for package import and settings instantiation."""

import importlib

import pytest


def test_import_rctab_cli() -> None:
    """Importing the package should not raise, even at pydantic import time."""
    module = importlib.import_module("rctab_cli")
    assert hasattr(module, "app")


def test_cli_config_instantiates(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLIConfig should build from environment variables."""
    from rctab_cli.config import CLIConfig

    monkeypatch.setenv("BASE_URL", "https://my-rctab.azurewebsites.net")
    monkeypatch.setenv("PORT", "443")

    settings = CLIConfig()

    assert settings.base_url == "https://my-rctab.azurewebsites.net"
    assert settings.port == 443
    assert settings.base_url_full == "https://my-rctab.azurewebsites.net:443/"


def test_auth_settings_instantiates(monkeypatch: pytest.MonkeyPatch) -> None:
    """AuthSettings should build from environment variables."""
    from rctab_cli.config import AuthSettings

    monkeypatch.setenv("CLIENT_ID", "00000000-0000-0000-0000-000000000009")
    monkeypatch.setenv("TENANT_ID", "00000000-0000-0000-0000-00000000000a")

    settings = AuthSettings()

    assert str(settings.client_id) == "00000000-0000-0000-0000-000000000009"
    assert (
        settings.authority
        == "https://login.microsoftonline.com/00000000-0000-0000-0000-00000000000a"
    )
