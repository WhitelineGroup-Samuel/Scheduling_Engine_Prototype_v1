"""
===============================================================================
File: app/cli/lint_sql.py
Purpose
-------
Lint SQL files under ./sql (or a provided path) using SQLFluff (if installed).
Designed to be an optional helper; soft-fails if SQLFluff is unavailable.

Command
-------
manage.py lint-sql [PATH] [--rules TEXT] [--verbose/-v]

Flags & behavior
----------------
PATH         : Directory or file glob; default "./sql".
--rules TEXT : Optional comma-separated rule codes to enforce (e.g., "L001,L003").
--verbose/-v : DEBUG logging for this run.

Responsibilities
----------------
1) Resolve PATH (default ./sql). If path missing and not provided, exit 0 with info.
2) Attempt to import sqlfluff; if missing → log INFO and exit 0 (informational).
3) Run linting; collect violations. If --rules provided, enforce only those.
4) Summarize results:
   - Human: per-file counts + total violations.
   - JSON: (optional future) not required in v1.
5) Exit codes:
   - IO error accessing files → 74 (IOErrorApp)
   - Lint violations:
       * If --rules provided → non-zero (e.g., 2)
       * If no --rules → exit 0 (informational)
   - Success → 0

Integration & dependencies
--------------------------
- app.config.logging_config
- app.errors.handlers (@wrap_cli_main)
- Optional dependency: sqlfluff

Logging contract
----------------
- INFO summary with {files_scanned, violations, enforced_rules?}
- WARN for violations (if not enforcing), ERROR if enforcing and violations found.

Examples
--------
  manage.py lint-sql
  manage.py lint-sql ./sql --rules L001,L003
  manage.py lint-sql -v

Notes
-----
- Keep runtime small; avoid scanning huge trees by default.
===============================================================================
"""
