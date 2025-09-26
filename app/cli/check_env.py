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
   - Use a shared sanitizer: if available, call `app.db.engine.sanitize_url_for_log(url)`,
     otherwise replace credentials with "***:***" while preserving host:port/db.
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
- app.db.engine.create_engine_from_settings(settings)  # build a SQLAlchemy Engine

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

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import typer

from app.config.logging_config import configure_logging
from app.config.settings import get_settings
from app.db.engine import create_engine_from_settings, sanitize_url_for_log
from app.db.healthcheck import ping
from app.errors.exceptions import ConfigError
from app.errors.handlers import wrap_cli_main
from app.utils.logging_tools import new_trace_id, with_trace_id


def _ctx_dict(ctx: typer.Context) -> dict[str, Any]:
    obj = ctx.obj
    if isinstance(obj, dict):
        return cast(dict[str, Any], obj)
    return {}


__all__ = ["check_env_command"]

_CREDENTIAL_RE = re.compile(r"://([^:/?#]+):([^@]+)@")


def _sanitize_database_url(url: str) -> str:
    """Return a credential-safe representation of ``url`` for logs/output."""

    try:
        return sanitize_url_for_log(url)
    except Exception:
        return _CREDENTIAL_RE.sub("://***:***@", url)


def _build_summary(settings: Any, sanitized_url: str) -> dict[str, Any]:
    """Construct the non-sensitive environment summary payload."""

    payload: dict[str, Any] = {
        "env": settings.APP_ENV,
        "log_level": settings.LOG_LEVEL,
        "log_json": bool(getattr(settings, "LOG_JSON", False)),
        "timezone": settings.TIMEZONE,
        "db": {
            "url_sanitized": sanitized_url,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "name": settings.DB_NAME,
        },
    }
    return payload


def _validate_timezone(timezone: str) -> list[str]:
    """Return a list of warnings for the provided timezone identifier."""

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return [f"Unknown timezone '{timezone}'"]
    except Exception:
        return [f"Unable to validate timezone '{timezone}'"]
    return []


def _format_latency(value: Any) -> str:
    """Render a latency value for human-readable output."""

    if isinstance(value, (int, float)):
        return f"{value:.2f}ms"
    return "n/a"


@wrap_cli_main
def check_env_command(
    ctx: typer.Context,
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Treat warnings (timezone issues, missing hints) as errors.",
        is_flag=True,
    ),
    json_output: bool | None = typer.Option(
        None,
        "--json/--no-json",
        help="Emit JSON summary instead of human-friendly text.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable DEBUG logging for this invocation only.",
        is_flag=True,
    ),
) -> None:
    """Validate runtime configuration without mutating state.

    Examples
    --------
      manage.py check-env
      manage.py check-env --strict
      manage.py check-env --json
      manage.py check-env -v
    """

    settings = get_settings()
    ctxd = _ctx_dict(ctx)
    global_verbose = bool(ctxd.get("verbose", False))
    effective_verbose = verbose or global_verbose
    configure_logging(
        settings,
        force_level="DEBUG" if effective_verbose else None,
    )
    logger = logging.getLogger("app.cli.check_env")

    default_json = bool(ctxd.get("default_json", False))
    emit_json = json_output if json_output is not None else default_json

    with with_trace_id(new_trace_id()):
        start = time.monotonic()

        try:
            effective_url = settings.effective_database_url
        except ValueError as exc:
            raise ConfigError(
                message="Invalid database configuration.",
                context={"detail": str(exc)},
            ) from exc

        sanitized_url = _sanitize_database_url(effective_url)
        summary = _build_summary(settings, sanitized_url)

        warnings = _validate_timezone(settings.TIMEZONE)
        if warnings:
            summary["warnings"] = warnings
            for warning in warnings:
                logger.warning("check-env warning", extra={"warning": warning})

        engine = create_engine_from_settings(settings, role="cli-check-env")
        try:
            ping_result = ping(engine)
        finally:
            engine.dispose()

        summary["ping"] = {
            "ok": bool(ping_result.get("ok", False)),
            "database": ping_result.get("database"),
            "server_version": ping_result.get("server_version"),
            "duration_ms": ping_result.get("duration_ms"),
        }

        logger.debug("check-env summary", extra={"summary": summary})

        if warnings and strict:
            raise ConfigError(
                message="Configuration warnings treated as errors.",
                context={"warnings": warnings},
            )

        duration_ms = (time.monotonic() - start) * 1000.0
        logger.info(
            "check-env ok",
            extra={
                "duration_ms": duration_ms,
                "database": summary["db"]["name"],
            },
        )

        if emit_json:
            payload: Dict[str, Any] = dict(summary)
            typer.echo(json.dumps(payload, separators=(",", ":")))
        else:
            latency = _format_latency(summary["ping"]["duration_ms"])
            typer.echo(
                (
                    f"Environment {summary['env']} | "
                    f"Database={summary['db']['name']} | "
                    f"Latency={latency}"
                )
            )
