from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class SchedulingLockRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for SchedulingLock rows (scheduling/scheduling_locks.py).

    When implementing:
    - Replace `model` with SchedulingLock.
    - Add acquire_lock(season_day_id, owner), release_lock(...), get_lock(...).
    - Consider DB uniqueness/index on season_day_id for single-owner semantics.
    """

    model: type[Any] = object  # TODO: set to SchedulingLock model class
