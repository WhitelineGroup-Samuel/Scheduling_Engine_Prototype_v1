from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class RoundDateBase(ORMBase):
    """
    Client-editable/business fields for binding a date to a round.
    """

    round_id: int
    date_id: int


class RoundDateCreate(RoundDateBase):
    """
    Create payload for RoundDate.
    """

    pass


class RoundDateUpdate(ORMBase):
    """
    Partial update for RoundDate — all fields optional.
    """

    round_id: int | None = None
    date_id: int | None = None


class RoundDateRead(RoundDateBase, CreatedStampedReadMixin):
    """
    Read payload for RoundDate (includes identifier and audit).
    """

    round_date_id: int
