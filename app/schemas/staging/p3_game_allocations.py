from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class P3GameAllocationBase(ORMBase):
    """
    Client-editable/business fields for a P3 game allocation (team pairings on a slot).
    """

    run_id: int
    p2_allocation_id: int | None = None
    round_id: int
    age_id: int
    grade_id: int
    team_a_id: int
    team_b_id: int
    court_time_id: int


class P3GameAllocationCreate(P3GameAllocationBase):
    """
    Create payload for P3GameAllocation.
    """

    pass


class P3GameAllocationUpdate(ORMBase):
    """
    Partial update for P3GameAllocation — all fields optional.
    """

    run_id: int | None = None
    p2_allocation_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    team_a_id: int | None = None
    team_b_id: int | None = None
    court_time_id: int | None = None


class P3GameAllocationRead(P3GameAllocationBase, CreatedStampedReadMixin):
    """
    Read payload for P3GameAllocation (includes identifier and audit fields).
    """

    p3_game_allocation_id: int
