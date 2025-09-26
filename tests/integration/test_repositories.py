"""Repository integration tests exercising transactional behaviour."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.core import Organisation
from app.repositories.base_repository import BaseRepository
from app.repositories.organisation_repository import OrganisationRepository

pytestmark = pytest.mark.integration


def test_base_repository_session_lifecycle(db_session: Session) -> None:
    """BaseRepository should reuse the provided session without closing it."""

    repository = BaseRepository(db_session)
    session = repository.require_session(None)
    assert session is db_session
    result = session.execute(text("select 1"))
    assert result.scalar_one() == 1
    assert session.is_active


def test_organisation_repository_roundtrip(db_session: Session) -> None:
    """Round-trip an organisation using the concrete repository implementation."""

    repository = OrganisationRepository()
    unique_suffix = uuid.uuid4().hex[:8]
    name = f"Integration Club {unique_suffix}"
    created = repository.create(db_session, name=name)
    assert isinstance(created, Organisation)
    assert created.organisation_id is not None
    assert created.organisation_name == name
    assert created.slug
    assert created.created_at is not None
    assert created.updated_at is not None
    assert created.created_at.tzinfo is not None
    assert created.updated_at.tzinfo is not None

    fetched_by_id = repository.get_by_id(db_session, created.organisation_id)
    assert fetched_by_id is not None
    assert fetched_by_id.organisation_id == created.organisation_id

    fetched_by_name = repository.get_by_name(db_session, name)
    assert fetched_by_name is not None
    assert fetched_by_name.organisation_id == created.organisation_id

    fetched_by_slug = repository.get_by_slug(db_session, created.slug)
    assert fetched_by_slug is not None
    assert fetched_by_slug.organisation_id == created.organisation_id


def test_organisation_repository_duplicate_name_raises(
    db_session: Session,
) -> None:
    """Attempting to insert the same organisation twice should raise an error."""

    repository = OrganisationRepository()
    name = "Duplicate Integration Club"
    first = repository.create(db_session, name=name)
    assert first.organisation_id is not None
    with pytest.raises(IntegrityError):
        repository.create(db_session, name=name)
    db_session.rollback()
