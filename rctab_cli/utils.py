from pathlib import Path

import typer

from rctab_cli.state import state

from .config import get_cli_settings
from .types import RCTabURL


def create_url(path: str) -> str:
    """Create and validate a url endpoint.

    Args:
        path: The endpoint path to the create.

    Returns:
        The url endpoint.
    """

    temp = str(RCTabURL(url=get_cli_settings().base_url_full + path).url)
    if state.verbose:
        typer.echo(temp)
    return temp


def file_exists_exception(file: Path) -> None:
    """Log an error if file doesn't exist.

    Args:
        file: The file to check.

    Raises:
        typer.Abort: If the file doesn't exist.

    Returns:
        None

    """
    if not file.exists():
        config_f = typer.style(str(file), fg=typer.colors.RED, bold=True)
        typer.echo(f"File {config_f} does not exist")
        raise typer.Abort()
