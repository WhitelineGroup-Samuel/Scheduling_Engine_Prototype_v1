## app/schemas/timeplan/time_slots.py

from __future__ import annotations

from datetime import time as dt_time

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import NonNegInt, PositiveInt


class TimeSlotBase(ORMBase):
    """
    Client-editable/business fields for a time window on a season day.
    Includes both normalized refs (start/end time ids) and denormalized times.
    """

    season_day_id: int
    start_time_id: int
    end_time_id: int
    start_time: dt_time
    end_time: dt_time
    time_slot_label: str = Field(min_length=1)
    buffer_minutes: NonNegInt  # non-negative
    duration_minutes: PositiveInt  # at least 1 minute


class TimeSlotCreate(TimeSlotBase):
    """
    Create payload for TimeSlot.
    """

    pass


class TimeSlotUpdate(ORMBase):
    """
    Partial update for TimeSlot — all fields optional.
    """

    season_day_id: int | None = None
    start_time_id: int | None = None
    end_time_id: int | None = None
    start_time: dt_time | None = None
    end_time: dt_time | None = None
    time_slot_label: str | None = Field(default=None, min_length=1)
    buffer_minutes: NonNegInt | None = None
    duration_minutes: PositiveInt | None = None


class TimeSlotRead(TimeSlotBase, CreatedStampedReadMixin):
    """
    Read payload for TimeSlot (includes identifier and audit).
    """

    time_slot_id: int
