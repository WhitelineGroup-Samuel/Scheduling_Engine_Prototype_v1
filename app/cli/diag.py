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
   - JSON keys MUST be:
       {
         "app": {"name": str, "version": str, "env": str},
         "python": {"version": str, "impl": str, "platform": str},
         "tz": {"timezone": str, "valid": bool},
         "db": {
            "ok": bool,
            "database": str | None,
            "server_version": str | None,
            "duration_ms": float | None,
         },
         "alembic": {"heads": list[str] | None}
       }
4) Exit codes:
   - Partial failures should not crash; log individual errors and still exit 0
     unless --strict is introduced (not in v1).

Integration & dependencies
--------------------------
- app.config.settings, app.config.logging_config
- app.db.healthcheck.ping
- alembic (heads) — optional; if not present, log INFO and omit field
- app.errors.handlers (@wrap_cli_main)
- app.db.engine.create_engine_from_settings(settings)  # build a SQLAlchemy Engine

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

from __future__ import annotations

import json
import logging
import platform
import time
from typing import Any, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import typer
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.config.logging_config import configure_logging
from app.config.paths import MIGRATIONS_DIR, REPO_ROOT
from app.config.settings import get_settings
from app.db.engine import create_engine_from_settings
from app.db.healthcheck import ping
from app.errors.handlers import wrap_cli_main
from app.utils.logging_tools import new_trace_id, with_trace_id


def _ctx_dict(ctx: typer.Context) -> dict[str, Any]:
    obj = ctx.obj
    if isinstance(obj, dict):
        return cast(dict[str, Any], obj)
    return {}


__all__ = ["diag_command"]


def _load_alembic_heads() -> list[str]:
    """Return the configured Alembic script heads."""

    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    script = ScriptDirectory.from_config(config)
    return sorted(script.get_heads())


def _validate_timezone(timezone: str) -> bool:
    """Return True when the timezone identifier is valid."""

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return False
    except Exception:
        return False
    return True


@wrap_cli_main
def diag_command(
    ctx: typer.Context,
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON diagnostics payload instead of text.",
        is_flag=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable DEBUG logging for this invocation only.",
        is_flag=True,
    ),
) -> None:
    """Emit diagnostic information about the runtime environment.

    Examples
    --------
      manage.py diag
      manage.py diag --json
      manage.py diag -v
    """

    settings = get_settings()
    ctxd = _ctx_dict(ctx)
    global_verbose = bool(ctxd.get("verbose", False))
    effective_verbose = verbose or global_verbose
    configure_logging(
        settings,
        force_level="DEBUG" if effective_verbose else None,
    )
    logger = logging.getLogger("app.cli.diag")

    default_json = bool(ctxd.get("default_json", False))
    emit_json = json_output or default_json

    with with_trace_id(new_trace_id()):
        start = time.monotonic()

        summary: dict[str, Any] = {
            "app": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "env": settings.APP_ENV,
            },
            "python": {
                "version": platform.python_version(),
                "impl": platform.python_implementation(),
                "platform": platform.platform(),
            },
            "tz": {
                "timezone": settings.TIMEZONE,
                "valid": _validate_timezone(settings.TIMEZONE),
            },
            "db": {
                "ok": False,
                "database": None,
                "server_version": None,
                "duration_ms": None,
            },
            "alembic": {"heads": None},
        }

        try:
            engine = create_engine_from_settings(settings, role="cli-diag")
            try:
                ping_result = ping(engine)
            finally:
                engine.dispose()
            summary["db"].update(
                {
                    "ok": bool(ping_result.get("ok", False)),
                    "database": ping_result.get("database"),
                    "server_version": ping_result.get("server_version"),
                    "duration_ms": ping_result.get("duration_ms"),
                }
            )
        except Exception as exc:
            logger.error("diag database ping failed", extra={"error": str(exc)})

        try:
            heads = _load_alembic_heads()
            summary["alembic"]["heads"] = heads
        except Exception as exc:
            logger.error("diag alembic inspection failed", extra={"error": str(exc)})

        duration_ms = (time.monotonic() - start) * 1000.0
        heads_count = len(summary["alembic"]["heads"] or [])
        logger.info(
            "diag complete",
            extra={
                "duration_ms": duration_ms,
                "db_ok": summary["db"]["ok"],
                "heads": heads_count,
            },
        )

        if emit_json:
            typer.echo(json.dumps(summary, separators=(",", ":")))
            return

        db_section = summary["db"]
        db_line = (
            f"DB: ok={db_section['ok']} name={db_section['database']} version={db_section['server_version']} duration_ms={db_section['duration_ms']}"
        )
        heads_display = summary["alembic"]["heads"]
        heads_str = ", ".join(heads_display) if heads_display else "<none>"

        typer.echo(f"App: {summary['app']['name']} v{summary['app']['version']} (env={summary['app']['env']})")
        typer.echo(f"Python: {summary['python']['version']} ({summary['python']['impl']}) on {summary['python']['platform']}")
        typer.echo(f"Timezone: {summary['tz']['timezone']} valid={summary['tz']['valid']}")
        typer.echo(db_line)
        typer.echo(f"Alembic heads: {heads_str}")
