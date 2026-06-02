# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context

Standalone desktop app for **capturing notes while reading books** — quotes, facts, plot-points, character knowledge. Desktop prototype (Python/Kivy), Android target later.

## Stack
- UI: Kivy 2.3.1
- ORM: SQLAlchemy 2.0 (not legacy 1.x patterns)
- DB: SQLite via `booknotes.db` in the project root
- Python 3.11+

## Commands

All commands run from the repository root.

```bash
uv sync                            # install dependencies
uv run python main.py              # run the app
uv run ruff check . --fix          # lint with auto-fix
uv run ruff format .               # format
uv run pre-commit install          # first-time hook setup
uv run pre-commit run --all-files  # manual hook run
uv run pytest                      # run tests (add pytest: uv add --dev pytest)
```

## Architecture

### KV file loading
Kivy auto-loads a `.kv` file whose name matches the App subclass — `BookNotesApp` → `booknotes.kv`. **Do not call `Builder.load_file("booknotes.kv")` manually** or it loads twice.

- `theme.kv` — shared dynamic classes (`PrimaryButton@Button`, `ScreenTitle@Label`). Included at the top of `booknotes.kv` via `#:include theme.kv`. Do not add a `#:kivy` version header to `theme.kv`.
- `booknotes.kv` — screen layouts and widget rules. Always `#:include theme.kv` at the top.
- All backgrounds via `canvas.before` Rectangle/RoundedRectangle — not `background_color` alone.

### Models (`models/`)
- `base.py` — `DeclarativeBase` shared by all models.
- `associations.py` — pure `Table` objects for many-to-many joins: `entry_topics` and `entry_people`. Kept separate to avoid circular imports between `entry.py` ↔ `topic.py`/`person.py`.
- `Entry` is the central entity. `Topic` and `Person` join to `Entry` (not to `Book`).
- Use SQLAlchemy 2.0 `select()` style: `session.execute(select(Model).where(...)).scalars().all()`

### Database sessions (`services/database.py`)
`get_session()` returns a bare session. **Sessions are short-lived** — open, use, close within a single method. No long-lived sessions on screen classes.

```python
session = get_session()
try:
    ...
finally:
    session.close()
```

`init_db()` is called once in `BookNotesApp.build()` before the screen manager is created.

### Design system
Visual tokens and component patterns for all Kivy screens live in `.claude/skills/kivy-ui-design/`. Read `SKILL.md` and import RGBA values from `colors.py` — never use raw hex. All new screens follow the 8dp spacing grid and 44dp minimum touch targets defined there.

### Screen pattern
Each screen class in `screens/` loads data in `on_enter()` and manages its own session lifecycle. UI logic stays in `screens/`; queries and writes stay close to the model layer, not in KV handlers.

## Testing

Tests use pytest with an in-memory SQLite fixture — no `booknotes.db` file on disk, no teardown needed:

```python
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    s = sessionmaker(bind=engine)()
    yield s
    s.close()
```

pytest is not yet in `pyproject.toml` — add with `uv add --dev pytest`.
