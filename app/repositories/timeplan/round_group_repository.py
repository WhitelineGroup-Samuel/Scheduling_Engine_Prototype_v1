from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class RoundGroupRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for RoundGroup rows (timeplan/round_groups.py in models).

    When implementing:
    - Replace `model` with the actual ORM class (RoundGroup).
    - Add list_for_season_day(season_day_id) or list_for_round(round_id).
    - Order by display_order/name for stable UI lists.
    - Implement CRUD as needed; return ORM models.
    """

    model: type[Any] = object  # TODO: set to RoundGroup model class
