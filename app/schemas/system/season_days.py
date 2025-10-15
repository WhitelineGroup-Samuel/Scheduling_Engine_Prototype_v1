from __future__ import annotations

from datetime import time
from typing import Literal

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase

# Optional weekday literals for stronger client typing.
WeekdayLiteral = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


class SeasonDayBase(ORMBase):
    """Shared, user-editable fields for a season day."""

    season_day_name: WeekdayLiteral
    season_day_label: str | None = None
    week_day: int = Field(ge=1, le=7)  # 1..7 as per ERD
    window_start: time
    window_end: time
    active: bool | None = False


class SeasonDayCreate(SeasonDayBase):
    """
    Create payload.
    Requires the parent season id.
    """

    season_id: int


class SeasonDayUpdate(ORMBase):
    """Partial update — all fields optional."""

    season_day_name: WeekdayLiteral | None = None
    season_day_label: str | None = None
    week_day: int | None = Field(default=None, ge=1, le=7)
    window_start: time | None = None
    window_end: time | None = None
    active: bool | None = None


class SeasonDayRead(SeasonDayBase, CreatedStampedReadMixin):
    """Read payload with identifiers and audit fields."""

    season_day_id: int
    season_id: int
