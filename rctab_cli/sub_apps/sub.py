"""Subscription management commands.

Attributes:
    subscription_app: Typer object for the subscription CLI.
    finance_app: Typer object for the finance CLI.
"""

# pylint: disable=too-many-arguments, redefined-outer-name
import calendar
import json
from datetime import date
from json.decoder import JSONDecodeError
from typing import Dict, Optional, Union
from uuid import UUID

import requests
import typer

from rctab_cli.auth import BearerAuth
from rctab_cli.state import state
from rctab_cli.utils import create_url

subscription_app = typer.Typer(no_args_is_help=True)
finance_app = typer.Typer(no_args_is_help=True)
subscription_app.add_typer(
    finance_app, name="finance", help="Manage subscription finance"
)


def raise_for_status(resp: requests.Response) -> None:
    """Check the status code of a response.

    Args:
        resp: The response to check.

    Raises:
        typer.Abort: If the response status code is not in the 200s.

    Returns:
        None.
    """
    if 200 <= resp.status_code <= 299:
        return

    try:
        try:
            detail = resp.json()
        except JSONDecodeError:
            detail = resp.content

        typer.secho(
            f"\nFailed with status code: {resp.status_code}. Details: {detail}",
            fg=typer.colors.RED,
        )
        raise typer.Abort()

    except JSONDecodeError:
        typer.echo(
            f"\nFailed with status code: {resp.status_code}. Contact the development team"
        )
        raise typer.Abort()


def add_subscription(subscription_id: UUID) -> None:
    """Add a subscription to the billing system.

    Args:
        subscription_id: The ID of the subscription to add.

    Returns:
        None.
    """
    path = "accounting/subscription"
    endpoint = create_url(path)

    resp = requests.post(
        endpoint,
        json={"sub_id": str(subscription_id)},
        auth=BearerAuth(state.get_access_token()),
    )

    if resp.status_code == 409:
        typer.echo(resp.json())
        return

    raise_for_status(resp)
    typer.echo(resp.json())


def set_the_persistence(subscription_id: UUID, always_on: bool = False) -> None:
    """Set the persistence of a subscription.

    Args:
        subscription_id: The ID of the subscription to set the persistence of.
        always_on: Whether the subscription should be always on.

    Returns:
        None.
    """
    path = "accounting/persistent"
    endpoint = create_url(path)

    resp = requests.post(
        endpoint,
        json={"sub_id": str(subscription_id), "always_on": always_on},
        auth=BearerAuth(state.get_access_token()),
    )

    raise_for_status(resp)
    typer.echo(resp.json())


def create_approval(
    subscription_id: UUID,
    ticket: str,
    amount: float,
    allocate: bool,
    date_from: str,
    date_to: str,
    force: bool = False,
) -> None:
    """Create an approval for a subscription.

    Args:
        subscription_id: The ID of the subscription to approve.
        ticket: The ticket reference of the request made.
        amount: The amount to approve.
        allocate: Whether to allocate the approved amount to the subscription.
        date_from: The date the approval is valid from.
        date_to: The date the approval is valid to.
        force: Whether to allow the date_from to be > 30 days ago.

    Returns:
        None.
    """
    path = "accounting/approve"
    endpoint = create_url(path)

    resp = requests.post(
        endpoint,
        json={
            "sub_id": str(subscription_id),
            "ticket": ticket,
            "amount": amount,
            "allocate": allocate,
            "date_from": date_from,
            "date_to": date_to,
            "force": force,
        },
        auth=BearerAuth(state.get_access_token()),
    )

    raise_for_status(resp)
    typer.echo(resp.json())


def create_allocation(
    subscription_id: UUID,
    ticket: str,
    amount: float,
) -> None:
    """Create an allocation for a subscription.

    Args:
        subscription_id: The ID of the subscription to allocate.
        ticket: The ticket reference of the request made.
        amount: The amount to allocate.

    Returns:
        None.
    """
    path = "accounting/topup"
    endpoint = create_url(path)

    resp = requests.post(
        endpoint,
        json={
            "sub_id": str(subscription_id),
            "ticket": ticket,
            "amount": amount,
        },
        auth=BearerAuth(state.get_access_token()),
    )

    raise_for_status(resp)
    typer.echo(resp.json())


