from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class PublicHolidayRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for PublicHoliday rows (calendar/public_holidays.py).

    When implementing:
    - Replace `model` with PublicHoliday.
    - Implement CRUD; return ORM models.
    """

    model: type[Any] = object  # TODO: set to PublicHoliday model class
