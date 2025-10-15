from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class CourtRankingRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for CourtRanking rows (venues/court_rankings.py in models).

    When implementing:
    - Replace `model` with the actual ORM class (CourtRanking).
    - Add list helpers (e.g., list_for_venue_court), ordered by rank.
    - Add CRUD as needed; return ORM models (DTOs in service layer).
    - Use asc(cast(Any, Model).field) for stable ordering (Pylance-friendly).
    """

    model: type[Any] = object  # TODO: set to CourtRanking model class
