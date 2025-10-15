from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class AgeRoundConstraintBase(ORMBase):
    """
    Client-editable/business fields for age_round_constraints.
    """

    round_setting_id: int
    age_id: int
    active: bool | None = True


class AgeRoundConstraintCreate(AgeRoundConstraintBase):
    """
    Create payload for AgeRoundConstraint.
    """

    pass


class AgeRoundConstraintUpdate(ORMBase):
    """
    Partial update for AgeRoundConstraint — all fields optional.
    """

    round_setting_id: int | None = None
    age_id: int | None = None
    active: bool | None = None


class AgeRoundConstraintRead(AgeRoundConstraintBase, CreatedStampedReadMixin):
    """
    Read payload for AgeRoundConstraint (includes identifier and audit fields).
    """

    age_round_constraint_id: int
