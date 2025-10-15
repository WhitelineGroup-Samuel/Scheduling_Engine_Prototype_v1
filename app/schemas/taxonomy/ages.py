from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import Code20, NonEmptyStr, NonNegInt, PositiveInt


class AgeBase(ORMBase):
    """
    Client-editable fields for an age band configured per season_day.
    """

    season_day_id: int
    age_code: Code20
    age_name: NonEmptyStr
    gender: str | None = None
    age_rank: PositiveInt  # rank order within the season_day
    age_required_games: NonNegInt | None = None
    active: bool | None = True


class AgeCreate(AgeBase):
    """
    Create payload for Age.
    `created_by_user_id` is injected by the service layer from the current user.
    """

    pass


class AgeUpdate(ORMBase):
    """
    Partial update for Age — all fields optional.
    """

    season_day_id: int | None = None
    age_code: Code20 | None = None
    age_name: NonEmptyStr | None = None
    gender: str | None = None
    age_rank: PositiveInt | None = None
    age_required_games: NonNegInt | None = None
    active: bool | None = None


class AgeRead(AgeBase, CreatedStampedReadMixin):
    """
    Read payload for Age (includes identifier and audit fields).
    """

    age_id: int
