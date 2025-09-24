"""
===============================================================================
File: manage.py
Purpose
-------
Top-level entry point for the developer CLI. Keeps itself tiny and delegates to
Typer app defined in `app.cli.main`.

Responsibilities
----------------
- Import `app.cli.main:app`.
- If executed as a script (`__main__`), invoke `app()`.
- No heavy logic here; all behavior lives in subcommand modules.

Usage
-----
  python manage.py --help
  python manage.py check-env
  python manage.py init-db
  python manage.py seed-data
  python manage.py lint-sql
  python manage.py diag

Exit codes
----------
- 0 on success.
- Non-zero per app.errors.codes via @wrap_cli_main in command handlers.

Notes
-----
- Ensure this file remains importable and side-effect free (besides Typer call).
===============================================================================
"""
