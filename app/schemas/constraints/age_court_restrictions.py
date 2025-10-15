from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase


class AgeCourtRestrictionBase(ORMBase):
    """
    Client-editable/business fields for age_court_restrictions.
    """

    round_setting_id: int
    age_id: int
    court_time_id: int


class AgeCourtRestrictionCreate(AgeCourtRestrictionBase):
    """
    Create payload for AgeCourtRestriction.
    """

    pass


class AgeCourtRestrictionUpdate(ORMBase):
    """
    Partial update for AgeCourtRestriction — all fields optional.
    """

    round_setting_id: int | None = None
    age_id: int | None = None
    court_time_id: int | None = None


class AgeCourtRestrictionRead(AgeCourtRestrictionBase, CreatedStampedReadMixin):
    """
    Read payload for AgeCourtRestriction (includes identifier and audit fields).
    """

    age_court_restriction_id: int
