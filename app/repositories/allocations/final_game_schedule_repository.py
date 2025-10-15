from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class FinalGameScheduleRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for FinalGameSchedule rows (allocations/final_game_schedule.py).

    When implementing:
    - Replace `model` with FinalGameSchedule.
    - Add list_for_run(run_id), list_for_round(round_id).
    - Add latest_published_for_season_day(season_day_id) if needed.
    """

    model: type[Any] = object  # TODO: set to FinalGameSchedule model class
