from __future__ import annotations

from typing import Any, cast

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cli.seed_data import (
    _plan_seed,  # type: ignore[attr-defined]  # private helper, intentional
)
from app.models.system.organisations import Organisation
from app.repositories.system.organisation_repository import OrganisationRepository


def test_seed_plan_then_apply_org(db_session: Session) -> None:
    """
    Plan seeding for an Organisation, apply it, then confirm idempotency.

    Flow:
      1) Plan (dry-run): expect 1 insert.
      2) Apply: create Organisation using the plan's values.
      3) Plan again: expect a skip (no changes needed).
    """
    org_name = "Demo Org"

    # --- 1) PLAN (dry-run) ---------------------------------------------------
    summary1: dict[str, Any] = _plan_seed(db_session, org_name)
    assert summary1["inserted"] == 1
    assert summary1["updated"] == 0
    assert summary1["skipped"] == 0
    assert isinstance(summary1.get("items"), list)
    assert summary1["organisation"]["name"] == org_name
    # slug normalized to seed expectations (e.g., "demo-org")
    planned_slug = cast(str, summary1["organisation"]["slug"])
    assert planned_slug and planned_slug == "demo-org"

    # --- 2) APPLY -------------------------------------------------------------
    repo = OrganisationRepository(db_session)
    created = repo.create({"organisation_name": org_name, "slug": planned_slug})
    assert created.organisation_id is not None

    # Verify persisted values via a SELECT (no repo convenience needed)
    row = db_session.execute(select(Organisation).where(Organisation.organisation_id == created.organisation_id).limit(1)).scalars().first()
    assert row is not None
    assert row.organisation_name == org_name
    assert row.slug == planned_slug

    # --- 3) PLAN AGAIN (idempotency) -----------------------------------------
    summary2: dict[str, Any] = _plan_seed(db_session, org_name)
    # Now that the org exists with the expected values, planner should skip
    assert summary2["inserted"] == 0
    assert summary2["updated"] == 0
    assert summary2["skipped"] == 1
    assert isinstance(summary2.get("items"), list)
    # Optional: ensure the skip references the same id
    # (planner returns string or int id in 'id' depending on impl)
    skip_items = [it for it in summary2["items"] if it.get("action") == "skip"]
    assert skip_items, "Expected at least one 'skip' item"
    # No strict assertion on id equality to avoid coupling to planner internals.


@pytest.mark.skip(reason="Extend when seed branches handle competition/season/day.")
def test_seed_scaffold_competition_season_day(db_session: Session) -> None:
    """
    Placeholder for extended seeding:
      - org → competition → season → season_day
      - verify summary shows inserted counts for each level
      - re-run to verify idempotent summary (skips)
    """
    # When you add those seed branches, this test should:
    #  1) plan full scaffold
    #  2) apply scaffold
    #  3) re-plan and assert all 'skip'
    pass
