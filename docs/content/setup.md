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
eval $(poetry env activate)
```

You should also install [pre-commit](https://pre-commit.com) and install the pre-commit hooks with

```bash
pre-commit install --install-hooks
```

run the non-safety pre-commit hooks with

```bash
pre-commit run --all-files
```

set an environment variable with your [safety API key](https://docs.safetycli.com/safety-docs/support/invalid-api-key-error#how-to-get-a-safety-api-key)

```bash
export SAFETY_API_KEY=your-api-key
```

and run the safety hook with

```bash
pre-commit run --all-files --config .pre-commit-safety.yaml
```
