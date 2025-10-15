from __future__ import annotations

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase, UpdatedStampedReadMixin
from app.schemas.enums import AvailabilityStatus, LockState


class CourtTimeBase(ORMBase):
    """
    Client-editable fields for a concrete schedulable court-time cell.
    """

    season_day_id: int
    round_setting_id: int
    court_id: int
    time_slot_id: int
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    lock_state: LockState = LockState.OPEN
    block_reason: str | None = Field(default=None, description="Optional reason when unavailable/locked")


class CourtTimeCreate(CourtTimeBase):
    """
    Create payload for CourtTime.
    """

    pass


class CourtTimeUpdate(ORMBase):
    """
    Partial update for CourtTime — all fields optional.
    """

    season_day_id: int | None = None
    round_setting_id: int | None = None
    court_id: int | None = None
    time_slot_id: int | None = None
    availability_status: AvailabilityStatus | None = None
    lock_state: LockState | None = None
    block_reason: str | None = None


class CourtTimeRead(CourtTimeBase, CreatedStampedReadMixin, UpdatedStampedReadMixin):
    """
    Read payload for CourtTime (includes identifiers and audit fields).
    """

    court_time_id: int
