from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class AllocationSettingRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for AllocationSetting rows (constraints/allocation_settings.py).

    When implementing:
    - Replace `model` with AllocationSetting.
    - Add get_for_season_day(season_day_id) and/or get_for_season(season_id).
    - Implement CRUD; map integrity errors via BaseRepository.
    """

    model: type[Any] = object  # TODO: set to AllocationSetting model class
