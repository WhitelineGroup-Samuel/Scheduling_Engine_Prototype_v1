from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class AgeRoundConstraintRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for AgeRoundConstraint rows (constraints/age_round_constraints.py).

    When implementing:
    - Replace `model` with AgeRoundConstraint.
    - Add list_for_age(age_id) and list_for_round(round_id).
    - Implement CRUD; return ORM models to services/DTOs.
    """

    model: type[Any] = object  # TODO: set to AgeRoundConstraint model class
