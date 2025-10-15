from __future__ import annotations

from datetime import time as dt_time
from typing import cast

from sqlalchemy import select

from app.models.calendar.default_times import DefaultTime
from app.repositories.base import BaseRepository
from app.repositories.typing import SelectStmt


class DefaultTimeRepository(BaseRepository[DefaultTime]):
    model = DefaultTime

    def get_by_value(self, t: dt_time) -> DefaultTime | None:
        stmt: SelectStmt = select(DefaultTime).where(DefaultTime.time_value == t)
        res = self.session.execute(stmt).scalar_one_or_none()
        return cast(DefaultTime | None, res)

    def ensure_time(self, t: dt_time) -> DefaultTime:
        """Return DefaultTime row for `t`, creating it if missing."""
        obj = self.get_by_value(t)
        if obj is not None:
            return obj
        obj = DefaultTime(time_value=t)
        self.session.add(obj)
        self.session.flush()
        return obj
