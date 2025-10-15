## app/repositories/timeplan/time_slot_repository.py

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, datetime
from datetime import time as dt_time
from typing import Any

from sqlalchemy import select

from app.models.timeplan.time_slots import TimeSlot
from app.repositories.base import BaseRepository
from app.repositories.calendar.default_time_repository import DefaultTimeRepository
from app.repositories.mixins import OrderingMixin, SeasonDayScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class TimeSlotRepository(BaseRepository[TimeSlot], SeasonDayScopedMixin, OrderingMixin):
    """
    Data access for TimeSlot rows.

    Scopes:
    - where_season_day(stmt, season_day_id)

    Helpers:
    - list_for_season_day(season_day_id): ordered by start_time ASC, then PK
    - list_ordered(): generic ordered list with optional filters
    """

    model = TimeSlot

    # ---- SeasonDayScopedMixin contract ----
    def season_day_id_column(self) -> Any:
        return TimeSlot.season_day_id

    # ---- Queries ----
    def list_for_season_day(self, season_day_id: int) -> list[TimeSlot]:
        stmt: SelectStmt = select(TimeSlot)
        stmt = self.where_season_day(stmt, season_day_id)
        stmt = self.order_by(
            stmt,
            TimeSlot.start_time.asc(),
            TimeSlot.time_slot_id.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[TimeSlot]:
        stmt: SelectStmt = select(TimeSlot)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(
            stmt,
            TimeSlot.start_time.asc(),
            TimeSlot.time_slot_id.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_day_sorted(
        self,
        season_day_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[TimeSlot]:
        """
        Sorted list of time slots for a season day.
        Allowed sort keys: 'start' (start_time), 'end' (end_time), 'created'.
        Default: start ASC, PK tiebreaker is handled by BaseRepository.
        """
        stmt: SelectStmt = select(TimeSlot).where(TimeSlot.season_day_id == season_day_id)

        allowed: Mapping[str, Any] = {
            "start": TimeSlot.start_time,
            "end": TimeSlot.end_time,
            "created": TimeSlot.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=TimeSlot.start_time,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_day_sorted_paged(
        self,
        season_day_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[TimeSlot], int]:
        """
        Sorted + paginated list of time slots for a season day.
        Returns (items, total).
        """
        stmt: SelectStmt = select(TimeSlot).where(TimeSlot.season_day_id == season_day_id)

        allowed: Mapping[str, Any] = {
            "start": TimeSlot.start_time,
            "end": TimeSlot.end_time,
            "created": TimeSlot.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=TimeSlot.start_time,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def _ensure_default_time_id(self, t: dt_time) -> int:
        """Resolve or create a DefaultTime row for `t` and return its time_id."""
        repo = DefaultTimeRepository(self.session)
        obj = repo.ensure_time(t)
        return int(obj.time_id)

    @staticmethod
    def _minutes_between(start: dt_time, end: dt_time) -> int:
        """Return the positive number of minutes between two same-day times."""
        s = datetime.combine(date(2000, 1, 1), start)
        e = datetime.combine(date(2000, 1, 1), end)
        delta = e - s
        return max(0, int(delta.total_seconds() // 60))

    def create(self, values: dict[str, Any]) -> TimeSlot:
        vals = dict(values)

        # Resolve start/end time IDs from the provided dt_time values (on demand)
        st: dt_time | None = vals.get("start_time")
        et: dt_time | None = vals.get("end_time")

        if vals.get("start_time_id") is None and isinstance(st, dt_time):
            vals["start_time_id"] = self._ensure_default_time_id(st)
        if vals.get("end_time_id") is None and isinstance(et, dt_time):
            vals["end_time_id"] = self._ensure_default_time_id(et)

        # Derive duration if missing and both times are present
        if not vals.get("duration_minutes") and isinstance(st, dt_time) and isinstance(et, dt_time):
            # If you want to support wrapping past midnight, adjust here.
            mins = self._minutes_between(st, et)
            vals["duration_minutes"] = mins if mins > 0 else 1  # enforce >= 1

        # Derive a label if missing
        if not vals.get("time_slot_label") and isinstance(st, dt_time) and isinstance(et, dt_time):
            vals["time_slot_label"] = f"{st.strftime('%H:%M')}–{et.strftime('%H:%M')}"
        if not vals.get("time_slot_label"):
            vals["time_slot_label"] = "Time Slot"

        return super().create(vals)
