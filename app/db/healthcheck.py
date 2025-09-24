"""
===============================================================================
File: app/db/healthcheck.py
Purpose
-------
Provide a fast, **read-only** Postgres healthcheck used by:
- process startup (`run.py`)
- CLI diagnostics (`manage.py check-env`, `manage.py diag`)
- CI smoke tests

This module MUST NOT mutate schema or data and MUST NOT log on its own
(callers handle logging; this function returns data or raises).

Public API (Codex must implement)
---------------------------------
def ping(engine_or_session, *, timeout_seconds: float = 5.0) -> dict:
    Inputs:
      - engine_or_session: a SQLAlchemy Engine (preferred) or Session.
      - timeout_seconds  : overall timeout budget for the entire ping (float).

    Behavior (strict order; stop on first failure):
      1) Start a monotonic timer.
      2) Open a **fresh connection** (if Engine) or use the Session connection.
      3) Execute ONLY read-only statements:
           a) SELECT 1;
           b) SHOW server_version;
                - If SHOW fails (permissions/compat), FALL BACK to:
                  SELECT version();
                  - Parse the leading numeric segment into `server_version`
                    (e.g., "16.3"); optionally also collect the full banner
                    as `server_version_full` (optional extra).
           c) SELECT current_database();
      4) Compute `duration_ms` from the monotonic timer.
      5) Return the dict (success schema below).

    Success return (exact keys/types; deterministic):
      {
        "ok": True,                      # bool
        "database": "<db_name>",         # str, e.g., "scheduling_dev" / "scheduling_test"
        "server_version": "16.3",        # str, leading numeric portion of server version
        "duration_ms": 12.8              # float (milliseconds)
        # Optional extras if trivial to obtain:
        # "server_version_full": "PostgreSQL 16.3 on ...",  # str
        # "read_only": False,                                # bool (if SHOW default_transaction_read_only is available)
      }

    Failure behavior:
      - Do NOT return a dict on failure.
      - Raise DBConnectionError (from app.errors.exceptions) with SAFE context:
          DBConnectionError(
            message="Database healthcheck failed",
            context={
              "database": "<name-if-known-or-None>",
              "timeout_s": timeout_seconds,
              "driver": "psycopg2",     # if easily known
              "op": "healthcheck.ping"
            }
          )
      - Timeouts (your own timer or driver-level) are treated as DBConnectionError
        with the same context (include "timeout_s").

Performance budget & timeouts
-----------------------------
- Target: warm run typically < 50ms; **budget** <= 200ms in normal conditions.
- Enforce an overall **timeout** using the function argument (default 5.0s).
  If exceeded at any point, abort and raise DBConnectionError (include timeout).

Read-only & safety constraints
------------------------------
- Absolutely NO writes, NO DDL, NO locks beyond default.
- Use `sqlalchemy.text()`; avoid ORM overhead.
- Do NOT include secrets in the returned dict or exception messages/context.
  (Callers’ logging filters also redact as a safety net.)

Error mapping (authoritative)
-----------------------------
Map any of the following to DBConnectionError:
- sqlalchemy.exc.OperationalError
- psycopg.errors.InvalidCatalogName (if psycopg is available)
- psycopg.OperationalError (if applicable)
- Any timeout condition (elapsed > timeout_seconds)
- Any other exception during the 3 read-only statements above

(Do NOT raise DBOperationError from this function; it’s strictly connectivity/readiness.)

Integration & callers (how this is consumed)
--------------------------------------------
- run.py:
    If user did not pass --skip-db-check:
      - call ping(engine, timeout_seconds=5)
      - On success: the caller logs one INFO line with {database, server_version, duration_ms}
      - On failure: let exception bubble; top-level handler maps to exit code 65
- CLI check-env:
      Always run ping(); include returned dict under a "ping" key in JSON mode.
- CLI diag:
      Run ping(); place summary under "db" section. In v1, partial failures should
      be logged by the CLI and the command may still exit 0.

Settings and engine helpers
---------------------------
Optional helper (Codex MAY implement for convenience):
- def build_engine_from_settings(settings) -> sqlalchemy.Engine
    Creates an Engine using the effective DB URL. Must NOT connect here; only ping() uses it.

Dependencies
------------
- sqlalchemy (Engine/Connection, text())
- app.errors.exceptions.DBConnectionError

Testing expectations
--------------------
Unit (no real DB):
- Simulate sqlalchemy.exc.OperationalError on first statement → DBConnectionError
- Simulate failure of SHOW server_version; fallback to SELECT version(); parse numeric
- Simulate slow run → exceed timeout_seconds → DBConnectionError with {"timeout_s": ...}

Integration (with `scheduling_test`):
- ping() returns:
    ok is True
    database == "scheduling_test"
    server_version is not empty and looks like digits/dots (e.g., r"^\\d+(\\.\\d+)*$")
    duration_ms > 0

Smoke (existing tests/test_smoke.py):
- test_db_healthcheck_readonly asserts keys above and that no write/DDL occurred.

Redaction
---------
- Never return or include full DATABASE_URL (or credentials) in messages/context.

Notes
-----
- This module should not emit logs by itself; the caller is responsible for logging
  success/failure using the structured logging setup from Phase F Step 13.
===============================================================================
"""
