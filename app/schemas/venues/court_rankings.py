from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase, UpdatedStampedReadMixin
from app.schemas.types import NonNegInt


class CourtRankingBase(ORMBase):
    """
    Client-editable fields for a court ranking entry.
    """

    court_id: int
    season_day_id: int
    round_setting_id: int
    court_rank: NonNegInt
    overridden: bool | None = False


class CourtRankingCreate(CourtRankingBase):
    """
    Create payload for CourtRanking.
    """

    pass


class CourtRankingUpdate(ORMBase):
    """
    Partial update for CourtRanking — all fields optional.
    """

    court_id: int | None = None
    season_day_id: int | None = None
    round_setting_id: int | None = None
    court_rank: NonNegInt | None = None
    overridden: bool | None = None


class CourtRankingRead(CourtRankingBase, CreatedStampedReadMixin, UpdatedStampedReadMixin):
    """
    Read payload for CourtRanking (includes identifiers and audit fields).
    """

    court_rank_id: int
