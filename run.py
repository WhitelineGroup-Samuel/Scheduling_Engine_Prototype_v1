"""
===============================================================================
File: run.py
Purpose
-------
Canonical process entrypoint for local development and testing (no web server yet).
Implements a predictable lifecycle:
  env load (dev/test only) → settings → logging → diagnostics → main → shutdown

Runtime flags (argparse)
------------------------
--verbose / -v   : raise log level to DEBUG for this run
--json-logs      : force JSON log formatter regardless of settings.LOG_JSON
--no-banner      : suppress human banner (JSON logs still emitted)
--skip-db-check  : skip read-only DB healthcheck during startup

Boot sequence (must implement in order)
---------------------------------------
1) Early setup:
   - Capture PROCESS_START_TIME via time.monotonic() and PID.
   - Parse flags with argparse (avoid heavy imports before this).

2) Environment load:
   - Determine app_env from OS (default "dev" if unset).
   - If app_env in {"dev","test"}:
       * Call app.config.env.load_dotenv_for_env(app_env, test_mode=(app_env=="test"))
     Else (prod): NO-OP.

3) Settings:
   - Call app.config.settings.get_settings() ONCE; validate required fields.
   - If invalid → raise ConfigError to be handled below.

4) Logging:
   - Call app.config.logging_config.configure_logging(
         settings,
         force_json=flags.json_logs or None,
         force_level=("DEBUG" if flags.verbose else None),
     )
   - Start a new trace for the whole process:
       with logging_tools.with_trace_id(logging_tools.new_trace_id()):
           continue boot…

5) Banner & startup logs:
   - If not flags.no_banner and not (settings.LOG_JSON or flags.json_logs):
       print a one-line banner:
         "{APP_NAME} v{APP_VERSION} | env={APP_ENV} | pid={PID} | tz={TIMEZONE}"
   - Log INFO "startup_begin" with {pid, env, version}.

6) Diagnostics (read-only):
   - If not flags.skip_db_check:
       * Build engine from settings and call app.db.healthcheck.ping(engine, timeout_seconds=5).
       * On success: log INFO "db_ping_ok" with {database, server_version, duration_ms}.
       * On failure: raise DBConnectionError.

7) Main task placeholder:
   - For v1, prefer the simplest behavior: after successful startup and optional DB ping,
     log INFO "ready" and exit(0). (No long-running loop yet.)

8) Signals & shutdown:
   - Register SIGINT/SIGTERM handlers → set a shutdown flag.
   - On first signal: log WARNING "shutdown_requested" {signal}.
   - Allow up to 10s for cleanup; if exceeded → log CRITICAL "shutdown_timeout" and exit 75.
   - On clean exit: log INFO "shutdown_complete" with uptime_ms and exit 0.
   - If you implement a sleep/wait loop instead of exiting immediately, register SIGINT/SIGTERM
     handlers using `signal.signal(...)` and break the loop to exit; otherwise skip signal wiring.

9) Global exception safety:
   - Wrap main() in try/except BaseException:
       code = app.errors.handlers.handle_cli_error(err, logger)
       raise SystemExit(code)

Exit codes (policy)
-------------------
- 0 success
- 78 ConfigError (settings/env)
- 65 DB errors (connect/health/migrate)
- 75 shutdown timeout
- 1 UnknownError

Dependencies
------------
- app.config.env, app.config.settings, app.config.logging_config
- app.utils.logging_tools (trace id helpers)
- app.db.healthcheck (read-only ping)
- app.errors.handlers (error mapping and exit codes)

Testing (later)
---------------
- Unit: flag parsing, banner toggle, JSON override, idempotent logging config.
- Integration: with test DB, ping success path; simulated OperationalError → exit 65.
- Smoke: `python run.py --skip-db-check --no-banner` logs "ready" and exits 0.

Notes
-----
- Keep module import side effects minimal. Heavy imports should occur inside main().

Exports (explicit)
------------------
- export nothing; keep side-effect free imports.
===============================================================================
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import time
from types import FrameType
from typing import Optional

_PROCESS_START_TIME: float = time.monotonic()
_PID: int = os.getpid()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the runtime entrypoint."""

    parser = argparse.ArgumentParser(
        description="Whiteline SportsHub scheduling engine runtime entrypoint.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable DEBUG logging for this execution.",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Force JSON log formatting for this run.",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Suppress the startup banner when using human-readable logs.",
    )
    parser.add_argument(
        "--skip-db-check",
        action="store_true",
        help="Skip the startup database connectivity check.",
    )
    return parser.parse_args(argv)


