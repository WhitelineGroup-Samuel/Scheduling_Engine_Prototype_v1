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

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, cast

import typer

from app.config.logging_config import configure_logging
from app.config.settings import get_settings
from app.errors.handlers import wrap_cli_main
from app.utils.logging_tools import new_trace_id, with_trace_id

__all__ = ["lint_sql_command"]


def _ctx_dict(ctx: typer.Context) -> dict[str, Any]:
    obj = ctx.obj
    if isinstance(obj, dict):
        return cast(dict[str, Any], obj)
    empty: dict[str, Any] = {}
    return empty


def _count_violations(record: dict[str, Any]) -> int:
    """Return the number of actionable violations for a lint record."""
    total = 0
    violations = record.get("violations")
    if isinstance(violations, list):
        violations_list = cast(list[dict[str, Any] | object], violations)
        for v_any in violations_list:
            ignore = False
            if isinstance(v_any, dict):
                v_dict = cast(dict[str, Any], v_any)
                ignore = bool(v_dict.get("ignore"))
            else:
                ignore = bool(getattr(v_any, "ignore", False))
            if not ignore:
                total += 1
    return total


def _normalise_records(records: Any) -> list[dict[str, Any]]:
    """Render sqlfluff lint records into dictionaries."""
    normalised: list[dict[str, Any]] = []
    if isinstance(records, list):
        records_list = cast(list[dict[str, Any] | object], records)
        for r_any in records_list:
            if isinstance(r_any, dict):
                r_dict = cast(dict[str, Any], r_any)
                normalised.append(r_dict)
    elif hasattr(records, "as_records"):
        raw = records.as_records()
        raw_list: list[dict[str, Any] | object] = []
        if isinstance(raw, list):
            raw_list = cast(list[dict[str, Any] | object], raw)
        for r_any in raw_list:
            if isinstance(r_any, dict):
                r_dict = cast(dict[str, Any], r_any)
                normalised.append(r_dict)
    return normalised


@wrap_cli_main
def lint_sql_command(
    ctx: typer.Context,
    path: Path | None = typer.Argument(
        None,
        help="Directory or file glob to lint (default: ./sql).",
    ),
    rules: str | None = typer.Option(
        None,
        "--rules",
        help="Comma separated rule codes to enforce (e.g. L001,L003).",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable DEBUG logging for this invocation only.",
        is_flag=True,
    ),
) -> None:
    """Lint SQL files using sqlfluff when available.

    Examples
    --------
      manage.py lint-sql
      manage.py lint-sql ./sql --rules L001,L003
      manage.py lint-sql -v
    """

    settings = get_settings()
    ctxd = _ctx_dict(ctx)
    global_verbose = bool(ctxd.get("verbose", False))
    effective_verbose = verbose or global_verbose
    configure_logging(
        settings,
        force_level="DEBUG" if effective_verbose else None,
    )
    logger = logging.getLogger("app.cli.lint_sql")

    default_path = Path("./sql")
    explicit_path = path is not None
    target_path = path or default_path

    if not target_path.exists():
        if explicit_path:
            raise OSError(f"Specified path does not exist: {target_path}")
        logger.info("lint-sql skipped: path missing", extra={"path": str(target_path)})
        typer.echo(f"No SQL directory at {target_path}, skipping lint.")
        return

    try:
        from sqlfluff.core import Linter
    except Exception:
        logger.info("sqlfluff unavailable; skipping SQL linting")
        typer.echo("sqlfluff is not installed; skipping lint.")
        return

    rule_list = (
        [rule.strip() for rule in rules.split(",") if rule.strip()] if rules else None
    )
    linter_kwargs: dict[str, Any] = {}
    if rule_list:
        linter_kwargs["rule_whitelist"] = tuple(rule_list)

    with with_trace_id(new_trace_id()):
        linter = Linter(**linter_kwargs)
        lint_result = linter.lint_paths(paths=(str(target_path),))
        records = _normalise_records(lint_result)

        per_file: list[tuple[str, int]] = []
        for record in records:
            record_dict: dict[str, Any] = record
            filepath = record_dict.get("filepath")
            if filepath is None:
                continue
            per_file.append((str(filepath), _count_violations(record_dict)))

        files_scanned = len(per_file)
        total_violations = sum(count for _, count in per_file)

        logger.info(
            "lint-sql complete",
            extra={
                "files_scanned": files_scanned,
                "violations": total_violations,
                "enforced_rules": rule_list,
            },
        )

        for filepath, count in per_file:
            typer.echo(f"{filepath}: {count} violation(s)")

        typer.echo(
            f"Total files scanned: {files_scanned} | Total violations: {total_violations}"
        )

        if total_violations:
            log_method = logger.error if rule_list else logger.warning
            log_method(
                "lint-sql violations detected",
                extra={"violations": total_violations, "enforced_rules": rule_list},
            )
            if rule_list:
                raise typer.Exit(2)
