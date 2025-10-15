from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session
from tests.fixtures.calendar import SeasonWithDaysBundle

from app.models.timeplan.round_settings import RoundSetting
from app.repositories.timeplan.round_setting_repository import RoundSettingRepository
from app.schemas._base import SortQuery


def test_round_setting_repository_scopes_sorting_paging(
    db_session: Session,
    make_season_with_weekdays: Callable[..., SeasonWithDaysBundle],
) -> None:
    rs_repo = RoundSettingRepository(db_session)

    # Get Season + SeasonDay directly from fixture
    bundle = make_season_with_weekdays(1)  # MONDAY
    sd = bundle["season_days"][0]

    rs1 = rs_repo.create({"season_day_id": sd.season_day_id, "round_settings_number": 2})
    rs2 = rs_repo.create({"season_day_id": sd.season_day_id, "round_settings_number": 1})
    rs3 = rs_repo.create({"season_day_id": sd.season_day_id, "round_settings_number": 3})

    # list_for_season_day → PK ascending
    rows: list[RoundSetting] = rs_repo.list_for_season_day(sd.season_day_id)
    assert [r.round_setting_id for r in rows] == [
        rs1.round_setting_id,
        rs2.round_setting_id,
        rs3.round_setting_id,
    ]

    # list_ordered with WHERE filter
    rows2: list[RoundSetting] = rs_repo.list_ordered(where=(RoundSetting.season_day_id == sd.season_day_id,))
    assert [r.round_setting_id for r in rows2] == [
        rs1.round_setting_id,
        rs2.round_setting_id,
        rs3.round_setting_id,
    ]

    # list_for_season_day_sorted (default / explicit "id")
    by_default: list[RoundSetting] = rs_repo.list_for_season_day_sorted(sd.season_day_id, sort=None)
    by_id: list[RoundSetting] = rs_repo.list_for_season_day_sorted(sd.season_day_id, sort=SortQuery(order_by="id", direction="asc"))
    assert [r.round_setting_id for r in by_default] == [
        rs1.round_setting_id,
        rs2.round_setting_id,
        rs3.round_setting_id,
    ]
    assert [r.round_setting_id for r in by_id] == [
        rs1.round_setting_id,
        rs2.round_setting_id,
        rs3.round_setting_id,
    ]

    # list_for_season_day_sorted_paged
    page1, total = rs_repo.list_for_season_day_sorted_paged(
        sd.season_day_id,
        sort=SortQuery(order_by="id", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = rs_repo.list_for_season_day_sorted_paged(
        sd.season_day_id,
        sort=SortQuery(order_by="id", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [r.round_setting_id for r in page1] == [
        rs1.round_setting_id,
        rs2.round_setting_id,
    ]
    assert [r.round_setting_id for r in page2] == [rs3.round_setting_id]
