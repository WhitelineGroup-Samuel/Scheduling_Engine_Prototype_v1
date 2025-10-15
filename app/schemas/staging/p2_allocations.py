from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class P2AllocationBase(ORMBase):
    """
    Client-editable/business fields for a P2 allocation (age/grade -> court_time within a run/round).
    """

    run_id: int
    round_id: int
    age_id: int
    grade_id: int
    court_time_id: int


class P2AllocationCreate(P2AllocationBase):
    """
    Create payload for P2Allocation.
    Service injects created_by_user_id from auth context.
    """

    pass


class P2AllocationUpdate(ORMBase):
    """
    Partial update for P2Allocation — all fields optional.
    """

    run_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    court_time_id: int | None = None


class P2AllocationRead(P2AllocationBase, CreatedStampedReadMixin):
    """
    Read payload for P2Allocation (includes identifier and audit fields).
    """

    p2_allocation_id: int
