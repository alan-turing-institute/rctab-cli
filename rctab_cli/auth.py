"""Authentication helpers for the RCTab CLI."""
import atexit
import logging
from pathlib import Path

import msal
import requests
import typer

from rctab_cli.config import APP_NAME


class BearerAuth(requests.auth.AuthBase):
    """Bearer authentication class.

    Attributes:
        token: The token to use for authentication.
    """

    def __init__(self, token: str) -> None:
        """Initialize the BearerAuth class."""
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Add the bearer token to the request headers."""
        r.headers["authorization"] = "Bearer " + self.token
        return r


def write_cache(token_cache_f: Path, cache: msal.TokenCache) -> None:
    """Save the token cache to a file.

    Args:
        token_cache_f: The path to the token cache file.
        cache: The token cache.

    Returns:
        None.
    """
    if not token_cache_f.exists():
        token_cache_f.touch(mode=0o700)

    logging.info("Saving auth token to cache")
    token_cache_f.write_text(cache.serialize())


def load_cache() -> msal.TokenCache:
    """Load the token cache from a file.

    Returns:
        The token cache.
    """
    app_dir = Path(typer.get_app_dir(APP_NAME))
    token_cache_f = app_dir / "cache.bin"
    cache = msal.SerializableTokenCache()

    if token_cache_f.exists():
        cache.deserialize(token_cache_f.read_text(encoding="utf-8"))

    atexit.register(
        lambda: write_cache(token_cache_f, cache)
        # Hint: The following optional line persists only when state changed
        # if cache.has_state_changed
        # else None
    )

    return cache
