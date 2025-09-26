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
- Locate alembic.ini at repo root (paths.REPO_ROOT / "alembic.ini") and set
  `Config(file_=...)`; script_location is `migrations` per our repo.

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

from __future__ import annotations

import logging
import time
from typing import Any, Iterable, Sequence, cast

import typer
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine

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


__all__ = ["init_db_command"]


def _build_alembic_config(database_url: str) -> Config:
    """Return a configured Alembic ``Config`` instance."""

    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _current_heads(engine: Engine) -> list[str]:
    """Return the current database migration heads."""

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        heads: Iterable[str] = context.get_current_heads() or []
        return sorted(heads)


def _script_heads(config: Config) -> list[str]:
    """Return the Alembic script heads defined in the repository."""

    script = ScriptDirectory.from_config(config)
    return sorted(script.get_heads())


@wrap_cli_main
def init_db_command(
    ctx: typer.Context,
    revision: str = typer.Option(
        "head",
        "--revision",
        help="Target revision identifier (default: head).",
        show_default=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Summarise intended actions without applying migrations.",
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
    """Apply Alembic migrations or simulate the operations.

    Examples
    --------
      manage.py init-db
      manage.py init-db --revision base
      manage.py init-db --dry-run -v
    """

    settings = get_settings()
    ctxd = _ctx_dict(ctx)
    global_verbose = bool(ctxd.get("verbose", False))
    effective_verbose = verbose or global_verbose
    configure_logging(
        settings,
        force_level="DEBUG" if effective_verbose else None,
    )
    logger = logging.getLogger("app.cli.init_db")

    with with_trace_id(new_trace_id()):
        start = time.monotonic()
        target_revision = revision or "head"
        logger.info(
            "init-db start",
            extra={"target_revision": target_revision, "env": settings.APP_ENV},
        )

        config = _build_alembic_config(settings.effective_database_url)
        engine = create_engine_from_settings(settings, role="cli-init-db")

        try:
            if dry_run:
                ping_result = ping(engine)
                db_heads = _current_heads(engine)
                script_heads = _script_heads(config)
                logger.info(
                    "init-db dry-run",
                    extra={
                        "target_revision": target_revision,
                        "database_heads": db_heads,
                        "script_heads": script_heads,
                        "ping_ms": ping_result.get("duration_ms"),
                    },
                )
                typer.echo(
                    (
                        f"Current heads: {db_heads or ['<empty>']} | "
                        f"Script heads: {script_heads or ['<empty>']} | "
                        f"Target: {target_revision}"
                    )
                )
                return

            before_heads = _current_heads(engine)
        finally:
            engine.dispose()

        command.upgrade(config, target_revision)

        post_engine = create_engine_from_settings(settings, role="cli-init-db")
        try:
            after_heads = _current_heads(post_engine)
        finally:
            post_engine.dispose()

        applied: Sequence[str] = [
            head for head in after_heads if head not in before_heads
        ]
        duration_ms = (time.monotonic() - start) * 1000.0
        logger.info(
            "init-db complete",
            extra={
                "applied_count": len(applied) or len(after_heads),
                "duration_ms": duration_ms,
            },
        )
        if applied:
            typer.echo(f"Applied revisions: {', '.join(applied)}")
        else:
            typer.echo("Database already at requested revision.")
