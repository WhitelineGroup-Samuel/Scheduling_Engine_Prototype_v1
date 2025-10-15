from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import RoundStatus, RoundType


class RoundBase(ORMBase):
    """
    Client-editable/business fields for a round.
    """

    round_number: int = Field(ge=1)
    round_label: str = Field(min_length=1)
    round_type: RoundType
    round_status: RoundStatus = RoundStatus.PLANNED


class RoundCreate(RoundBase):
    """
    Create payload for Round.
    Requires the parent season.
    """

    season_id: int


class RoundUpdate(ORMBase):
    """
    Partial update for Round — all fields optional.
    """

    round_number: int | None = Field(default=None, ge=1)
    round_label: str | None = Field(default=None, min_length=1)
    round_type: RoundType | None = None
    round_status: RoundStatus | None = None
    published_at: datetime | None = None


class RoundRead(RoundBase, CreatedStampedReadMixin):
    """
    Read payload for Round (includes identifiers and audit).
    """

    round_id: int
    season_id: int
    published_at: datetime | None = None
