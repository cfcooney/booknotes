# booknotes

Desktop prototype for capturing and organizing notes while reading books.

## Stack

- Python 3.11+
- Kivy
- SQLAlchemy 2.0
- SQLite

## Setup

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## Lint and Format

```bash
uv run ruff check . --fix
uv run ruff format .
```

## Pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
