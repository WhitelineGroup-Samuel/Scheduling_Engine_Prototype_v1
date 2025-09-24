"""
===============================================================================
File: app/config/logging_config.py
Purpose
-------
Central logging configuration applied once at process start (run.py / CLI).
Supports human and JSON formats, injects `trace_id/env/app/version`, and redacts
secrets (DB credentials). Idempotent and fast.

What Codex must implement
-------------------------
Public API:
- configure_logging(settings) -> logging.Logger
    * Builds & applies a dictConfig that:
      - Emits to **stdout** only (no files by default).
      - Selects **JSON** formatter when `settings.LOG_JSON` is true; otherwise uses
        a human-readable formatter.
      - Attaches filters in this order: StaticFieldsFilter -> TraceIdFilter -> RedactionFilter.
      - Sets root level from `settings.LOG_LEVEL`.
      - Lowers noise from libraries (e.g., `sqlalchemy.engine` to WARNING by default).
    * Returns an app logger: `logging.getLogger("app")` (or root if you prefer).

- Optional helper: get_logger(name: str) -> logging.Logger
    * Ensures `configure_logging()` ran once (idempotent) and returns a named logger.

Formatters:
- Human formatter (dev):
    fmt = "%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s | %(message)s"
    datefmt = ISO-8601 with local offset (no color; keep width-friendly)
    Note: The underlying timestamp can be UTC; display offset is fine.

- JSON formatter (ci/prod):
    Emits a single-line JSON object with keys:
      ts (UTC ISO8601, Z)
      level
      logger
      trace_id
      msg
      env
      app
      version
    Include arbitrary extras if present (e.g., duration_ms, db, component).
    Implementation may subclass `logging.Formatter` and `json.dumps(record_dict)`.

Filters:
- StaticFieldsFilter(settings):
    Injects `env=settings.APP_ENV`, `app=settings.APP_NAME` (fallback "scheduling-engine"),
    `version=settings.APP_VERSION` (from package metadata if available, else "0.1.0").

- TraceIdFilter:
    Reads current trace id from `app.utils.logging_tools` (contextvar). If absent,
    generate one and set it for the current context; attach to `record.trace_id`.

- RedactionFilter:
    Scrubs secrets in `record.getMessage()` **and** any known fields:
      - redact credentials inside URLs: "://user:pass@" -> "://***:***@"
      - wipe env-style secrets if present: DB_PASSWORD, DATABASE_URL password part, etc.
    Keep rules conservative and testable; prefer small, explicit regexes.

Handlers:
- stdout: `logging.StreamHandler(sys.stdout)` using chosen formatter + filters.

Loggers:
- Root: level from settings; handler: stdout; propagate=False.
- Library overrides:
    "sqlalchemy.engine": WARNING (can be tuned to INFO when diagnosing)
    "alembic": INFO (optional)

Idempotency & safety:
- Calling `configure_logging()` multiple times must not duplicate handlers.
- Do not log secrets during configuration; only log sanitized summaries.

Top-level run behavior specifics
-------------------------
- `run.py` may call `configure_logging(settings, force_json=flags.json_logs, force_level="DEBUG" if flags.verbose else None)`.
- Must be safe to call multiple times without duplicating handlers (idempotent).
- Must not log secrets while configuring.

Settings contract (read-only usage)
-----------------------------------
- settings.APP_ENV: "dev" | "test" | "prod"
- settings.LOG_LEVEL: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"
- settings.LOG_JSON: bool (prod/CI recommended True; dev default False)
- settings.APP_NAME: str ("scheduling-engine" default if missing)
- settings.APP_VERSION: str ("0.1.0" default if missing)

Tests that must pass (see tests/test_smoke.py)
----------------------------------------------
- configure_logging(settings) returns a logger without raising.
- In human mode, `caplog` captures a record that has `trace_id` in LogRecord.
- In JSON mode, emitted line parses as JSON and contains keys:
  ts, level, logger, trace_id, msg, env, app, version.

Collaborators
-------------
- app.utils.logging_tools: contextvars + trace helpers (new_trace_id/get_trace_id/with_trace_id)
- app.config.settings: provides values listed above

Non-goals
---------
- No file rotation or external sinks in v1.
- No structured exception serialization beyond standard logging (optional later).

===============================================================================
"""
