from click.testing import Result


class ExitCodeException(Exception):
    def __init__(self, result: Result) -> None:
        self.result = result
        super().__init__()

    def __str__(self) -> str:
        return f"\nexit code: {self.result.exit_code}" f"\nstdout: {self.result.stdout}"
