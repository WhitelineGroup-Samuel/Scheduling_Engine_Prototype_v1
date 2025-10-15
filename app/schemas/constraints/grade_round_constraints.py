from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class GradeRoundConstraintBase(ORMBase):
    """
    Client-editable/business fields for grade_round_constraints.
    """

    round_setting_id: int
    age_id: int
    grade_id: int
    active: bool | None = True


class GradeRoundConstraintCreate(GradeRoundConstraintBase):
    """
    Create payload for GradeRoundConstraint.
    """

    pass


class GradeRoundConstraintUpdate(ORMBase):
    """
    Partial update for GradeRoundConstraint — all fields optional.
    """

    round_setting_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    active: bool | None = None


class GradeRoundConstraintRead(GradeRoundConstraintBase, CreatedStampedReadMixin):
    """
    Read payload for GradeRoundConstraint (includes identifier and audit fields).
    """

    grade_round_constraint_id: int
