from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class GradeRoundConstraintRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for GradeRoundConstraint rows (constraints/grade_round_constraints.py).

    When implementing:
    - Replace `model` with GradeRoundConstraint.
    - Add list_for_grade(grade_id) and list_for_round(round_id).
    - Implement CRUD; return ORM models.
    """

    model: type[Any] = object  # TODO: set to GradeRoundConstraint model class
