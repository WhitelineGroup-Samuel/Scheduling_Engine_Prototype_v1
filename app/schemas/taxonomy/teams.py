from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import Code20, NonEmptyStr


class TeamBase(ORMBase):
    """
    Client-editable fields for a team registered in a grade.
    """

    grade_id: int
    team_code: Code20
    team_name: NonEmptyStr | None = None
    active: bool | None = True


class TeamCreate(TeamBase):
    """
    Create payload for Team.
    """

    pass


class TeamUpdate(ORMBase):
    """
    Partial update for Team — all fields optional.
    """

    grade_id: int | None = None
    team_code: Code20 | None = None
    team_name: NonEmptyStr | None = None
    active: bool | None = None


class TeamRead(TeamBase, CreatedStampedReadMixin):
    """
    Read payload for Team (includes identifier and audit fields).
    """

    team_id: int
