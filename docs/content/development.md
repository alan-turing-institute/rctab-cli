# Development

This page covers working on the RCTab CLI itself.
See [Installation](setup.md) for the developer install and [Usage](usage.md) for the commands.

## Where RCTab CLI fits

The CLI is one component of the wider [RCTab](https://rctab.readthedocs.io/en/latest/) system, which manages Azure subscriptions and spending.
The other components are:

- **RCTab API** — the web server the CLI talks to. It serves the web frontend and receives data from the function apps.
- **Function apps** — *usage* (pulls spending data from Azure), *status* (reports subscription state and access control) and *controller* (enables/disables subscriptions in Azure to match the desired state held by the API).
- **fastapimsal** — the Azure Active Directory single sign-on library used for authentication.
- **Infrastructure** — Pulumi deployment tooling, plus logging and alerting.

This repository contains *only* the CLI.
It has no database of its own: everything it does is an authenticated HTTP request to an RCTab API server.
If a change seems to need a new API endpoint, that work belongs in the RCTab API repository.

## Repository layout

```text
rctab_cli/
├── cli.py          # Typer app, top-level commands, token acquisition
├── auth.py         # MSAL token cache and bearer auth
├── config.py       # Pydantic settings: CLIConfig (.env), AuthSettings (.auth.env)
├── state.py        # Global `state` object holding the access token and verbosity
├── types.py        # URL validation types
├── utils.py        # create_url() and other helpers
└── sub_apps/
    ├── __init__.py # subscription_app and finance_app Typer sub-apps
    └── sub.py      # `rctab sub ...` and `rctab sub finance ...` commands
tests/              # mirrors the package layout
docs/               # Sphinx documentation (this page lives in docs/content/)
```

Documentation source lives in `docs/`.
`docs/index.rst` is the entry point; narrative pages are Markdown files in `docs/content/` and are picked up automatically by the `content/*` glob in the toctree.
API documentation is generated from Google-style docstrings by `autosummary`, so a new public function needs a docstring, not a docs edit.
The built docs are published at <https://rctab-cli.readthedocs.io/>.

Adding a command means adding a function decorated with `@subscription_app.command()` (or `@finance_app.command()`) in `rctab_cli/sub_apps/sub.py`, and a matching test.

## Which server am I talking to?

`BASE_URL` and `PORT` come from `.env` (or the environment), and they determine which RCTab API server every command hits.
There are usually several to choose from:

- the **production** deployment on Azure,
- one or more **dev deployments** on Azure, and
- a **local** API server, typically `http://localhost:8000`.

A local `.env` frequently points at production, often with the dev URLs sitting commented out just above.
**Always check `.env` before running a command that changes anything.**
Commands such as `sub add`, `approve`, `allocate`, `set-persistence`, `finance create/update/delete` and `cost-recovery` write to the RCTab database, and `cost-recovery` in particular is intended to be run exactly once per month, in order — running it against production by mistake is not easily undone.

Read-only commands (`summary`, `approvals`, `allocations`, `finance list`, `finance get`) are safe to explore with, but note that their output contains real subscription IDs, finance codes and amounts.

Use `rctab --verbose ...` to have the CLI echo the URL it is about to call.

## Testing

Tests use **pytest** and live in `tests/`, mirroring the package layout.

```bash
pytest tests/
```

Tests must never make a network request or contact a real RCTab API.
Two patterns are used, often in the same test:

1. **Call the command function directly** and patch its collaborators with `unittest.mock.patch`, naming them at the point of use (`rctab_cli.sub_apps.sub.add_subscription`, not `rctab_cli.sub_apps.sub`'s import source). Assert with `mock.assert_called_once_with(...)`.
2. **Invoke through Typer's `CliRunner`** when the behaviour under test involves argument parsing, defaults or prompts — this is the only way to exercise default parameter values and option names.

```python
from unittest.mock import patch
from typer.testing import CliRunner

from rctab_cli import cli
from tests.utils import ExitCodeException

runner = CliRunner()


def test_something() -> None:
    with patch("rctab_cli.sub_apps.sub.add_subscription") as mock_add:
        result = runner.invoke(cli.app, ["sub", "add", "--subscription-id", "...", "-y"])
        if result.exit_code != 0:
            raise ExitCodeException(result)
        mock_add.assert_called_once_with(...)
```

Raise `tests.utils.ExitCodeException(result)` rather than asserting on the exit code — it prints the command's stdout, which is otherwise swallowed by `CliRunner`.
Pass `-y` to skip interactive confirmation prompts, or supply input via `CliRunner.invoke(..., input=...)`.

Pytest runs on every pull request to `main` (`.github/workflows/pytest.yml`).

## Code quality

Checks are enforced by [pre-commit](https://pre-commit.com) and mirrored in CI: black, isort, mypy, pylint (`.python-lint`) and pydocstyle (Google convention, excluding `tests/`).
Gitleaks runs as a pre-commit hook and as a workflow, and `safety` runs from the separate `.pre-commit-safety.yaml` config.

```bash
pre-commit run --all-files
```

Every public module, class and function in `rctab_cli/` needs a Google-style docstring; `tests/` is exempt from pydocstyle but docstrings are still the norm there.
Type annotations are required — mypy runs over the whole package.

## What not to put in version control

- `.env` and `.auth.env` — server URLs, tenant and client IDs. Both are already git-ignored; keep it that way.
- Any other credentials, tokens or connection strings. The MSAL token cache is written to the Typer app directory outside the repository (`typer.get_app_dir("RCTab-CLI")`), so it should never appear here.
- **Command output containing real data.** Saved responses from `summary`, `finance list` or `cost-recovery` contain live subscription IDs, finance codes and spend figures. Write them outside the repository, or to a git-ignored path.
- Local environment cruft: `.venv/`, `.idea/`, `.DS_Store`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`.

If you need to add a real example to the docs, redact the subscription IDs and finance codes first.
