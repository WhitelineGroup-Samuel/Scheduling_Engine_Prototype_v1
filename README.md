# Whiteline SportsHub — Scheduling Engine (Back-End Prototype)

A production-grade **skeleton** for the Regular Rounds Scheduling Engine. This repo provides a clean, testable foundation: configuration, logging, DB wiring (PostgreSQL + SQLAlchemy 2.x + Alembic), CLI utilities, CI hooks, and VS Code ergonomics — **without** scheduling logic yet.

## Stack (locked)
- **Python** 3.12
- **PostgreSQL** 16 (manual DB creation)
- **SQLAlchemy** 2.x, **Alembic**
- **Pydantic v2** (Settings), **Typer** (CLI), **python-dotenv**
- Logging: stdlib `logging` + dictConfig (console + rotating file; optional JSON)
- Quality: **ruff**, **black**, **mypy (strict)**, **pytest** (+cov), **pre-commit**
- Optional: **sqlfluff** for `/sql` lint

## Quick Start
1. **Python 3.12**: install via Homebrew or pyenv.
2. Create venv & select in VS Code:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Create databases manually** (per company policy):
    - **Dev DB:** ```scheduling_dev``` - used for local development.
    - **Test DB:** ```scheduling_test``` - used for automated tests and migrations.
4. Copy ```.env.example``` → ```.env``` and set:
    ```bash
    APP_ENV=dev
    EXPORT_DIR=./exports
    LOG_LEVEL=INFO
    DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/scheduling_dev
    TIMEZONE=Australia/Melbourne
    LOG_JSON=false
    ```
5. (Soon) Install deps → run tasks:
    ```bash
    # when pyproject is populated
    pip install -e .
    pre-commit install
    ```

## Commands (once generated)
- ```python run.py``` — bootstrap app: load settings, configure logging, DB ping, migration head check.
- ```python manage.py``` — developer CLI:
    - ```check-env``` — validate ```.env``` completeness and types
    - ```init-db``` — run ```alembic upgrade head```
    - ```seed-data``` — minimal rows for dev
    - ```lint-sql``` — lint ```/sql``` (optional)
    - ```diag``` — environment/system diagnostics

## Project Layout (excerpt)
```arduino
app/
config/   # settings, env, logging config, paths, feature flags
db/       # engine, session, base, alembic env, seed, healthcheck
models/   # core mixins; (domain models later)
repositories/
schemas/
errors/
utils/
cli/
migrations/
docs/
tests/
.vscode/
```

## Policies
- See ```docs/POLICY_DIGEST.md``` for **non-negotiables**.
- No automatic DB creation in code. All creation/ownership is manual via pgAdmin or SQL.
- All schema changes via Alembic migrations (coming in later steps).
- UTC stored in DB; app presents in Australia/Melbourne.

## Status
This is a **skeleton**. Scheduling logic (phases/allocators) will be added after the foundations are finalized and tested.
