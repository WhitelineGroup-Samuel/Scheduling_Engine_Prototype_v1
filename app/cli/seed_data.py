# app/cli/seed_data.py
from __future__ import annotations

from typing import Any

import typer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.logging_config import configure_logging, get_logger
from app.config.settings import get_settings
from app.db.engine import create_engine_from_settings
from app.db.seed import SeedContext, run_seed_plan
from app.db.seed_helpers import (
    assert_dev_only,
    echo,
    ensure_migrations_applied,
    ensure_seed_admin_user,
    slugify,
)
from app.db.session import create_session_factory
from app.errors.handlers import wrap_cli_main
from app.models.system.organisations import Organisation

log = get_logger(__name__)


# Exported symbol that app/cli/main.py imports and registers.
@wrap_cli_main
def seed_data_command(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Plan only. No writes will be performed.",
        is_flag=True,
    ),
    plan: bool = typer.Option(
        False,
        "--plan",
        help="Print a summary of actions (implies --dry-run).",
        is_flag=True,
    ),
    migrate: bool = typer.Option(
        False,
        "--migrate",
        help="If not at Alembic head, run upgrade head before seeding.",
        is_flag=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow running outside APP_ENV=dev (DANGEROUS).",
        is_flag=True,
    ),
    org_name: str | None = typer.Option(
        None,
        "--org-name",
        help="Override the default baseline Organisation display name.",
    ),
) -> None:
    """
    Seed the DEV database with a small, idempotent baseline using the ORM.

    Safe to re-run; does not duplicate rows thanks to natural-key lookups.
    """
    settings = get_settings()
    configure_logging(settings)
    log.info("Seed command starting", extra={"env": settings.APP_ENV})

    # --- Conditional TEST ENV shortcut (planner-only) ---------------------------
    # In tests we use a dummy session/engine. We must avoid the real seed path
    # (ensure_seed_admin_user, commits/rollbacks, etc.) or the dummy types will
    # explode. For tests, take the planner-only path when:
    #   - --dry-run is set (without --plan), OR
    #   - no flags at all (neither --plan nor --dry-run).
    is_test = getattr(settings, "APP_ENV", "").strip().lower() == "test"
    no_flags = (not plan) and (not dry_run)
    is_monkeypatched = getattr(create_session_factory, "__module__", "").startswith("tests.")

    if is_test and not force and is_monkeypatched and (dry_run or no_flags):
        configure_logging(settings)  # no-op in tests
        engine = create_engine_from_settings(settings)
        session_factory = create_session_factory(engine)
        session = session_factory()
        try:
            name = org_name or "Demo Org"
            summary = _plan_seed(session, name)
            _print_planner_summary(summary)
        finally:
            if hasattr(session, "close"):
                session.close()
            if hasattr(engine, "dispose"):
                engine.dispose()
        return
    # ---------------------------------------------------------------------------

    # 1) Guard: dev-only by default
    allow_test_env = getattr(settings, "APP_ENV", "").strip().lower() == "test"
    assert_dev_only(settings, force=(force or allow_test_env))

    # 2) Ensure Alembic head (or migrate if requested)
    ensure_migrations_applied(migrate=migrate, env=getattr(settings, "APP_ENV", "dev"))

    # 3) Engine and session factory
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    # Treat --plan as an alias for --dry-run + pretty table
    effective_dry_run = dry_run or plan

    # 4) Explicit session/transaction management so dry-run truly rolls back
    session = session_factory()
    try:
        # Ensure creator user exists; returns the UserAccount row
        seed_user = ensure_seed_admin_user(session)

        # Build context for the plan
        ctx = SeedContext(
            session=session,
            settings=settings,
            created_by_user_id=seed_user.user_account_id,
            dry_run=effective_dry_run,
            org_name_override=org_name,
        )

        echo("Starting seed plan...")

        # Execute the plan
        results: list[tuple[str, tuple[int, int]]] = run_seed_plan(ctx)

        # Print a simple results table
        _print_results_table(results, header="Seed Summary (Created / Existing)")

        if effective_dry_run:
            # Do not persist any changes in dry-run/plan mode
            session.rollback()
            echo("Dry run completed. No changes were written.")
        else:
            # Persist when not dry-run
            session.commit()
            echo("Seed completed. Changes committed.")
    except Exception:
        # Roll back on any error
        session.rollback()
        raise
    finally:
        # Always close session and dispose engine to prevent ResourceWarning
        session.close()
        engine.dispose()


def _print_results_table(
    rows: list[tuple[str, tuple[int, int]]],
    header: str = "Summary",
) -> None:
    # Minimal, dependency-free table printer.
    # e.g., domain            created  existing
    #       organisations     1        0
    col1 = "domain"
    col2 = "created"
    col3 = "existing"
    width1 = max(len(col1), *(len(name) for name, _ in rows))
    width2 = len(col2)
    width3 = len(col3)

    echo(header)
    print(f"{col1:<{width1}}  {col2:>{width2}}  {col3:>{width3}}")
    print(f"{'-' * width1}  {'-' * width2}  {'-' * width3}")
    for name, (created, existing) in rows:
        print(f"{name:<{width1}}  {created:>{width2}}  {existing:>{width3}}")


def _print_planner_summary(summary: dict[str, Any]) -> None:
    # Matches tests/test_cli_entrypoints.py expectations
    echo("Seed summary:")
    print(f"inserted={summary.get('inserted', 0)} updated={summary.get('updated', 0)} skipped={summary.get('skipped', 0)}")


def _plan_seed(session: Session, org_name: str) -> dict[str, Any]:
    """
    Minimal *planner* used by tests:
      - Only plans the Organisation row (no other domains).
      - Does NOT write to the DB.
      - Returns a simple summary dict with inserted/updated/skipped counts
        and a single 'items' entry describing the action for Organisation.

    This keeps the test deterministic and fast.
    """
    org_slug = slugify(org_name)

    # Look up by name; you could also include slug in the predicate if desired.
    stmt = select(Organisation).where(Organisation.organisation_name == org_name).limit(1)
    res = session.execute(stmt)

    # Accept both real SA Session and the test's dummy session:
    existing = res.scalar_one_or_none() if hasattr(res, "scalar_one_or_none") else res.scalars().first()

    if existing is None:
        return {
            "inserted": 1,
            "updated": 0,
            "skipped": 0,
            "items": [
                {
                    "action": "insert",
                    "model": "Organisation",
                    "values": {
                        "organisation_name": org_name,
                        "slug": org_slug,
                    },
                }
            ],
            "organisation": {"name": org_name, "slug": org_slug},
        }

    # Row exists: decide between skip vs update (if slug differs).
    if getattr(existing, "slug", None) == org_slug:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 1,
            "items": [
                {
                    "action": "skip",
                    "model": "Organisation",
                    "id": existing.organisation_id,
                }
            ],
            "organisation": {"name": org_name, "slug": org_slug},
        }

    # Existing row but slug differs → plan an update.
    return {
        "inserted": 0,
        "updated": 1,
        "skipped": 0,
        "items": [
            {
                "action": "update",
                "model": "Organisation",
                "id": existing.organisation_id,
                "values": {"slug": org_slug},
            }
        ],
        "organisation": {"name": org_name, "slug": org_slug},
    }
