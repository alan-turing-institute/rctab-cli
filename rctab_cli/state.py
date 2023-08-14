"""State module."""
from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass()
class State:
    """Retrieves the state.

    Args:
        access_token: The access token.
        verbose: Whether to display verbose output.
    """

    access_token: Optional[Callable]
    verbose: bool = False

    def get_headers(self) -> Dict:
        """Get the headers with the bearer token if the access_token is valid.

        Raises:
            ValueError: If the access_token is not valid.

        Returns:
            The headers.
        """
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token()['access_token']}"}

        raise ValueError("access_token method not available")

    def get_access_token(self) -> str:
        """Get the access token.

        Returns:
            The access token.
        Raises:
            ArithmeticError: If the access token is not valid.
        """
        if self.access_token:
            return self.access_token()["access_token"]
        raise ArithmeticError


state = State(access_token=None)
