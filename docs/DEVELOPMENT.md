# Development Guide

## Workflow
- Feature branches from `main`.
- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.
- Open PRs early; small, reviewable changes.

## Tooling
- **Formatter**: black (88 cols)
- **Linter**: ruff (includes isort)
- **Types**: mypy (strict profile)
- **Tests**: pytest (+cov)
- **Pre-commit**: ruff → black → mypy (check) → sqlfluff (optional) → whitespace fixers

## Running Tasks (after code generation)
```bash
# quality
pre-commit run --all-files
ruff check .
black --check .
mypy .

# tests
pytest -q
pytest -q --maxfail=1 -k smoke

# DB
alembic upgrade head
python manage.py seed-data

# app
python run.py
```

## Project Structure (overview)
- ```app/config:``` settings (```pydantic```), env loader, logging dictConfig, paths, feature flags
- ```app/db:``` engine/session/base, alembic env, seed, healthcheck
- ```app/models:``` ORM base mixins (timestamps, soft-delete, etc.)
- ```app/repositories:``` base repository + examples
- ```app/schemas:``` Pydantic DTOs
- ```app/errors:``` codes, exceptions, handlers
- ```app/utils:``` logging tools, time, ids, io, validators
- ```app/cli:``` Typer commands (check-env, init-db, seed-data, lint-sql, diag)

## Policies
- No side effects in ```__init__``` files.
- All DDL via Alembic.
- Logs include ```trace_id```, no secrets.
- Store UTC in DB; present in Australia/Melbourne when needed.

## CI Expectations
- GitHub Actions: lint → type-check → tests; Postgres service for DB steps.
- Coverage floor (skeleton): 70%.

## ADRs
- Major structural decisions require an ADR in ```docs/ADR/```.
