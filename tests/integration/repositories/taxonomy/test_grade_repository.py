from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session
from tests.fixtures.calendar import SeasonWithDaysBundle

from app.models.taxonomy.grades import Grade
from app.repositories.taxonomy.age_repository import AgeRepository
from app.repositories.taxonomy.grade_repository import GradeRepository
from app.schemas._base import SortQuery


def test_grade_repository_scopes_sorting_paging(
    db_session: Session,
    make_season_with_weekdays: Callable[..., SeasonWithDaysBundle],
) -> None:
    age_repo = AgeRepository(db_session)
    grade_repo = GradeRepository(db_session)

    # Get a Season + SeasonDay, then build age/grades beneath it
    bundle = make_season_with_weekdays(3)  # WEDNESDAY
    sd = bundle["season_days"][0]
    age = age_repo.create({"season_day_id": sd.season_day_id, "age_name": "U13", "age_rank": 1})

    # Create grades out of rank/name order
    g1 = grade_repo.create({"age_id": age.age_id, "grade_name": "B Grade", "grade_rank": 2})
    _g2 = grade_repo.create({"age_id": age.age_id, "grade_name": "A Grade", "grade_rank": 1})
    _g3 = grade_repo.create({"age_id": age.age_id, "grade_name": "C Grade", "grade_rank": 3})

    # list_for_age_ordered: rank ASC then grade_name
    rows: list[Grade] = grade_repo.list_for_age_ordered(age.age_id)
    assert [r.grade_name for r in rows] == ["A Grade", "B Grade", "C Grade"]

    # get_by_name_in_age convenience
    got = grade_repo.get_by_name_in_age(age.age_id, "B Grade")
    assert got is not None and got.grade_id == g1.grade_id

    # list_ordered with WHERE filter
    ordered_filtered: list[Grade] = grade_repo.list_ordered(where=(Grade.age_id == age.age_id,))
    assert [r.grade_name for r in ordered_filtered] == ["A Grade", "B Grade", "C Grade"]

    # list_for_age_sorted with sort='name'
    by_name: list[Grade] = grade_repo.list_for_age_sorted(age.age_id, sort=SortQuery(order_by="name", direction="asc"))
    assert [r.grade_name for r in by_name] == ["A Grade", "B Grade", "C Grade"]

    # list_for_age_sorted_paged
    page1, total = grade_repo.list_for_age_sorted_paged(age.age_id, sort=SortQuery(order_by="rank", direction="asc"), page=1, per_page=2)
    page2, total2 = grade_repo.list_for_age_sorted_paged(age.age_id, sort=SortQuery(order_by="rank", direction="asc"), page=2, per_page=2)
    assert total == 3 and total2 == 3
    assert [r.grade_name for r in page1] == ["A Grade", "B Grade"]
    assert [r.grade_name for r in page2] == ["C Grade"]
