# ADR 0001 — Project Foundation & Stack
- **Status**: Accepted
- **Date**: 2025-09-23
- **Context**: We need a stable, testable skeleton for the Scheduling Engine before implementing scheduling logic.

## Decision
- **Packaging stance**: App-first, package-ready.
- **Runtime**: Python **3.12**, PostgreSQL **16**.
- **Core libs**: SQLAlchemy 2.x, Alembic, Pydantic v2, Typer, python-dotenv.
- **Driver**: psycopg (v3) with binary extras (dev).
- **Logging**: stdlib dictConfig; console + rotating file; optional JSON; `trace_id` via `contextvars`.
- **Quality**: ruff + black, mypy (strict), pytest(+cov), pre-commit; sqlfluff optional.
- **DB policy**: UTC in DB; Alembic for all DDL; **manual DB creation**.
- **CI**: GitHub Actions with Postgres service container.

## Consequences
- Predictable local/CI behavior; minimal hidden magic.
- Slightly more initial ceremony (manual DB create), but fewer production surprises.
- Strict typing/linting increases initial effort, reduces long-term regressions.

## Alternatives Considered
- Package-first (PyPI-style): premature for this stage.
- ORM alternatives: sticking to SQLAlchemy 2.x aligns with ecosystem & Alembic.
- Automatic DB creation: rejected to avoid surprise writes & permissions friction.

## Follow-ups
- Formalize error codes in `app.errors.codes` and handlers mapping.
- Decide UUID vs ULID for PKs.
- Add security scans (`pip-audit`) as non-blocking initially.
