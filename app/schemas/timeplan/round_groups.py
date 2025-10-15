from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class RoundGroupBase(ORMBase):
    """
    Client-editable/business fields for linking a round to a round_setting.
    """

    round_id: int
    round_setting_id: int


class RoundGroupCreate(RoundGroupBase):
    """
    Create payload for RoundGroup.
    """

    pass


class RoundGroupUpdate(ORMBase):
    """
    Partial update for RoundGroup — all fields optional.
    """

    round_id: int | None = None
    round_setting_id: int | None = None


class RoundGroupRead(RoundGroupBase, CreatedStampedReadMixin):
    """
    Read payload for RoundGroup (includes identifier and audit).
    """

    round_group_id: int
