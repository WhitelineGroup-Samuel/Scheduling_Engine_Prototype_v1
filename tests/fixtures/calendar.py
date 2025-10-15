# tests/fixtures/calendar.py
from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from datetime import time as _time
from typing import TYPE_CHECKING, TypedDict

import pytest
from sqlalchemy.orm import Session

from app.models.calendar.dates import Date
from app.repositories.calendar.date_repository import DateRepository
from app.repositories.system.competition_repository import CompetitionRepository
from app.repositories.system.organisation_repository import OrganisationRepository
from app.repositories.system.season_day_repository import SeasonDayRepository
from app.repositories.system.season_repository import SeasonRepository

if TYPE_CHECKING:
    from app.models.system.competitions import Competition
    from app.models.system.organisations import Organisation
    from app.models.system.season_days import SeasonDay
    from app.models.system.seasons import Season


class SeasonWithDaysBundle(TypedDict):
    organisation: Organisation
    competition: Competition
    season: Season
    dates: list[Date]
    season_days: list[SeasonDay]


_WEEKDAY_NAME = {
    1: "MONDAY",
    2: "TUESDAY",
    3: "WEDNESDAY",
    4: "THURSDAY",
    5: "FRIDAY",
    6: "SATURDAY",
    7: "SUNDAY",
}


@pytest.fixture
def ensure_calendar_dates(db_session: Session) -> Callable[..., list[Date]]:
    """
    Factory fixture: ensure_calendar_dates(*dates) -> [Date, ...]
    Ensures each given Python date has a corresponding row in 'dates',
    creating it if missing, and returns the Date rows.
    """

    def _ensure(*date_values: dt.date) -> list[Date]:
        repo = DateRepository(db_session)
        rows: list[Date] = [repo.get_or_create_by_value(dv) for dv in date_values]
        db_session.flush()
        return rows

    return _ensure


@pytest.fixture
def make_season_with_weekdays(
    db_session: Session,
) -> Callable[..., SeasonWithDaysBundle]:
    """
    Factory fixture:
        make_season_with_weekdays(*weekdays, org_name=..., comp_name=..., season_name=..., visibility="public")
    Creates Organisation -> Competition -> Season, then creates SeasonDay rows for the given weekdays (1..7).
    """

    def _make(
        *weekdays: int,
        org_name: str = "Fixture Org",
        comp_name: str = "Fixture Comp",
        season_name: str = "Fixture Season",
        visibility: str = "public",
        window_start: _time = _time(8, 0),
        window_end: _time = _time(22, 0),
        active: bool = True,
    ) -> SeasonWithDaysBundle:
        if not weekdays:
            weekdays = (3,)  # default WEDNESDAY if none provided

        # 1) Minimal org -> comp -> season chain
        org_repo = OrganisationRepository(db_session)
        comp_repo = CompetitionRepository(db_session)
        season_repo = SeasonRepository(db_session)

        org = org_repo.create({"organisation_name": org_name})
        comp = comp_repo.create(
            {
                "competition_name": comp_name,
                "organisation_id": org.organisation_id,
            }
        )
        season = season_repo.create(
            {
                "season_name": season_name,
                "competition_id": comp.competition_id,
                "visibility": visibility,
            }
        )

        # 2) Create SeasonDay rows for the requested weekdays
        sd_repo = SeasonDayRepository(db_session)
        season_days: list[SeasonDay] = []
        for w in dict.fromkeys(weekdays):  # de-dupe while preserving order
            season_days.append(
                sd_repo.create(
                    {
                        "season_id": season.season_id,
                        "season_day_name": _WEEKDAY_NAME[w],
                        "week_day": w,
                        "window_start": window_start,
                        "window_end": window_end,
                        "active": active,
                    }
                )
            )
        db_session.flush()

        return {
            "organisation": org,
            "competition": comp,
            "season": season,
            "dates": [],  # kept for bundle shape compatibility
            "season_days": season_days,
        }

    return _make
