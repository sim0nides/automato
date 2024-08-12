# Development

## Installation

1. Install [poetry](https://python-poetry.org/docs/#installation)

2. Install dependencies:

```bash
poetry install
```

3. Enable pre-commit hook:

```bash
poetry run pre-commit install
```

## Useful commands

- Run tests:

```bash
poetry run pytest
```

- Lint:

```bash
poetry run ruff # use --fix to write changes
```

- Sort imports:

```bash
poetry run isort # use --diff without applying changes
```
