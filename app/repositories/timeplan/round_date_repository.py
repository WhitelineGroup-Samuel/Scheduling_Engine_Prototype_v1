from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class RoundDateRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for RoundDate rows (timeplan/round_dates.py in models).

    When implementing:
    - Replace `model` with the actual ORM class (RoundDate).
    - Add list_for_round(round_id) and list_for_season_day(season_day_id).
    - Order by date_id (or game_date) then PK.
    - Implement CRUD as needed; return ORM models.
    """

    model: type[Any] = object  # TODO: set to RoundDate model class
