from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class CourtTimeRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for CourtTime rows (venues/court_times.py in models).

    When implementing:
    - Replace `model` with the actual ORM class (CourtTime).
    - Add list helpers (e.g., list_for_court, list_for_venue).
    - Order by start_time then PK for deterministic results.
    - Implement CRUD as needed; return ORM models.
    """

    model: type[Any] = object  # TODO: set to CourtTime model class
