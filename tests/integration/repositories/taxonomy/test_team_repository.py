from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session
from tests.fixtures.calendar import SeasonWithDaysBundle

from app.models.taxonomy.teams import Team
from app.repositories.taxonomy.age_repository import AgeRepository
from app.repositories.taxonomy.grade_repository import GradeRepository
from app.repositories.taxonomy.team_repository import TeamRepository
from app.schemas._base import SortQuery


def test_team_repository_scopes_sorting_paging(
    db_session: Session,
    make_season_with_weekdays: Callable[..., SeasonWithDaysBundle],
) -> None:
    age_repo = AgeRepository(db_session)
    grade_repo = GradeRepository(db_session)
    team_repo = TeamRepository(db_session)

    # Get Season + SeasonDay → build age/grade under it
    bundle = make_season_with_weekdays(4)  # THURSDAY
    sd = bundle["season_days"][0]
    age = age_repo.create({"season_day_id": sd.season_day_id, "age_name": "U13", "age_rank": 1})
    grade = grade_repo.create({"age_id": age.age_id, "grade_name": "A Grade", "grade_rank": 1})

    # Create teams deliberately unsorted by code/name
    _t1 = team_repo.create({"grade_id": grade.grade_id, "team_code": "T02", "team_name": "Zebras"})
    _t2 = team_repo.create({"grade_id": grade.grade_id, "team_code": "T01", "team_name": "Alphas"})
    t3 = team_repo.create({"grade_id": grade.grade_id, "team_code": "T03", "team_name": "Bruins"})

    # list_for_grade: ordered by team_code ASC then team_name ASC
    rows: list[Team] = team_repo.list_for_grade(grade.grade_id)
    assert [r.team_code for r in rows] == ["T01", "T02", "T03"]

    # get_by_code_in_grade convenience
    got = team_repo.get_by_code_in_grade(grade.grade_id, "T03")
    assert got is not None and got.team_id == t3.team_id

    # list_ordered with WHERE filter
    ordered_filtered: list[Team] = team_repo.list_ordered(where=(Team.grade_id == grade.grade_id,))
    assert [r.team_code for r in ordered_filtered] == ["T01", "T02", "T03"]

    # list_for_grade_sorted with sort='name'
    by_name: list[Team] = team_repo.list_for_grade_sorted(grade.grade_id, sort=SortQuery(order_by="name", direction="asc"))
    assert [r.team_name for r in by_name] == ["Alphas", "Bruins", "Zebras"]

    # list_for_grade_sorted_paged
    page1, total = team_repo.list_for_grade_sorted_paged(
        grade.grade_id,
        sort=SortQuery(order_by="code", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = team_repo.list_for_grade_sorted_paged(
        grade.grade_id,
        sort=SortQuery(order_by="code", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [r.team_code for r in page1] == ["T01", "T02"]
    assert [r.team_code for r in page2] == ["T03"]
