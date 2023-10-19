from datetime import date
from unittest.mock import patch
from uuid import UUID

from typer.testing import CliRunner

from rctab_cli import cli
from rctab_cli.sub_apps import sub
from tests.utils import ExitCodeException

runner = CliRunner()


def test_add() -> None:
    """Test add command with all commandline options."""

    with patch("rctab_cli.sub_apps.sub.add_subscription") as mock_sub, patch(
        "rctab_cli.sub_apps.sub.set_the_persistence"
    ) as mock_persist, patch("rctab_cli.sub_apps.sub.create_approval") as mock_approve:
        sub.add(
            subscription_id=UUID(int=1),
            persistent=True,
            ticket="TICKET",
            amount=10,
            allocate=True,
            date_from="2020-01-01",
            date_to="2020-02-01",
            skip_check=True,
        )

        mock_sub.assert_called_once_with(UUID(int=1))

        mock_persist.assert_called_once_with(UUID(int=1), always_on=True)

        mock_approve.assert_called_once_with(
            UUID(int=1),
            "TICKET",
            10,
            True,
            "2020-01-01",
            "2020-02-01",
        )


def test_add_defaults() -> None:
    """Test add command with minimal commandline options."""

    with patch("rctab_cli.sub_apps.sub.add_subscription") as mock_sub, patch(
        "rctab_cli.sub_apps.sub.set_the_persistence"
    ) as mock_persist, patch("rctab_cli.sub_apps.sub.create_approval") as mock_approve:
        # More complicated invocation needed to test default params.
        result = runner.invoke(
            cli.app,
            [
                "sub",
                "add",
                "--subscription-id",
                str(UUID(int=1)),
                "--date-to",
                "2020-02-01",
                "--amount",
                "10",
                "--ticket",
                "TICKET",
                "--allocate",
                "-y",  # required for non-interactive mode
            ],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_sub.assert_called_once_with(UUID(int=1))

        mock_persist.assert_called_once_with(UUID(int=1), always_on=False)

        mock_approve.assert_called_once_with(
            UUID(int=1),
            "TICKET",
            10.0,
            True,
            date.today().isoformat(),
            "2020-02-01",
        )


def test_approve() -> None:
    """Test approve command with all commandline options."""

    with patch("rctab_cli.sub_apps.sub.create_approval") as mock_approve:
        sub.approve(
            subscription_id=UUID(int=1),
            ticket="TICKET",
            amount=10,
            allocate=True,
            date_from="2020-01-01",
            date_to="2020-02-01",
            force=True,
        )

        mock_approve.assert_called_once_with(
            UUID(int=1), "TICKET", 10, True, "2020-01-01", "2020-02-01", True
        )


def test_approve_defaults() -> None:
    """Test approve command with minimal commandline options."""

    with patch("rctab_cli.sub_apps.sub.create_approval") as mock_approve:
        # More complicated invocation needed to test default params.
        result = runner.invoke(
            cli.app,
            [
                "sub",
                "approve",
                "--subscription-id",
                str(UUID(int=1)),
                "--date-to",
                "2020-02-01",
                "--amount",
                "10",
                "--ticket",
                "TICKET",
            ],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_approve.assert_called_once_with(
            UUID(int=1),
            "TICKET",
            10.0,
            False,
            date.today().isoformat(),
            "2020-02-01",
            False,
        )
