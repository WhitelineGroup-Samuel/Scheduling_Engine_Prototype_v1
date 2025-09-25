"""
===============================================================================
File: app/cli/check_env.py
Purpose
-------
Validate required configuration and prove runtime wiring via a read-only check.
Intended to be safe to run anytime in dev/test/CI.

Command (registered in app/cli/main.py)
---------------------------------------
manage.py check-env [--strict] [--json] [--verbose/-v]

Flags & behavior
----------------
--strict    : Treat warnings (e.g., optional-but-recommended vars missing) as errors.
--json      : Emit a machine-friendly JSON summary to stdout.
--verbose/-v: Raise log level to DEBUG for this run only (do not persist).

Responsibilities
----------------
1) Load settings via canonical factory (e.g., app.config.settings.get_settings()).
2) Build a sanitized summary (redact DB secrets):
   - APP_ENV, LOG_LEVEL, LOG_JSON, TIMEZONE
   - Effective DATABASE_URL (with "user:pass" redacted as "***:***")
   - DB_HOST/DB_PORT/DB_NAME (safe)
3) Read-only DB ping:
   - Connect using engine built from settings (no schema mutations).
   - SELECT 1; SELECT version(); SELECT current_database().
   - Return {ok: bool, database, server_version, duration_ms}.
4) Output
   - Human: print a one-line OK summary at INFO; details at DEBUG on --verbose.
   - JSON: dump keys {env, log_level, db: {url_sanitized, host, port, name}, ping: {...}}.
5) Exit codes (see app.errors.codes):
   - ConfigError (invalid/missing)           → 78
   - DBConnectionError (cannot connect)      → 65
   - Success                                 → 0

Integration & dependencies
--------------------------
- app.config.settings  : read-only
- app.config.logging_config.configure_logging(settings): ensure logging before printing
- app.db.healthcheck.ping(engine) : read-only ping helper
- app.errors.handlers  : use @wrap_cli_main to enforce single-line structured error logs

Logging contract
----------------
- Use configure_logging(settings) once.
- Start command within a new trace context:
    with logging_tools.with_trace_id(logging_tools.new_trace_id()):
        ...
- INFO success: "check-env ok" with duration_ms and db.name.
- On failure: one structured log line via handle_cli_error in the decorator.

Examples (for --help epilog)
----------------------------
  manage.py check-env
  manage.py check-env --strict
  manage.py check-env --json
  manage.py check-env -v

Notes
-----
- Never print raw secrets.
- Should not modify filesystem or database.
===============================================================================
"""
