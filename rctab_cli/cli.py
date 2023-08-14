"""Insert usage data via the API asynchronously.

Attributes:
    app: Typer object for the CLI.
"""

import logging
import os

try:
    from importlib import metadata  # type: ignore
except ImportError:  # for Python<3.8
    import importlib_metadata as metadata  # type: ignore
from pathlib import Path
from typing import Dict, Union

import msal
import requests
import typer

from rctab_cli.auth import BearerAuth, load_cache
from rctab_cli.config import APP_NAME, get_auth_settings
from rctab_cli.state import state
from rctab_cli.sub_apps import subscription_app
from rctab_cli.utils import create_url

app = typer.Typer()

app.add_typer(subscription_app, name="sub", help="Manage Azure subscriptions")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


def acquire_access_token() -> Dict:
    """Get an access token from Azure.

    Returns:
        Access token.
    """
    app_dir = Path(typer.get_app_dir(APP_NAME))
    app_dir.mkdir(0o700, exist_ok=True)

    auth = get_auth_settings()
    cache = load_cache()
    msal_app = msal.PublicClientApplication(
        str(auth.client_id), authority=auth.authority, token_cache=cache
    )

    # The pattern to acquire a token looks like this.
    result = None

    # pylint: disable=W0511
    # Firstly, check the cache to see if this end user has signed in before
    accounts = msal_app.get_accounts()
    if accounts:
        logging.info("Account(s) exists in cache, probably with token too. Let's try.")
        user = accounts[0]
        result = msal_app.acquire_token_silent(
            scopes=[f"api://{str(auth.client_id)}/admin"], account=user
        )

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        result = msal_app.acquire_token_interactive(
            scopes=[f"api://{str(auth.client_id)}/admin"],
        )

    return result


def version_callback(value: bool) -> None:
    """Show the current CLI and API version.

    Args:
        value: Whether to display the version.

    Returns:
        None.
    """
    if value:
        cli_version = metadata.version(__package__)
        api_version = get_api_version()
        version_str = f"RCTab CLI version {cli_version}"
        if api_version:
            version_str += f", API version {api_version}"
        typer.secho(version_str, fg=typer.colors.GREEN)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # pylint: disable=unused-argument
        False,
        callback=version_callback,
        help="Display RCTab CLI version and API version.",
    )
) -> None:
    """
    The RCTab CLI.

    What it does do:

    \b
      - Add subscriptions to the Research Compute Billing System.
      - Approve credits for a subscription.
      - Allocate approved credits to a subscription.
      - Check all the approvals and allocations made for a subscription.
      - Get a summary of all the approvals, allocations and costs for all subscriptions.

    What it doesn't do:

    \b
      - Create subscriptions on Azure.
      - Add users to a subscription.

    Further information:

    \b
      - RCTab API : https://github.com/alan-turing-institute/rctab-api
      - RCTab CLI : https://github.com/alan-turing-institute/rctab-cli
    """
    state.access_token = acquire_access_token


@app.command()
def logout() -> None:
    """Clear the app cache and all login info.

    Returns:
        None.
    """
    app_dir = Path(typer.get_app_dir(APP_NAME))

    cache_dir = app_dir / "cache.bin"

    if cache_dir.exists():
        cache_dir.unlink()

    if app_dir.exists():
        app_dir.rmdir()


@app.command()
def request_access() -> None:
    """Request access to the RCTab API - required.

    Raises:
        typer.Abort: If the API request fails.

    Returns:
        None.
    """
    path = "admin/request-access"
    endpoint = create_url(path)
    resp = requests.post(endpoint, auth=BearerAuth(state.get_access_token()))

    if resp.status_code != 200:
        typer.echo(
            f"Failed with status code: {resp.status_code}. Detail: {resp.json()}"
        )
        raise typer.Abort("API request failed")

    typer.secho("Admin request submitted", fg=typer.colors.GREEN)
    typer.echo(resp.json())


@app.command()
def token() -> None:
    """Return an access token and display it.

    Returns:
        None.
    """
    typer.echo(state.get_access_token(), nl=False)


def get_api_version() -> Union[str, None]:
    """Get the RCTab CLI version.

    Returns:
        The RCTab CLI version if the request is successful, else None.
    """
    path = "version"
    endpoint = create_url(path)
    state.access_token = acquire_access_token
    resp = requests.get(endpoint, auth=BearerAuth(state.get_access_token()))
    if resp.status_code != 200:
        return None
    return resp.json()["detail"]


if __name__ == "__main__":
    app()
