from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import GradeCourtRestrictionType


class GradeCourtRestrictionBase(ORMBase):
    """
    Client-editable/business fields for grade_court_restrictions.
    """

    round_setting_id: int
    grade_id: int
    court_time_id: int
    restriction_type: GradeCourtRestrictionType


class GradeCourtRestrictionCreate(GradeCourtRestrictionBase):
    """
    Create payload for GradeCourtRestriction.
    """

    pass


class GradeCourtRestrictionUpdate(ORMBase):
    """
    Partial update for GradeCourtRestriction — all fields optional.
    """

    round_setting_id: int | None = None
    grade_id: int | None = None
    court_time_id: int | None = None
    restriction_type: GradeCourtRestrictionType | None = None


class GradeCourtRestrictionRead(GradeCourtRestrictionBase, CreatedStampedReadMixin):
    """
    Read payload for GradeCourtRestriction (includes identifier and audit fields).
    """

    grade_court_restriction_id: int
