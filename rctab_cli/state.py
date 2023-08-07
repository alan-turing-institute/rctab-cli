from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass()
class State:
    access_token: Optional[Callable]
    verbose: bool = False

    def get_headers(self) -> Dict:
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token()['access_token']}"}

        raise ValueError("access_token method not available")

    def get_access_token(self) -> str:
        if self.access_token:
            return self.access_token()["access_token"]
        raise ArithmeticError


state = State(access_token=None)
