## tests/integration/repositories/timeplan/test_time_slot_repository.py

from __future__ import annotations

from collections.abc import Callable
from datetime import time

from sqlalchemy.orm import Session
from tests.fixtures.calendar import SeasonWithDaysBundle

from app.models.timeplan.time_slots import TimeSlot
from app.repositories.timeplan.time_slot_repository import TimeSlotRepository
from app.schemas._base import SortQuery


def test_time_slot_repository_scopes_sorting_paging(
    db_session: Session,
    make_season_with_weekdays: Callable[..., SeasonWithDaysBundle],
) -> None:
    ts_repo = TimeSlotRepository(db_session)

    # Get Season + SeasonDay from the fixture
    bundle = make_season_with_weekdays(5)  # FRIDAY
    sd = bundle["season_days"][0]

    t_b = ts_repo.create(
        {
            "season_day_id": sd.season_day_id,
            "start_time": time(10, 0),
            "end_time": time(10, 45),
            "buffer_minutes": 5,
        }
    )
    t_a = ts_repo.create(
        {
            "season_day_id": sd.season_day_id,
            "start_time": time(9, 0),
            "end_time": time(9, 45),
            "buffer_minutes": 10,
        }
    )
    t_c = ts_repo.create(
        {
            "season_day_id": sd.season_day_id,
            "start_time": time(11, 0),
            "end_time": time(11, 45),
            "buffer_minutes": 15,
        }
    )

    # list_for_season_day → start_time ASC (then PK)
    rows: list[TimeSlot] = ts_repo.list_for_season_day(sd.season_day_id)
    assert [r.start_time for r in rows] == [time(9, 0), time(10, 0), time(11, 0)]

    # list_ordered with WHERE filter
    rows2: list[TimeSlot] = ts_repo.list_ordered(where=(TimeSlot.season_day_id == sd.season_day_id,))
    assert [r.time_slot_id for r in rows2] == [
        t_a.time_slot_id,
        t_b.time_slot_id,
        t_c.time_slot_id,
    ]

    # list_for_season_day_sorted (default / explicit "start")
    by_default: list[TimeSlot] = ts_repo.list_for_season_day_sorted(sd.season_day_id, sort=None)
    by_start: list[TimeSlot] = ts_repo.list_for_season_day_sorted(sd.season_day_id, sort=SortQuery(order_by="start", direction="asc"))
    assert [r.start_time for r in by_default] == [time(9, 0), time(10, 0), time(11, 0)]
    assert [r.start_time for r in by_start] == [time(9, 0), time(10, 0), time(11, 0)]

    # list_for_season_day_sorted_paged
    page1, total = ts_repo.list_for_season_day_sorted_paged(
        sd.season_day_id,
        sort=SortQuery(order_by="start", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = ts_repo.list_for_season_day_sorted_paged(
        sd.season_day_id,
        sort=SortQuery(order_by="start", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [r.start_time for r in page1] == [time(9, 0), time(10, 0)]
    assert [r.start_time for r in page2] == [time(11, 0)]
