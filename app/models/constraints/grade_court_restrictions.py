from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class GradeCourtRestriction(CreatedStampedMixin, Base):
    """
    ERD TABLE: grade_court_restrictions
    PURPOSE: Grade-level or dual restrictions for specific court_time under a round_setting.

    Columns:
      - grade_court_restriction_id SERIAL PK
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - court_time_id INTEGER NOT NULL FK -> court_times(court_time_id)
      - restriction_type TEXT NOT NULL  // CHECK: 'GRADE','DUAL'
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (round_setting_id, grade_id, court_time_id) -> uq_grade_court_restrictions_key
      - INDEX  (round_setting_id, grade_id, court_time_id) -> idx_grade_court_restrictions_keys
    """

    __tablename__ = "grade_court_restrictions"

    grade_court_restriction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    court_time_id: Mapped[int] = mapped_column(ForeignKey("court_times.court_time_id"), nullable=False)

    restriction_type: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "round_setting_id",
            "grade_id",
            "court_time_id",
            name="uq_grade_court_restrictions_key",
        ),
        Index(
            "idx_grade_court_restrictions_keys",
            "round_setting_id",
            "grade_id",
            "court_time_id",
        ),
        CheckConstraint(
            "restriction_type IN ('GRADE','DUAL')",
            name="chk_grade_court_restrictions_type",
        ),
    )

    # Relationships
    round_setting = relationship("RoundSetting")
    grade = relationship("Grade")
    court_time = relationship("CourtTime")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [GradeCourtRestriction.created_by_user_id])

    def __repr__(self) -> str:
        return (
            f"<GradeCourtRestriction id={self.grade_court_restriction_id} "
            f"round_setting_id={self.round_setting_id} grade_id={self.grade_id} "
            f"court_time_id={self.court_time_id} type={self.restriction_type!r}>"
        )
