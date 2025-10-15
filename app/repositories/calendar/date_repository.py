# app/repositories/calendar/date_repository.py
from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select

from app.models.calendar.dates import Date
from app.repositories.base import BaseRepository

_WEEKDAY_NAMES = [
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
]


class DateRepository(BaseRepository[Date]):
    model = Date

    def get_by_value(self, value: date) -> Date | None:
        stmt = select(Date).where(Date.date_value == value)
        res: Date | None = self.session.execute(stmt).scalars().first()
        return res

    def get_or_create_by_value(self, value: date) -> Date:
        existing = self.get_by_value(value)
        if existing:
            return existing
        payload = self._build_payload(value)
        return super().create(payload)

    @staticmethod
    def _build_payload(value: date) -> dict[str, Any]:
        iso = value.isocalendar()  # has .week in py3.12
        weekday_idx = value.weekday()  # Monday=0..Sunday=6
        return {
            "date_value": value,
            "date_day": _WEEKDAY_NAMES[weekday_idx],
            "calendar_year": value.year,
            "iso_week_int": iso.week,
            "is_weekend": weekday_idx >= 5,
            "is_public_holiday": False,
        }
