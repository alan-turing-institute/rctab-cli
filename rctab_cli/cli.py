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

from datetime import datetime
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
        check_cli_version(cli_version)
        check_api_version(api_version)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # pylint: disable=unused-argument
        False,
        callback=version_callback,
        help="Display RCTab CLI version and API version.",
    )
) -> None:
    """Perform RCTab administrative duties.

    With this CLI you can add subscriptions to RCTab, approve credits,
    allocate approved credits, and check the status of all the above.

    The CLI cannot be used to create subscriptions on Azure. For that,
    see the Azure CLI.

    See also https://github.com/alan-turing-institute/rctab
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


def check_api_version(api_version: Union[str, None]) -> None:
    """Check the RCTab API version on Azure uses the latest Docker Hub image.

    A list of docker image tags is retrieved from Docker Hub along with the time
    when they were pushed. The latest image tag is then compared to the API version.

    Args:
        api_version: The RCTab API version on Azure.
    """
    url = "https://hub.docker.com/v2/repositories/turingrc/rctab-api/tags"
    response = requests.get(url)
    if api_version and response.status_code == 200 and response.json() != []:
        tag_names = {
            datetime.strptime(tag["tag_last_pushed"], "%Y-%m-%dT%H:%M:%S.%fZ"): tag[
                "name"
            ]
            for tag in response.json()["results"]
            if "release" not in tag["name"]
        }
        latest_tag = tag_names[max(tag_names.keys())]
        if latest_tag != api_version:
            typer.secho(
                "You are using an old version of the RCTab API."
                f"The latest version is {latest_tag}. Restart the webapp in the "
                "Azure portal to update to the latest version.",
                fg=typer.colors.YELLOW,
            )


def check_cli_version(cli_version: str) -> None:
    """Check if the RCTab CLI version matches the latest release on GitHub.

    A list of release tags is retrieved from the GitHub API along with the time
    when it was published. The latest tag is then compared to the CLI version.

    Args:
        cli_version: The RCTab CLI package version.
    """
    url = "https://api.github.com/repos/alan-turing-institute/rctab-cli/releases"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json() != []:
        tags = {
            datetime.strptime(tag["published_at"], "%Y-%m-%dT%H:%M:%SZ"): tag[
                "tag_name"
            ]
            for tag in response.json()
        }
        latest_tag = tags[max(tags.keys())]
        if latest_tag != cli_version:
            typer.secho(
                "You are using an old version of the RCTab CLI. The latest "
                f"version is {latest_tag}. Pull the latest version from GitHub "
                "(https:://github.com/alan-turing-institute/rctab-cli)",
                fg=typer.colors.YELLOW,
            )


if __name__ == "__main__":
    app()
