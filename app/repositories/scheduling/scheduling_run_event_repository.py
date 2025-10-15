from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class SchedulingRunEventRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for SchedulingRunEvent rows (scheduling/scheduling_run_events.py).

    When implementing:
    - Replace `model` with SchedulingRunEvent.
    - Add append_event(run_id, stage, severity, message), list_for_run(run_id).
    - Order by created_at ascending for chronological logs.
    """

    model: type[Any] = object  # TODO: set to SchedulingRunEvent model class