class _SignalHandler:
    """Manage process shutdown signal handling."""

    def __init__(self, logger: logging.Logger, *, timeout_s: float = 10.0) -> None:
        self._logger = logger
        self._timeout_s = timeout_s
        self._requested = False
        self._first_signal_time: float | None = None

    def __call__(self, signum: int, frame: FrameType | None) -> None:  # noqa: ARG002
        signal_name = signal.Signals(signum).name
        if not self._requested:
            self._requested = True
            self._first_signal_time = time.monotonic()
            self._logger.warning("shutdown_requested", extra={"signal": signal_name})
            return

        elapsed = 0.0
        if self._first_signal_time is not None:
            elapsed = time.monotonic() - self._first_signal_time
        if elapsed >= self._timeout_s:
            self._logger.critical("shutdown_timeout", extra={"signal": signal_name})
            raise SystemExit(75)
        self._logger.warning(
            "shutdown_in_progress",
            extra={"signal": signal_name, "elapsed_s": elapsed},
        )


_SIGNAL_HANDLER: _SignalHandler | None = None


def _register_signal_handlers(logger: logging.Logger) -> None:
    """Register signal handlers for graceful shutdown management."""

    global _SIGNAL_HANDLER
    _SIGNAL_HANDLER = _SignalHandler(logger)
    signal.signal(signal.SIGINT, _SIGNAL_HANDLER)
    signal.signal(signal.SIGTERM, _SIGNAL_HANDLER)


def main(argv: Optional[list[str]] = None) -> None:
    """Execute the scheduling engine runtime bootstrap sequence."""

    args = parse_args(argv)

    app_env = os.getenv("APP_ENV", "dev")
    if app_env in {"dev", "test"}:
        from app.config.env import load_dotenv_for_env

        load_dotenv_for_env(app_env, test_mode=(app_env == "test"))

    from app.config.logging_config import configure_logging
    from app.config.settings import get_settings
    from app.db.engine import create_engine_from_settings
    from app.db.healthcheck import ping
    from app.utils.logging_tools import new_trace_id, with_trace_id

    settings = get_settings()

    configure_logging(
        settings,
        force_json=True if args.json_logs else None,
        force_level="DEBUG" if args.verbose else None,
    )

    logger = logging.getLogger("app.run")

    with with_trace_id(new_trace_id()):
        if not args.no_banner and not (settings.LOG_JSON or args.json_logs):
            banner = (
                f"{settings.APP_NAME} v{settings.APP_VERSION} | env={settings.APP_ENV} "
                f"| pid={_PID} | tz={settings.TIMEZONE}"
            )
            print(banner)

        logger.info(
            "startup_begin",
            extra={
                "pid": _PID,
                "env": settings.APP_ENV,
                "version": settings.APP_VERSION,
            },
        )

        _register_signal_handlers(logger)

        if not args.skip_db_check:
            engine = create_engine_from_settings(settings, role="process-startup")
            try:
                ping_result = ping(engine, timeout_seconds=5.0)
            finally:
                engine.dispose()
            logger.info(
                "db_ping_ok",
                extra={
                    "database": ping_result.get("database"),
                    "server_version": ping_result.get("server_version"),
                    "duration_ms": ping_result.get("duration_ms"),
                },
            )

        logger.info("ready")

        uptime_ms = (time.monotonic() - _PROCESS_START_TIME) * 1000.0
        logger.info("shutdown_complete", extra={"uptime_ms": uptime_ms})


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as err:  # noqa: BLE001
        from app.errors.handlers import handle_cli_error

        logger = logging.getLogger("app.run")
        code = handle_cli_error(err, logger)
        raise SystemExit(code) from err
