"""
===============================================================================
File: app/cli/diag.py
Purpose
-------
Produce a read-only diagnostics bundle: versions, env, timezone, DB ping summary,
and Alembic head(s). Safe to run anytime in dev/test/CI.

Command
-------
manage.py diag [--json] [--verbose/-v]

Flags & behavior
----------------
--json      : Emit machine-readable JSON.
--verbose/-v: DEBUG logging for this run.

Responsibilities
----------------
1) Load settings; configure logging; start new trace.
2) Collect:
   - App: name, version, env
   - Python: version, implementation, platform
   - Timezone: settings.TIMEZONE availability
   - DB: ping summary (db name, server_version, duration_ms)
   - Migrations: current head(s) via Alembic script
3) Output:
   - Human: tidy table-like lines
   - JSON: single dict with nested sections {app, python, tz, db, alembic}
4) Exit codes:
   - Partial failures should not crash; log individual errors and still exit 0
     unless --strict is introduced (not in v1).

Integration & dependencies
--------------------------
- app.config.settings, app.config.logging_config
- app.db.healthcheck.ping
- alembic (heads) — optional; if not present, log INFO and omit field
- app.errors.handlers (@wrap_cli_main)

Logging contract
----------------
- INFO one-line success with duration_ms and quick counts.
- For each failing probe, log an ERROR but continue.

Examples
--------
  manage.py diag
  manage.py diag --json
  manage.py diag -v
===============================================================================
"""
