from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class AgeCourtRestrictionRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for AgeCourtRestriction rows (constraints/age_court_restrictions.py).

    When implementing:
    - Replace `model` with AgeCourtRestriction.
    - Add list_for_age(age_id), list_for_venue(venue_id), list_for_court(court_id).
    - Implement CRUD; return ORM models.
    """

    model: type[Any] = object  # TODO: set to AgeCourtRestriction model class
