from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from datetime import time as dt_time

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import FinalGameStatus


class FinalGameScheduleBase(ORMBase):
    """
    Client-editable/business fields for a published, denormalized final game row.
    """

    run_id: int
    round_id: int
    age_id: int
    grade_id: int
    team_a_id: int
    team_b_id: int
    court_time_id: int

    game_date: dt_date
    game_name: str
    organisation_name: str
    competition_name: str
    season_name: str
    gender: str | None = None
    venue_name: str
    court_name: str
    start_time: dt_time
    age_name: str
    grade_name: str
    team_a_name: str
    team_b_name: str

    game_status: FinalGameStatus | None = FinalGameStatus.FINALISED

    # Publishing attribution (set by publishing workflow)
    published_at: datetime | None = None
    published_by_user_id: int


class FinalGameScheduleCreate(FinalGameScheduleBase):
    """
    Create payload for FinalGameSchedule.
    Service injects created_by_user_id from auth context.
    """

    pass


class FinalGameScheduleUpdate(ORMBase):
    """
    Partial update for FinalGameSchedule — all fields optional.
    Note: in most systems final schedules are append-only; use carefully.
    """

    run_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    team_a_id: int | None = None
    team_b_id: int | None = None
    court_time_id: int | None = None

    game_date: dt_date | None = None
    game_name: str | None = None
    organisation_name: str | None = None
    competition_name: str | None = None
    season_name: str | None = None
    gender: str | None = None
    venue_name: str | None = None
    court_name: str | None = None
    start_time: dt_time | None = None
    age_name: str | None = None
    grade_name: str | None = None
    team_a_name: str | None = None
    team_b_name: str | None = None

    game_status: FinalGameStatus | None = None
    published_at: datetime | None = None
    published_by_user_id: int | None = None


class FinalGameScheduleRead(FinalGameScheduleBase, CreatedStampedReadMixin):
    """
    Read payload for FinalGameSchedule (includes identifier, publishing, and audit fields).
    """

    final_game_schedule_id: int
