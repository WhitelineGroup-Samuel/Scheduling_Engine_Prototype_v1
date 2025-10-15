## app/schemas/calendar/default_times.py

from __future__ import annotations

from datetime import time as dt_time

from app.schemas._base import ORMBase


class DefaultTimeBase(ORMBase):
    """
    Client-editable/business fields for DefaultTime (time catalog).
    """

    time_value: dt_time


class DefaultTimeCreate(DefaultTimeBase):
    """
    Create payload for DefaultTime.
    """

    pass


class DefaultTimeUpdate(ORMBase):
    """
    Partial update payload for DefaultTime.
    """

    time_value: dt_time | None = None


class DefaultTimeRead(DefaultTimeBase):
    """
    Read payload for DefaultTime (includes identifier).
    """

    time_id: int
