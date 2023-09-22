# Installation

## User Install

```bash
pip install git+https://github.com/alan-turing-institute/rctab-cli
```

## Developer Install

To get started install [Poetry](https://python-poetry.org/docs/).

Then from the root of the repository, install dependencies and activate a Poetry shell, which we will assume is active for the rest of the document, with

```bash
poetry install
poetry shell
```

You should also install [pre-commit](https://pre-commit.com) and install the pre-commit hooks with

```bash
pre-commit install --install-hooks
```

and check that all hooks pass by running

```bash
pre-commit run --all-files
```
