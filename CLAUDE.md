# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Context

This repository is a standalone product feature for **adding and retaining notes from books as they are being read**. As a reader finds interesting information - quotes, facts, plot-points, character knowledge - they can add notes to the application for retrieval later.
Desktop prototype first (Python/Kivy), Android target later.

## Stack
- UI: Kivy
- ORM: SQLAlchemy
- DB: SQLite
- Python 3.11+

## Project Structure
- models/       SQLAlchemy models (Book, Entry, Topic, Person)
- screens/      Kivy screen classes
- services/     External API calls and business logic
- main.py       App entry point
- booknotes.kv  Kivy layout definitions

## Code Style
- Use SQLAlchemy 2.0 style (not legacy 1.x patterns)
- Keep UI logic in screens/, business logic in services/
- Type hints on all function signatures

## Commands

All commands should be run from the repository root.

**Dependency management:** Uses `uv` (not pip or poetry).

```bash
# Install all dependencies
uv sync

# Add a runtime dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>

# Lint and auto-fix
uv run ruff check . --fix

# Format code
uv run ruff format .

# Run the main pipeline
uv run python main.py

# Install pre-commit hooks (first time setup)
uv run pre-commit install

# Run pre-commit checks manually
uv run pre-commit run --all-files
```

**Pre-commit hooks** (configured in `.pre-commit-config.yaml`) run ruff lint and ruff format on every commit. Tests are not run in pre-commit.