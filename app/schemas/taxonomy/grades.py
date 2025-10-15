from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import Code20, NonEmptyStr, NonNegInt, PositiveInt


class GradeBase(ORMBase):
    """
    Client-editable fields for a competitive grade within an age.
    """

    age_id: int
    grade_code: Code20
    grade_name: NonEmptyStr
    grade_rank: PositiveInt
    grade_required_games: NonNegInt | None = None
    bye_requirement: bool | None = False
    active: bool | None = True
    display_colour: str | None = None  # keep free-text to match ERD (can later tighten to HexColour)


class GradeCreate(GradeBase):
    """
    Create payload for Grade.
    """

    pass


class GradeUpdate(ORMBase):
    """
    Partial update for Grade — all fields optional.
    """

    age_id: int | None = None
    grade_code: Code20 | None = None
    grade_name: NonEmptyStr | None = None
    grade_rank: PositiveInt | None = None
    grade_required_games: NonNegInt | None = None
    bye_requirement: bool | None = None
    active: bool | None = None
    display_colour: str | None = None


class GradeRead(GradeBase, CreatedStampedReadMixin):
    """
    Read payload for Grade (includes identifier and audit fields).
    """

    grade_id: int
