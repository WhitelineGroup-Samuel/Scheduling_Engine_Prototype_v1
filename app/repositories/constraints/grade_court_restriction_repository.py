from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class GradeCourtRestrictionRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for GradeCourtRestriction rows (constraints/grade_court_restrictions.py).

    When implementing:
    - Replace `model` with GradeCourtRestriction.
    - Add list_for_grade(grade_id), list_for_venue(venue_id), list_for_court(court_id).
    - Implement CRUD; return ORM models.
    """

    model: type[Any] = object  # TODO: set to GradeCourtRestriction model class
