from unittest.mock import patch
from uuid import UUID

import pytest
import typer
from typer.testing import CliRunner

from rctab_cli.cli import app
from rctab_cli.sub_apps import sub
from tests.utils import ExitCodeException

runner = CliRunner()


def test_finance_create() -> None:
    """Test finance create command with all commandline options."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.BearerAuth") as mock_auth,
        patch("rctab_cli.sub_apps.sub.state") as mock_state,
        patch("requests.post") as mock_post,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
    ):
        mock_url.return_value = "fake.url"

        sub.finance_create(
            subscription_id=UUID(int=1),
            date_from="2020-01",
            date_to="2020-01",
            amount=10,
            finance_code="max",
            ticket="TICKET",
            priority=1,
        )
        mock_post.assert_called_once_with(
            "fake.url",
            json={
                "subscription_id": str(UUID(int=1)),
                "date_from": "2020-01-01",
                "date_to": "2020-01-31",
                "amount": 10,
                "finance_code": "max",
                "ticket": "TICKET",
                "priority": 1,
            },
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_called_once_with(mock_post.return_value)
        mock_echo.assert_called_once_with(mock_post.return_value.json.return_value)


def test_finance_create_defaults() -> None:
    """Test finance create command with minimal commandline options."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.BearerAuth") as mock_auth,
        patch("rctab_cli.sub_apps.sub.state") as mock_state,
        patch("requests.post") as mock_post,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
    ):
        mock_url.return_value = "fake.url"

        # More complicated invocation needed to test default params.
        result = runner.invoke(
            app,
            [
                "sub",
                "finance",
                "create",
                "--subscription-id",
                str(UUID(int=1)),
                "--date-from",
                "2020-01",
                "--date-to",
                "2020-01",
                "--amount",
                "10",
                "--finance-code",
                "max",
                "--ticket",
                "TICKET",
                "--priority",
                "1",
            ],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_post.assert_called_once_with(
            "fake.url",
            json={
                "subscription_id": str(UUID(int=1)),
                "date_from": "2020-01-01",
                "date_to": "2020-01-31",
                "amount": 10.0,
                "finance_code": "max",
                "ticket": "TICKET",
                "priority": 1,
            },
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_called_once_with(mock_post.return_value)
        mock_echo.assert_called_once_with(mock_post.return_value.json.return_value)


def test_finance_create_raises() -> None:
    with patch("requests.get"):
        with pytest.raises(typer.Abort):
            # This will error as the date should be in YYYY-MM format
            # without a day
            sub.finance_create(
                UUID(int=0),
                date_from="2001-01-01",
            )
        with pytest.raises(typer.Abort):
            # This will error as the date should be in YYYY-MM format
            # without a day
            sub.finance_create(
                UUID(int=0),
                date_from="2001-01",
                date_to="2001-01-01",
            )


def test_finance_get() -> None:
    """Test finance get command."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.BearerAuth") as mock_auth,
        patch("rctab_cli.sub_apps.sub.state") as mock_state,
        patch("requests.get") as mock_get,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
    ):
        mock_url.return_value = "fake.url"

        # More complicated invocation needed to test default params.
        result = runner.invoke(
            app,
            ["sub", "finance", "get", "--finance-id", "1"],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_get.assert_called_once_with(
            "fake.url/1",
            json={"finance_id": 1},
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_called_once_with(mock_get.return_value)
        mock_echo.assert_called_once_with(mock_get.return_value.json.return_value)


def test_finance_update() -> None:
    """Test finance update command with all commandline options."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.BearerAuth") as mock_auth,
        patch("rctab_cli.sub_apps.sub.state") as mock_state,
        patch("requests.put") as mock_put,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
        patch("rctab_cli.sub_apps.sub.get_finance") as mock_get_finance,
    ):
        mock_get_finance.return_value = {
            "finance_id": 1,
            "subscription_id": str(UUID(int=1)),
        }
        mock_url.return_value = "fake.url"

        sub.finance_update(
            finance_id=1,
            subscription_id=UUID(int=1),
            date_from="2020-01",
            date_to="2020-01",
            amount=10,
            finance_code="max",
            ticket="TICKET",
            priority=1,
        )
        mock_put.assert_called_once_with(
            "fake.url/1",
            json={
                "finance_id": 1,
                "subscription_id": str(UUID(int=1)),
                "date_from": "2020-01-01",
                "date_to": "2020-01-31",
                "amount": 10,
                "finance_code": "max",
                "ticket": "TICKET",
                "priority": 1,
            },
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_called_once_with(mock_put.return_value)
        mock_echo.assert_called_once_with(mock_put.return_value.json.return_value)


def test_finance_does_not_update() -> None:
    """Test finance update command only updates when necessary."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("requests.put") as mock_put,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
        patch("rctab_cli.sub_apps.sub.get_finance") as mock_get_finance,
    ):
        mock_get_finance.return_value = {
            "finance_id": 1,
            "subscription_id": str(UUID(int=2)),
            "date_from": "2020-01-01",
            "date_to": "2020-01-31",
            "amount": 10,
            "finance_code": "max",
            "ticket": "TICKET",
            "priority": 1,
        }
        mock_url.return_value = "fake.url"

        sub.finance_update(
            finance_id=1,
            subscription_id=UUID(int=2),
            date_from="2020-01",
            date_to="2020-01",
            amount=10,
            finance_code="max",
            ticket="TICKET",
            priority=1,
        )
        mock_put.assert_not_called()
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_not_called()
        mock_echo.assert_called_once_with(
            "Finance records identical. Taking no action."
        )


def test_finance_update_defaults() -> None:
    """Test finance update command with minimal commandline options."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("requests.put") as mock_put,
        patch("rctab_cli.sub_apps.sub.get_finance") as mock_get_finance,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
    ):
        mock_url.return_value = "fake.url"
        mock_get_finance.return_value = {
            "finance_id": 1,
            "subscription_id": str(UUID(int=2)),
            "date_from": "2001-01-01",
            "date_to": "2001-01-31",
            "amount": 5.0,
            "finance_code": "test-code",
            "ticket": "test-ticket",
            "priority": 101,
        }

        # More complicated invocation needed to test default params.
        result = runner.invoke(
            app,
            [
                "sub",
                "finance",
                "update",
                "--finance-id",
                "1",
                "--subscription-id",
                str(UUID(int=2)),
            ],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_put.assert_not_called()
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_not_called()
        mock_echo.assert_called_once_with(
            "Finance records identical. Taking no action."
        )


def test_finance_update_raises() -> None:
    """Test finance_update raises if the subscription IDs don't match."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.get_finance") as mock_get_finance,
    ):
        mock_url.return_value = "fake.url"
        mock_get_finance.return_value = {
            "finance_id": 1,
            "subscription_id": str(UUID(int=2)),
            "date_from": "2001-02-01",
            "date_to": "2001-03-31",
            "amount": 5.0,
            "finance_code": "test-code",
            "ticket": "test-ticket",
            "priority": 101,
        }

        # Function should double-check that the finance is for the right subscription
        with pytest.raises(sub.SubscriptionIdMismatch):
            sub.finance_update(finance_id=1, subscription_id=UUID(int=3))

        # Function should raise an Abort if date_from is badly formatted
        with pytest.raises(typer.Abort):
            sub.finance_update(
                finance_id=1, subscription_id=UUID(int=2), date_from="2020-01-02"
            )

        # Function should raise an Abort if date_to is badly formatted
        with pytest.raises(typer.Abort):
            sub.finance_update(
                finance_id=1,
                subscription_id=UUID(int=2),
                date_from="2020-01",
                date_to="2020-01-02",
            )


def test_finance_list() -> None:
    """Test finance list command."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.BearerAuth") as mock_auth,
        patch("rctab_cli.sub_apps.sub.state") as mock_state,
        patch("requests.get") as mock_get,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
    ):
        mock_url.return_value = "fake.url"

        # More complicated invocation needed to test default params.
        result = runner.invoke(
            app,
            [
                "sub",
                "finance",
                "list",
                "--subscription-id",
                "00000000-0000-0000-0000-00000000035a",
            ],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_get.assert_called_once_with(
            "fake.url",
            json={"sub_id": "00000000-0000-0000-0000-00000000035a"},
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/finance")
        mock_raise_for_status.assert_called_once_with(mock_get.return_value)
        mock_echo.assert_called_once_with(mock_get.return_value.json.return_value)


def test_finance_delete() -> None:
    """Test finance delete command."""

    with (
        patch("rctab_cli.sub_apps.sub.create_url") as mock_url,
        patch("rctab_cli.sub_apps.sub.BearerAuth") as mock_auth,
        patch("rctab_cli.sub_apps.sub.state") as mock_state,
        patch("requests.delete") as mock_delete,
        patch("rctab_cli.sub_apps.sub.raise_for_status") as mock_raise_for_status,
        patch("typer.echo") as mock_echo,
    ):
        mock_url.return_value = "fake.url"

        # More complicated invocation needed to test default params.
        result = runner.invoke(
            app,
            [
                "sub",
                "finance",
                "delete",
                "--subscription-id",
                "00000000-0000-0000-0000-00000000035a",
                "--finance-id",
                "1",
            ],
        )

        if result.exit_code != 0:
            raise ExitCodeException(result)

        mock_delete.assert_called_once_with(
            "fake.url/1",
            json={"sub_id": "00000000-0000-0000-0000-00000000035a"},
            auth=mock_auth.return_value,
        )
        mock_auth.assert_called_once_with(mock_state.get_access_token.return_value)
        mock_url.assert_called_once_with("accounting/finances")
        mock_raise_for_status.assert_called_once_with(mock_delete.return_value)
        mock_echo.assert_called_once_with(mock_delete.return_value.json.return_value)
