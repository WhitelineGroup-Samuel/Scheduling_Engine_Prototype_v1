from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class GradeRoundConstraint(CreatedStampedMixin, Base):
    """
    ERD TABLE: grade_round_constraints
    PURPOSE: Declares which grades are in-scope for a given round_setting (age carried for convenience).

    Columns:
      - grade_round_constraint_id SERIAL PK
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - active BOOLEAN NULL DEFAULT TRUE
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (round_setting_id, grade_id)               -> uq_grade_round_constraints_key
      - INDEX  (round_setting_id, grade_id)               -> idx_grade_round_constraints_keys
    """

    __tablename__ = "grade_round_constraints"

    grade_round_constraint_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)

    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))

    __table_args__ = (
        UniqueConstraint("round_setting_id", "grade_id", name="uq_grade_round_constraints_key"),
        Index("idx_grade_round_constraints_keys", "round_setting_id", "grade_id"),
    )

    # Relationships
    round_setting = relationship("RoundSetting")
    age = relationship("Age")
    grade = relationship("Grade")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [GradeRoundConstraint.created_by_user_id])

    def __repr__(self) -> str:
        return (
            f"<GradeRoundConstraint id={self.grade_round_constraint_id} "
            f"round_setting_id={self.round_setting_id} grade_id={self.grade_id} active={self.active}>"
        )
