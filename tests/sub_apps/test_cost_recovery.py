from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from rctab_cli import cli
from rctab_cli.sub_apps import sub

runner = CliRunner()


def test_cost_recovery() -> None:
    """Test cost-recovery command with all commandline options."""

    with patch("rctab_cli.sub_apps.sub.create_url") as mock_url, patch(
        "rctab_cli.sub_apps.sub.BearerAuth"
    ) as mock_auth, patch("rctab_cli.sub_apps.sub.state") as mock_state, patch(
        "requests.post"
    ) as mock_post, patch(
        "rctab_cli.sub_apps.sub.raise_for_status"
    ) as mock_raise_for_status, patch(
        "typer.echo"
    ) as mock_echo:
        mock_url.return_value = "fake.url"

        sub.cost_recovery(month="2020-01", for_real=True)

        mock_post.assert_called_once_with(
            "fake.url",
            json={
                "first_day": "2020-01-01",
            },
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/cli-cost-recovery")
        mock_raise_for_status.assert_called_once_with(mock_post.return_value)
        mock_echo.assert_called_once_with(mock_post.return_value.json.return_value)


def test_cost_recovery_defaults() -> None:
    """Test finance command with minimal commandline options."""

    with patch("rctab_cli.sub_apps.sub.create_url") as mock_url, patch(
        "rctab_cli.sub_apps.sub.BearerAuth"
    ) as mock_auth, patch("rctab_cli.sub_apps.sub.state") as mock_state, patch(
        "requests.get"
    ) as mock_get, patch(
        "rctab_cli.sub_apps.sub.raise_for_status"
    ) as mock_raise_for_status, patch(
        "typer.echo"
    ) as mock_echo:
        mock_url.return_value = "fake.url"

        # We can use the --dry-run option...
        result = runner.invoke(
            cli.app,
            ["sub", "cost-recovery", "--month", "2020-01", "--dry-run"],
        )
        if result.exit_code != 0:
            raise ValueError(result.output)

        # ...or no extra option, which should behave the same way
        result = runner.invoke(
            cli.app,
            [
                "sub",
                "cost-recovery",
                "--month",
                "2020-01",
            ],
        )

        if result.exit_code != 0:
            raise ValueError(result.output)

        mock_get.assert_called_with(
            "fake.url",
            json={
                "first_day": "2020-01-01",
            },
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_with("accounting/cli-cost-recovery")
        mock_raise_for_status.assert_called_with(mock_get.return_value)
        mock_echo.assert_called_with(mock_get.return_value.json.return_value)


def test_cost_recovery_raises() -> None:
    """Test cost-recovery command raises correct errors."""

    # Patch this only so that we can't accidentally contact the real server
    with patch("rctab_cli.sub_apps.sub.create_url"):
        with pytest.raises(typer.Abort):
            sub.cost_recovery(
                # This will error as the date should be in YYYY-MM format
                # without a day
                month="2001-01-01",
            )
