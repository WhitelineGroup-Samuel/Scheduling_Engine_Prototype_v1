"""Integration tests covering deterministic database seed routines."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.seed import OrganisationSeed, SeedPlan, seed_from_plan, seed_minimal
from app.repositories.organisation_repository import OrganisationRepository

pytestmark = pytest.mark.integration


def test_seed_minimal_idempotent(db_session: Session) -> None:
    """Applying the minimal seed twice should not create duplicates."""

    organisation_name = "Acme FC"
    first_result = seed_minimal(db_session, org_name=organisation_name)
    assert first_result["inserted"] >= 1
    assert first_result["updated"] == 0
    second_result = seed_minimal(db_session, org_name=organisation_name)
    assert second_result["inserted"] == 0
    assert second_result["updated"] == 0
    assert second_result["skipped"] >= 1


def test_seed_minimal_dry_run_matches_apply(db_session: Session) -> None:
    """A dry-run should report the same actions as an actual apply."""

    repository = OrganisationRepository()
    organisation_name = "Acme FC Dry Run"
    plan = SeedPlan(organisations=(OrganisationSeed(name=organisation_name),))

    dry_run_summary: set[tuple[str | None, str | None]] = set()
    dry_run_transaction = db_session.begin_nested()
    try:
        dry_run_result = seed_from_plan(db_session, plan)
        assert dry_run_result["inserted"] == 1
        dry_run_summary = {
            (item.get("name"), item.get("slug")) for item in dry_run_result["items"]
        }
    finally:
        dry_run_transaction.rollback()

    assert repository.get_by_name(db_session, organisation_name) is None

    apply_result = seed_from_plan(db_session, plan)
    assert apply_result["inserted"] == 1
    apply_summary = {
        (item.get("name"), item.get("slug")) for item in apply_result["items"]
    }
    assert dry_run_summary == apply_summary

    repeat_result = seed_from_plan(db_session, plan)
    assert repeat_result["inserted"] == 0
    assert repeat_result["skipped"] >= 1


def test_seed_minimal_duplicate_name_raises(db_session: Session) -> None:
    """Direct repository usage should raise when attempting duplicate inserts."""

    repository = OrganisationRepository()
    name = "Seed Duplicate"
    repository.create(db_session, name=name)
    with pytest.raises(IntegrityError):
        repository.create(db_session, name=name)
    db_session.rollback()
