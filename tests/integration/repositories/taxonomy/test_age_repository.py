from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session
from tests.fixtures.calendar import SeasonWithDaysBundle

from app.models.taxonomy.ages import Age
from app.repositories.taxonomy.age_repository import AgeRepository
from app.schemas._base import SortQuery


def test_age_repository_scopes_sorting_paging(
    db_session: Session,
    make_season_with_weekdays: Callable[..., SeasonWithDaysBundle],
) -> None:
    age_repo = AgeRepository(db_session)

    # Get a Season + one or more SeasonDay rows (pick any weekday 1..7)
    bundle = make_season_with_weekdays(2)  # MONDAY
    sd = bundle["season_days"][0]

    # Create ages deliberately out of rank order (and two with same rank to see name tiebreak)
    _a1 = age_repo.create({"season_day_id": sd.season_day_id, "age_name": "U13", "age_rank": 3})
    _a2 = age_repo.create({"season_day_id": sd.season_day_id, "age_name": "U11", "age_rank": 1})
    _a3 = age_repo.create({"season_day_id": sd.season_day_id, "age_name": "U15", "age_rank": 4})
    _a4 = age_repo.create({"season_day_id": sd.season_day_id, "age_name": "U12", "age_rank": 2})

    # list_for_season_day: ordered by age_rank ASC then age_name ASC
    rows: list[Age] = age_repo.list_for_season_day(sd.season_day_id)
    assert [r.age_name for r in rows] == ["U11", "U12", "U13", "U15"]

    # list_ordered restricted via WHERE
    ordered_filtered: list[Age] = age_repo.list_ordered(where=(Age.season_day_id == sd.season_day_id,))
    assert [r.age_name for r in ordered_filtered] == ["U11", "U12", "U13", "U15"]

    # list_for_season_day_sorted: use 'name' → alphabetical with stable tiebreak
    by_name: list[Age] = age_repo.list_for_season_day_sorted(sd.season_day_id, sort=SortQuery(order_by="name", direction="asc"))
    assert [r.age_name for r in by_name] == ["U11", "U12", "U13", "U15"]

    # list_for_season_day_sorted_paged
    page1, total = age_repo.list_for_season_day_sorted_paged(
        sd.season_day_id,
        sort=SortQuery(order_by="rank", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = age_repo.list_for_season_day_sorted_paged(
        sd.season_day_id,
        sort=SortQuery(order_by="rank", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 4 and total2 == 4
    assert [r.age_name for r in page1] == ["U11", "U12"]
    assert [r.age_name for r in page2] == ["U13", "U15"]
