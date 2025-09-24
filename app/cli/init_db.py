"""
===============================================================================
File: app/cli/init_db.py
Purpose
-------
Apply Alembic migrations to bring the database to the desired revision.
Safe to re-run when already at head (idempotent apply).

Command
-------
manage.py init-db [--revision TEXT] [--dry-run] [--verbose/-v]

Flags & behavior
----------------
--revision TEXT : Target revision (default: "head").
--dry-run       : Check connectivity and summarize intended actions without applying.
--verbose/-v    : Raise log level to DEBUG for this run only.

Responsibilities
----------------
1) Load settings; configure logging; begin a new trace context.
2) Resolve target revision (default "head").
3) If --dry-run:
   - Verify DB connectivity and Alembic script location.
   - Print would-do summary (current heads, target revision).
   - Exit 0.
4) Else:
   - Invoke Alembic upgrade to the target revision (online mode).
   - Provide a count/list of applied revisions if easily available.
5) Exit codes:
   - DBMigrationError (multiple heads, failed upgrade) → 65
   - DBConnectionError (cannot connect)               → 65
   - Success                                          → 0

Integration & dependencies
--------------------------
- alembic.config.Config, alembic.command.upgrade
- app.db.alembic_env (wired via alembic.ini script_location = migrations)
- app.config.settings, app.config.logging_config
- app.errors.handlers (@wrap_cli_main)
- Optional: app.db.healthcheck.ping for pre-checks when --dry-run

Logging contract
----------------
- INFO "init-db start" {target_revision, env}
- INFO "init-db complete" {applied_count, duration_ms}
- On failure: structured log via handlers; CRITICAL with traceback for migration failures.

Examples
--------
  manage.py init-db
  manage.py init-db --revision base
  manage.py init-db --dry-run -v

Notes
-----
- Do not attempt to create the database itself (we manage DB creation manually).
- Offline SQL generation is out of scope for v1 (can be added later).
===============================================================================
"""
