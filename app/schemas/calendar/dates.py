# app/schemas/calendar/dates.py

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field

from app.schemas._base import ORMBase

# Weekday literal (aligns with ERD: 'MONDAY'..'SUNDAY')
WeekdayLiteral = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


class DateBase(ORMBase):
    """
    Client-editable/business fields for a Date dimension row.
    """

    date_value: date
    date_day: WeekdayLiteral
    calendar_year: int = Field(ge=1)
    iso_week_int: int = Field(ge=1, le=53)
    is_weekend: bool
    is_public_holiday: bool


class DateCreate(DateBase):
    """
    Create payload for Date.
    Note: Primary key is DB-generated; no audit fields in ERD.
    """

    pass


class DateUpdate(ORMBase):
    """
    Partial update payload for Date (all fields optional).
    Use exclude_unset=True in service layer to apply changes.
    """

    date_value: date | None = None
    date_day: WeekdayLiteral | None = None
    calendar_year: int | None = Field(default=None, ge=1)
    iso_week_int: int | None = Field(default=None, ge=1, le=53)
    is_weekend: bool | None = None
    is_public_holiday: bool | None = None


class DateRead(DateBase):
    """
    Read payload for Date (includes identifier).
    """

    date_id: int
