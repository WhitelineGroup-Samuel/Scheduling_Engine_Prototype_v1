from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class FinalByeScheduleRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for FinalByeSchedule rows (allocations/final_bye_schedule.py).

    When implementing:
    - Replace `model` with FinalByeSchedule.
    - Add list_for_run(run_id), list_for_round(round_id).
    - Add latest_published_for_season_day(season_day_id) if needed.
    """

    model: type[Any] = object  # TODO: set to FinalByeSchedule model class
