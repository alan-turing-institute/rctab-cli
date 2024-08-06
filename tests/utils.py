"""Utilities for testing."""

from click.testing import Result


class ExitCodeException(Exception):
    """Exception for when a command exits with a non-zero exit code."""

    def __init__(self, result: Result) -> None:
        """Initialize the ExitCodeException class."""
        self.result = result
        super().__init__()

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"\nexit code: {self.result.exit_code}" f"\nstdout: {self.result.stdout}"
