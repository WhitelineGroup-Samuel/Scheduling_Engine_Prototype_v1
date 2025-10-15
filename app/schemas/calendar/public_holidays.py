from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas._base import ORMBase

# Australian jurisdiction/region codes per ERD
HolidayRegion = Literal["CTH", "TAS", "VIC", "NSW", "ACT", "QLD", "SA", "NT", "WA"]


class PublicHolidayBase(ORMBase):
    """
    Client-editable/business fields for PublicHoliday.
    """

    date_id: int
    holiday_name: str = Field(min_length=1)
    holiday_region: HolidayRegion


class PublicHolidayCreate(PublicHolidayBase):
    """
    Create payload for PublicHoliday.
    """

    pass


class PublicHolidayUpdate(ORMBase):
    """
    Partial update payload for PublicHoliday.
    """

    date_id: int | None = None
    holiday_name: str | None = Field(default=None, min_length=1)
    holiday_region: HolidayRegion | None = None


class PublicHolidayRead(PublicHolidayBase):
    """
    Read payload for PublicHoliday (includes identifier).
    """

    public_holiday_id: int
