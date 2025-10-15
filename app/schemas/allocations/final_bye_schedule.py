from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import ByeReason


class FinalByeScheduleBase(ORMBase):
    """
    Client-editable/business fields for a published, denormalized final bye row.
    """

    run_id: int
    round_id: int
    age_id: int
    grade_id: int
    team_id: int

    bye_date: dt_date
    bye_name: str
    organisation_name: str
    competition_name: str
    season_name: str
    gender: str | None = None
    age_name: str
    grade_name: str
    team_name: str
    bye_reason: ByeReason

    # Publishing attribution (set by publishing workflow)
    published_at: datetime | None = None
    published_by_user_id: int


class FinalByeScheduleCreate(FinalByeScheduleBase):
    """
    Create payload for FinalByeSchedule.
    Service injects created_by_user_id from auth context.
    """

    pass


class FinalByeScheduleUpdate(ORMBase):
    """
    Partial update for FinalByeSchedule — all fields optional.
    """

    run_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    team_id: int | None = None

    bye_date: dt_date | None = None
    bye_name: str | None = None
    organisation_name: str | None = None
    competition_name: str | None = None
    season_name: str | None = None
    gender: str | None = None
    age_name: str | None = None
    grade_name: str | None = None
    team_name: str | None = None
    bye_reason: ByeReason | None = None

    published_at: datetime | None = None
    published_by_user_id: int | None = None


class FinalByeScheduleRead(FinalByeScheduleBase, CreatedStampedReadMixin):
    """
    Read payload for FinalByeSchedule (includes identifier, publishing, and audit fields).
    """

    final_bye_schedule_id: int
