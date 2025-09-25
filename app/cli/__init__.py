"""
===============================================================================
Package: app.cli
Purpose
-------
Group Typer command modules and expose the main Typer application.

Exports (to be implemented by Codex)
------------------------------------
- app         : Typer application (from app/cli/main.py)
- Subcommand modules:
    check_env  (command: check-env)
    init_db    (command: init-db)
    seed_data  (command: seed-data)
    lint_sql   (command: lint-sql)
    diag       (command: diag)

Guidelines
----------
- No heavy imports at package import time (avoid slowing CLI startup).
- Subcommands implement functions; registration is centralized in main.py.
- All commands must use error handlers (@wrap_cli_main) and configure logging first.

Notes
-----
- Keep this __init__ side-effect free; it should be safe to import anywhere.
===============================================================================
"""
