"""
===============================================================================
File: app/cli/seed_data.py
Purpose
-------
Populate minimal, idempotent development/test data (e.g., a sample organisation).
Default is **dry-run** for safety.

Command
-------
manage.py seed-data [--org-name TEXT] [--apply/--dry-run] [--verbose/-v]

Flags & behavior
----------------
--org-name TEXT : Optional override for the default organisation name.
--apply         : Perform upserts inside a transaction (default is --dry-run).
--dry-run       : Print what would be inserted/updated (default).
--verbose/-v    : DEBUG logging for this run.

Responsibilities
----------------
1) Load settings; configure logging; start new trace.
2) Open a SQLAlchemy session (scoped or context-managed).
3) Compute intended changes (deterministic & idempotent).
4) If --dry-run: print counts; DO NOT write; exit 0.
5) If --apply: upsert rows (e.g., Organisation by unique name/slug); commit.
6) Return a summary: {"inserted": n, "updated": m, "skipped": k}.

Exit codes
----------
- DBOperationError (failed SQL)        → 65
- ConflictError (unexpected uniqueness)→ 69
- Success                               → 0

Integration & dependencies
--------------------------
- app.db.session.get_session() or SessionLocal
- app.db.seed.seed_minimal(session, org_name)  # idempotent helper
- app.repositories.organisation_repository
- app.errors.handlers (@wrap_cli_main)
- app.config.logging_config

Logging contract
----------------
- INFO summary on success with counts and duration_ms.
- On failure: single structured error line (no secrets).

Examples
--------
  manage.py seed-data
  manage.py seed-data --org-name "Demo Org"
  manage.py seed-data --apply -v

Notes
-----
- No destructive operations; only upserts for dev/test convenience.

ADDENDUM — Seed expectations
===============================================================================
Command flow (authoritative)
----------------------------
1) Parse flags:
   --org-name TEXT      : optional name; default "Whiteline Demo"
   --apply / --dry-run  : default --dry-run
   -v / --verbose       : bump log level for this run

2) Boot:
   - settings = get_settings()
   - configure_logging(settings)
   - start a new trace context (with_trace_id(new_trace_id()))

3) Open session (via SessionLocal from app.db.session):
   - If --dry-run:
       * Compute intended changes WITHOUT writing:
           - Look up organisation by name via OrganisationRepository.get_by_name()
           - If missing: would insert (derive/normalize slug if absent)
           - If exists but slug/name normalization differs: would update
       * Print a human summary (counts and actions) and exit 0.
   - If --apply:
       * Wrap in one transaction:
           result = seed_minimal(session, org_name=...)
           commit
           print one INFO summary line with counts and key identifiers
           (e.g., organisation name, slug, id)
       * Exit 0

4) Errors:
   - Let SQLAlchemy errors bubble to handlers:
       * IntegrityError -> ConflictError (exit 69)
       * OperationalError -> DBConnectionError (exit 65)
       * ProgrammingError -> DBOperationError (exit 65)
   - Unknown -> UnknownError (exit 1)

Determinism & idempotence
-------------------------
- Re-running --apply with the same inputs must not create duplicates.
- --dry-run and --apply must agree on the proposed actions.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any, Mapping

import typer
from sqlalchemy.orm import Session

from app.config.logging_config import configure_logging
from app.config.settings import get_settings
from app.db.engine import create_engine_from_settings
from app.db.seed import seed_minimal
from app.db.session import create_session_factory, get_session
from app.errors.handlers import wrap_cli_main
from app.repositories.organisation_repository import OrganisationRepository
from app.schemas.organisation import OrganisationInDTO, OrganisationOutDTO
from app.utils.logging_tools import new_trace_id, with_trace_id

__all__ = ["seed_data_command"]

_DEFAULT_ORG_NAME = "Whiteline Demo"


def _extract_identifier(entity: Any) -> str | None:
    """Return a readable identifier from an ORM entity."""

    for attr in ("organisation_id", "id"):
        if hasattr(entity, attr):
            value = getattr(entity, attr)
            return str(value) if value is not None else None
    return None


def _plan_seed(session: Session, org_name: str) -> dict[str, Any]:
    """Compute the intended actions without mutating the database."""

    dto = OrganisationInDTO(name=org_name)
    target_name = dto.name
    target_slug = dto.slug or OrganisationOutDTO.normalize_slug(dto.name)

    repository = OrganisationRepository()
    existing = repository.get_by_name(session, target_name)

    summary: dict[str, Any] = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "items": [],
        "organisation": {"name": target_name, "slug": target_slug},
    }

    if existing is None:
        summary["inserted"] = 1
        summary["items"].append(
            {"action": "insert", "name": target_name, "slug": target_slug}
        )
        return summary

    current_name = getattr(
        existing, "organisation_name", getattr(existing, "name", None)
    )
    current_slug = getattr(
        existing, "slug", getattr(existing, "organisation_slug", None)
    )
    updates: dict[str, str] = {}
    if current_name != target_name:
        updates["name"] = target_name
    if current_slug != target_slug:
        updates["slug"] = target_slug

    identifier = _extract_identifier(existing)
    if updates:
        summary["updated"] = 1
        summary["items"].append(
            {
                "action": "update",
                "id": identifier,
                "changes": updates,
                "current": {"name": current_name, "slug": current_slug},
            }
        )
    else:
        summary["skipped"] = 1
        summary["items"].append(
            {
                "action": "skip",
                "id": identifier,
                "name": current_name,
                "slug": current_slug,
            }
        )
    return summary


def _echo_summary(summary: Mapping[str, Any]) -> None:
    """Emit a human-readable representation of the seed summary."""

    counts = (
        f"inserted={summary.get('inserted', 0)} "
        f"updated={summary.get('updated', 0)} "
        f"skipped={summary.get('skipped', 0)}"
    )
    typer.echo(f"Seed summary: {counts}")
    items = summary.get("items", [])
    if isinstance(items, list):
        for item in items:
            typer.echo(f"  - {item}")


@wrap_cli_main
def seed_data_command(
    ctx: typer.Context,
    org_name: str = typer.Option(
        _DEFAULT_ORG_NAME,
        "--org-name",
        help="Organisation name to ensure exists.",
        show_default=True,
    ),
    apply_changes: bool = typer.Option(
        False,
        "--apply/--dry-run",
        help="Apply changes instead of performing a dry-run preview.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable DEBUG logging for this invocation only.",
        is_flag=True,
    ),
) -> None:
    """Seed deterministic development data with optional application.

    Examples
    --------
      manage.py seed-data
      manage.py seed-data --org-name "Demo Org"
      manage.py seed-data --apply -v
    """

    settings = get_settings()
    global_verbose = bool((ctx.obj or {}).get("verbose"))
    effective_verbose = verbose or global_verbose
    configure_logging(
        settings,
        force_level="DEBUG" if effective_verbose else None,
    )
    logger = logging.getLogger("app.cli.seed_data")

    with with_trace_id(new_trace_id()):
        start = time.monotonic()
        engine = create_engine_from_settings(settings, role="cli-seed-data")
        session_factory = create_session_factory(engine)

        try:
            if not apply_changes:
                session = session_factory()
                try:
                    summary = _plan_seed(session, org_name)
                finally:
                    session.close()
                duration_ms = (time.monotonic() - start) * 1000.0
                logger.info(
                    "seed-data dry-run",
                    extra={
                        "inserted": summary["inserted"],
                        "updated": summary["updated"],
                        "skipped": summary["skipped"],
                        "duration_ms": duration_ms,
                    },
                )
                _echo_summary(summary)
                return

            with get_session(session_factory) as session:
                result = seed_minimal(session, org_name=org_name)

            duration_ms = (time.monotonic() - start) * 1000.0
            logger.info(
                "seed-data applied",
                extra={
                    "inserted": result.get("inserted", 0),
                    "updated": result.get("updated", 0),
                    "skipped": result.get("skipped", 0),
                    "duration_ms": duration_ms,
                },
            )
            _echo_summary(result)
        finally:
            engine.dispose()
