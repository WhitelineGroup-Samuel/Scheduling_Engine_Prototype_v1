from __future__ import annotations

from datetime import datetime

from app.schemas._base import ORMBase


class SchedulingLockBase(ORMBase):
    """
    Client-editable/business fields for an orchestration lock per season_day.
    """

    season_day_id: int
    run_id: int
    locked_by_user_id: int
    locked_at: datetime | None = None  # server default if omitted


class SchedulingLockCreate(SchedulingLockBase):
    """
    Create payload for SchedulingLock.
    """

    pass


class SchedulingLockUpdate(ORMBase):
    """
    Partial update for SchedulingLock — all fields optional.
    Typical flows will delete/unlock rather than update.
    """

    season_day_id: int | None = None
    run_id: int | None = None
    locked_by_user_id: int | None = None
    locked_at: datetime | None = None


class SchedulingLockRead(SchedulingLockBase):
    """
    Read payload for SchedulingLock (includes identifier).
    """

    lock_id: int