@subscription_app.command()
def add(
    subscription_id: UUID = typer.Option(
        ..., help="Subscription id", prompt="Subscription id"
    ),
    persistent: bool = typer.Option(
        False, "--persistant", help="Set subscription to have no budget cap"
    ),
    ticket: str = typer.Option(
        ..., help="Helpdesk ticket reference", prompt="Helpdesk ticket reference"
    ),
    amount: float = typer.Option(
        ..., help="Amount to approve", prompt="How much to approve"
    ),
    allocate: bool = typer.Option(
        ...,
        help="Allocate the approved amount to the subscription",
        prompt="Allocate the full amount",
    ),
    date_from: str = typer.Option(
        date.today().isoformat(),
        help="ISO Date approved amount is valid from in ISO",
    ),
    date_to: str = typer.Option(
        ...,
        help="ISO Date approved amount is valid to (exclusive)",
        prompt="Allocation valid to (ISO date)",
    ),
    skip_check: bool = typer.Option(False, "-y", help="Dont ask for confirmation"),
) -> None:
    """Add an existing subscription to the billing system and add funds."""
    if not skip_check:
        query = typer.style("Summary:\n", fg=typer.colors.RED)
        info = (
            f"Subscription ID: {subscription_id}\n"
            f"Ticket: {ticket}\n"
            f"Amount: {amount}\n"
            f"Allocate: {allocate}\n"
            f"Date from: {date_from}\n"
            f"Date to: {date_to}\n"
            f"Persistent: {persistent}\n"
        )

        confirm = typer.confirm(query + info)

        if not confirm:
            raise typer.Abort()

    # Enter subscription_id into database
    add_subscription(subscription_id)

    # Set persistence
    set_the_persistence(subscription_id, always_on=persistent)

    # Approve funds
    create_approval(subscription_id, ticket, amount, allocate, date_from, date_to)


@subscription_app.command()
def set_persistence(
    subscription_id: UUID = typer.Option(..., help="Subscription id"),
    persistent: bool = typer.Option(..., help="Change subscription persistence"),
) -> None:
    """Change the persistence of a subscription."""
    set_the_persistence(subscription_id, always_on=persistent)


@subscription_app.command()
def approve(
    subscription_id: UUID = typer.Option(..., help="Subscription id"),
    ticket: str = typer.Option(..., help="Helpdesk ticket reference"),
    amount: float = typer.Option(..., help="Amount to approve"),
    allocate: bool = typer.Option(
        False, help="Allocate the approved amount to the subscription"
    ),
    date_from: str = typer.Option(
        date.today().isoformat(),
        help="ISO Date approved amount is valid from in ISO",
    ),
    date_to: str = typer.Option(
        ..., help="ISO Date approved amount is valid to (exclusive)"
    ),
    force: bool = typer.Option(
        False, "--force", help="Allow date-from to be > 30 days ago"
    ),
) -> None:
    """Approve credits for a subscription."""
    create_approval(
        subscription_id, ticket, amount, allocate, date_from, date_to, force
    )


@subscription_app.command()
def allocate(
    subscription_id: UUID = typer.Option(..., help="Subscription id"),
    ticket: str = typer.Option(..., help="Helpdesk ticket reference"),
    amount: float = typer.Option(..., help="Amount to allocate"),
) -> None:
    """Allocate credits a subscription.

    Funds must already be approved.
    """
    create_allocation(subscription_id, ticket, amount)


@subscription_app.command()
def approvals(
    subscription_id: UUID = typer.Option(..., help="Subscription id")
) -> None:
    """List all approvals for a subscription."""
    path = "accounting/approvals"
    endpoint = create_url(path)

    resp = requests.get(
        endpoint,
        json={"sub_id": str(subscription_id)},
        auth=BearerAuth(state.get_access_token()),
    )

    raise_for_status(resp)
    typer.echo(json.dumps(resp.json(), indent=4, sort_keys=True))


