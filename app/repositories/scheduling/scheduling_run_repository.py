from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class SchedulingRunRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for SchedulingRun rows (scheduling/scheduling_runs.py).

    When implementing:
    - Replace `model` with SchedulingRun.
    - Add create_run, update_status, set_metrics, set_error_details helpers.
    - Add list_for_season_day(season_day_id) and get_active_for_season_day(...).
    """

    model: type[Any] = object  # TODO: set to SchedulingRun model class
