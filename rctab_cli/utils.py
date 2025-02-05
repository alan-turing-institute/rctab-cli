"""Utility functions for the CLI."""

import typer
from pydantic import AnyHttpUrl
from pydantic.tools import parse_obj_as

from rctab_cli.config import get_cli_settings
from rctab_cli.state import state
from rctab_cli.types import RCTabURL


def create_url(path: str) -> str:
    """Create and validate a URL endpoint.

    Args:
        path: The path part of the URL.

    Returns:
        The URL of some resource on an RCTab API.
    """
    temp = str(
        RCTabURL(
            url=parse_obj_as(AnyHttpUrl, get_cli_settings().base_url_full + path)
        ).url
    )
    if state.verbose:
        typer.echo(temp)
    return temp