@subscription_app.command()
def allocations(
    subscription_id: UUID = typer.Option(..., help="Subscription id")
) -> None:
    """List all allocations for a subscription."""
    path = "accounting/allocations"
    endpoint = create_url(path)

    resp = requests.get(
        endpoint,
        json={"sub_id": str(subscription_id)},
        auth=BearerAuth(state.get_access_token()),
    )

    raise_for_status(resp)
    typer.echo(json.dumps(resp.json(), indent=4, sort_keys=True))


@subscription_app.command()
def summary(
    subscription_id: Optional[UUID] = typer.Option(None, help="Subscription id"),
    show_rbac: bool = typer.Option(
        False, "--show-rbac", help="Include the role assignments"
    ),
) -> None:
    """Get a summary of approvals, allocations and costs for one or all subscriptions."""
    path = "accounting/subscription"
    endpoint = create_url(path)

    params = {}

    if subscription_id:
        params["sub_id"] = str(subscription_id)

    resp = requests.get(
        endpoint,
        params=params,
        auth=BearerAuth(state.get_access_token()),
    )

    raise_for_status(resp)

    summaries = resp.json()
    if not show_rbac:
        for item in summaries:
            item.pop("role_assignments")

    typer.echo(json.dumps(summaries, indent=4, sort_keys=True))


@finance_app.command("create")
def finance_create(
    subscription_id: UUID = typer.Option(..., help="Subscription ID"),
    date_from: str = typer.Option(..., help="Start date, in YYYY-MM format"),
    date_to: str = typer.Option(..., help="End date, in YYYY-MM format"),
    amount: float = typer.Option(..., help="Amount to finance"),
    finance_code: str = typer.Option(..., help="Finance code for cost recovery"),
    ticket: str = typer.Option(..., help="Helpdesk ticket reference"),
    priority: int = typer.Option(100, help="Lower number is higher priority"),
) -> None:
    """Create a finance record for a subscription."""
    try:
        # The first day of the month
        date_from_date = date.fromisoformat(date_from + "-01")

        date_to_date = date.fromisoformat(date_to + "-01")
    except ValueError:
        typer.secho(
            "Month must be in YYYY-MM format",
            fg=typer.colors.RED,
        )
        raise typer.Abort()

    # The last day of the month
    month_range = calendar.monthrange(date_to_date.year, date_to_date.month)
    date_to_date = date(date_to_date.year, date_to_date.month, month_range[1])

    endpoint = create_url("accounting/finances")
    resp = requests.post(
        endpoint,
        json={
            "subscription_id": str(subscription_id),
            "date_from": date_from_date.isoformat(),
            "date_to": date_to_date.isoformat(),
            "amount": amount,
            "finance_code": finance_code,
            "ticket": ticket,
            "priority": priority,
        },
        auth=BearerAuth(state.get_access_token()),
    )
    raise_for_status(resp)
    typer.echo(resp.json())


def get_finance(
    finance_id: int,
) -> Dict[str, Union[float, str]]:
    """Retrieve a finance record from the server.

    Not to be confused with finance_get, for the finance-get command.
    """
    endpoint = create_url("accounting/finances")

    resp = requests.get(
        endpoint + f"/{finance_id}",
        json={
            "finance_id": finance_id,
        },
        auth=BearerAuth(state.get_access_token()),
    )
    raise_for_status(resp)
    return resp.json()


@finance_app.command("get")
def finance_get(
    finance_id: int = typer.Option(..., help="Finance ID"),
) -> None:
    """Get a finance row from the database."""
    result = get_finance(finance_id)
    typer.echo(result)


class SubscriptionIdMismatch(Exception):
    """When the Subscription ID and Finance ID don't match."""


