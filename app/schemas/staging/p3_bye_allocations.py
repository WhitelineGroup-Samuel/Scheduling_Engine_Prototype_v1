from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import ByeReason


class P3ByeAllocationBase(ORMBase):
    """
    Client-editable/business fields for a P3 bye allocation.
    """

    run_id: int
    round_id: int
    age_id: int
    grade_id: int
    team_id: int
    bye_reason: ByeReason


class P3ByeAllocationCreate(P3ByeAllocationBase):
    """
    Create payload for P3ByeAllocation.
    """

    pass


class P3ByeAllocationUpdate(ORMBase):
    """
    Partial update for P3ByeAllocation — all fields optional.
    """

    run_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    team_id: int | None = None
    bye_reason: ByeReason | None = None


class P3ByeAllocationRead(P3ByeAllocationBase, CreatedStampedReadMixin):
    """
    Read payload for P3ByeAllocation (includes identifier and audit fields).
    """

    p3_bye_allocation_id: int
