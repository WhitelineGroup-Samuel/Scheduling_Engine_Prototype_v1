from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session
from tests.fixtures.calendar import SeasonWithDaysBundle

from app.repositories.system.season_day_repository import SeasonDayRepository


def test_season_day_list_for_season_and_sorting(
    db_session: Session,
    make_season_with_weekdays: Callable[..., SeasonWithDaysBundle],
) -> None:
    # Create three weekdays: WED(3), THU(4), FRI(5)
    bundle: SeasonWithDaysBundle = make_season_with_weekdays(3, 4, 5)
    season = bundle["season"]
    season_id = season.season_id

    repo = SeasonDayRepository(db_session)
    expected_total = len(bundle["season_days"])

    # 1) Basic list should come back ordered by week_day asc
    rows = repo.list_for_season(season_id)
    got_days = [r.week_day for r in rows]
    assert got_days == sorted(got_days)

    # 2) Sorted variant with sort=None should be identical (default is weekday asc)
    rows2 = repo.list_for_season_sorted(season_id, sort=None)
    got_days2 = [r.week_day for r in rows2]
    assert got_days2 == got_days

    # 3) Pagination: use the paged method
    page1_items, total = repo.list_for_season_sorted_paged(season_id, sort=None, page=1, per_page=2)
    assert len(page1_items) == 2
    assert total == expected_total

    page2_items, total2 = repo.list_for_season_sorted_paged(season_id, sort=None, page=2, per_page=2)
    # second page should have the remainder
    assert len(page2_items) == max(0, expected_total - 2)
    assert total2 == expected_total