@finance_app.command("update")
def finance_update(
    finance_id: int = typer.Option(..., help="Finance ID"),
    subscription_id: UUID = typer.Option(..., help="Subscription ID"),
    date_from: str = typer.Option(None, help="Start date, in YYYY-MM format"),
    date_to: str = typer.Option(None, help="End date, in YYYY-MM format"),
    amount: float = typer.Option(None, help="Amount to finance"),
    finance_code: str = typer.Option(None, help="Finance code for cost recovery"),
    ticket: str = typer.Option(None, help="Helpdesk ticket reference"),
    priority: int = typer.Option(None, help="Lower number is higher priority"),
) -> None:
    """Update a finance record for a subscription."""
    endpoint = create_url("accounting/finances")

    # Get the finance object as it currently is in case we have only
    # been given some optional arguments
    old_finance = get_finance(finance_id)
    new_finance = old_finance.copy()

    if str(subscription_id) != old_finance["subscription_id"]:
        raise SubscriptionIdMismatch

    if date_from:
        try:
            # The first day of the month
            date_from_date = date.fromisoformat(date_from + "-01")

        except ValueError:
            typer.secho(
                "Month must be in YYYY-MM format",
                fg=typer.colors.RED,
            )
            raise typer.Abort()
        new_finance["date_from"] = date_from_date.isoformat()

    if date_to:
        try:
            # The last day of the month
            date_to_date = date.fromisoformat(date_to + "-01")
        except ValueError:
            typer.secho(
                "Month must be in YYYY-MM format",
                fg=typer.colors.RED,
            )
            raise typer.Abort()
        month_range = calendar.monthrange(date_to_date.year, date_to_date.month)
        date_to_date = date(date_to_date.year, date_to_date.month, month_range[1])
        new_finance["date_to"] = date_to_date.isoformat()

    new_finance["amount"] = amount if amount is not None else old_finance["amount"]
    new_finance["finance_code"] = (
        finance_code if finance_code else old_finance["finance_code"]
    )
    new_finance["ticket"] = ticket if ticket else old_finance["ticket"]
    new_finance["priority"] = (
        priority if priority is not None else old_finance["priority"]
    )

    if new_finance == old_finance:
        typer.echo("Finance records identical. Taking no action.")
        return

    resp = requests.put(
        endpoint + f"/{finance_id}",
        json=new_finance,
        auth=BearerAuth(state.get_access_token()),
    )
    raise_for_status(resp)
    typer.echo(resp.json())


@finance_app.command("delete")
def finance_delete(
    finance_id: int = typer.Option(..., help="Finance ID"),
    subscription_id: UUID = typer.Option(..., help="Subscription ID"),
) -> None:
    """Delete a finance record for a subscription."""
    endpoint = create_url("accounting/finances")

    resp = requests.delete(
        endpoint + f"/{finance_id}",
        json={"sub_id": str(subscription_id)},
        auth=BearerAuth(state.get_access_token()),
    )
    raise_for_status(resp)
    typer.echo(resp.json())


@finance_app.command("list")
def finance_list(
    subscription_id: UUID = typer.Option(..., help="Subscription ID"),
) -> None:
    """List all finance records for a subscription."""
    endpoint = create_url("accounting/finance")
    resp = requests.get(
        endpoint,
        json={
            "sub_id": str(subscription_id),
        },
        auth=BearerAuth(state.get_access_token()),
    )
    raise_for_status(resp)
    typer.echo(resp.json())


@subscription_app.command()
def cost_recovery(
    month: str = typer.Option(..., help="A month, in YYYY-MM format"),
    for_real: bool = typer.Option(
        False, "--for-real/--dry-run", help="Save the results to the database"
    ),
) -> None:
    """Recover costs for a given month."""
    # The first day of the month
    try:
        month_date = date.fromisoformat(month + "-01")
    except ValueError:
        typer.secho(
            "Month must be in YYYY-MM format",
            fg=typer.colors.RED,
        )
        raise typer.Abort()

    endpoint = create_url("accounting/cli-cost-recovery")

    if for_real:
        # If we POST, the server commits the calculated costs to the db
        resp = requests.post(
            endpoint,
            json={
                "first_day": month_date.isoformat(),
            },
            auth=BearerAuth(state.get_access_token()),
        )

    else:
        # If we GET, the server returns the calculated recoverable costs
        resp = requests.get(
            endpoint,
            json={
                "first_day": month_date.isoformat(),
            },
            auth=BearerAuth(state.get_access_token()),
        )

    raise_for_status(resp)
    typer.echo(resp.json())
