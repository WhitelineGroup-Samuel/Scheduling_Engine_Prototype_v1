"""
===============================================================================
File: app/db/engine.py
Purpose
-------
Create and manage the canonical SQLAlchemy **Engine** for Postgres.
Enforce safe defaults (timeouts, pooling, pre-ping, redaction) and provide
helpers for building sanitized URLs for logs. The engine is used by:
- healthcheck (read-only ping)
- session factory (transactions, repositories)
- CLI commands (init-db, seed-data, diag, check-env)
- Alembic (via separate alembic.ini path, not this module)

Public API (Codex must implement)
---------------------------------
1) def create_engine_from_settings(
       settings,
       *,
       echo_sql: bool | None = None,
       role: str = "app",
       statement_timeout_ms: int | None = 5000,
       idle_in_tx_timeout_ms: int | None = 120000,
       connect_timeout_s: int | None = 5,
   ) -> "sqlalchemy.Engine":
   Behavior:
   - Build an Engine for Postgres using an **effective URL** from `settings`:
       * Prefer settings.DATABASE_URL when provided (must be "postgresql+psycopg2://...")
       * Else compose from parts (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
   - Safe defaults:
       * pool_pre_ping=True (detect dead connections)
       * pool_size=5 (dev/test), max_overflow=5, pool_timeout=10, pool_recycle=1800
       * echo=echo_sql if provided else (True only when APP_ENV=="dev" and LOG_LEVEL=="DEBUG")
       * future=True (if using SQLAlchemy 2.x style)
   - connect_args (psycopg2):
       * "connect_timeout": connect_timeout_s (default 5)
       * "application_name": f"{settings.APP_NAME}:{role}"
       * optionally "options": f"-c statement_timeout={statement_timeout_ms} -c idle_in_transaction_session_timeout={idle_in_tx_timeout_ms}"
         (Only include clauses that are not None)
   - MUST NOT log unsanitized URLs (use sanitizer below).
   - Return the Engine instance.

2) def sanitize_url_for_log(url: str) -> str
   - Redact credentials in a Postgres URL:
       "postgresql+psycopg2://user:pass@host:5432/db" -> "postgresql+psycopg2://***:***@host:5432/db"
   - Keep scheme/host/port/dbname intact for troubleshooting.

3) Optional: def engine_diagnostics(engine) -> dict
   - Return simple, **non-connecting** metadata about the engine configuration:
     {"pool_size": int, "max_overflow": int, "echo": bool, "dialect": "postgresql+psycopg2"}
   - MUST NOT connect to the DB just to compute diagnostics.

Safety & timeouts
-----------------
- Use `pool_pre_ping=True` to detect stale connections.
- Enforce driver-level **connect_timeout** via connect_args.
- Prefer **server-side** statement timeouts via the "options" string:
    -c statement_timeout=5000
    -c idle_in_transaction_session_timeout=120000
- These timeouts apply per-connection; callers may still enforce higher-level timeouts.

Environment & settings contract (read-only)
-------------------------------------------
- settings.effective_database_url (property or method; see settings.py)
- settings.APP_ENV, settings.APP_NAME, settings.LOG_LEVEL
- Optional: settings.DB_* parts when composing URL

Logging & redaction
-------------------
- This module must not log secrets. If it logs the URL, always use `sanitize_url_for_log`.
- Final logging formatting is handled by app.config.logging_config filters (trace_id, env, redaction).

Integration
-----------
- Used by healthcheck.ping(engine) (read-only)
- Used by session factory (see app/db/session.py)
- CLI init-db/seed-data/diag/check-env call this to get an Engine.

Testing
-------
- Unit (no DB): constructing engine with composed URL; `sanitize_url_for_log` correctness.
- Integration (test DB): engine connects and works with healthcheck.ping()
  respecting timeouts (no mutation).

Non-goals
---------
- No async engine in v1.
- No engine caching/global singleton here; the caller (CLI/run.py) stores it.
===============================================================================
"""
