from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin, UpdatedStampedMixin


class AllocationSetting(CreatedStampedMixin, UpdatedStampedMixin, Base):
    """
    ERD TABLE: allocation_settings
    PURPOSE: Restriction flags at (round_setting, age, grade) granularity.

    Columns:
      - allocation_setting_id SERIAL PK
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - restricted BOOLEAN NULL DEFAULT FALSE
      - restriction_type TEXT NOT NULL DEFAULT 'NONE'  // CHECK: 'NONE','AGE','GRADE','DUAL'
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - updated_at TIMESTAMPTZ NULL
      - updated_by_user_id INTEGER NULL FK -> users(user_account_id)

    Notes:
      - No alternate keys in ERD; multiples for a tuple are allowed.
      - No indexes defined in ERD.
    """

    __tablename__ = "allocation_settings"

    allocation_setting_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)

    restricted: Mapped[bool | None] = mapped_column(Boolean, server_default=text("FALSE"))
    restriction_type: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'NONE'"))

    __table_args__ = (
        CheckConstraint(
            "restriction_type IN ('NONE','AGE','GRADE','DUAL')",
            name="chk_allocation_settings_restriction_type",
        ),
    )

    # Relationships
    round_setting = relationship("RoundSetting")
    age = relationship("Age")
    grade = relationship("Grade")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [AllocationSetting.created_by_user_id])
    updated_by = relationship("UserAccount", foreign_keys=lambda: [AllocationSetting.updated_by_user_id])

    def __repr__(self) -> str:
        return (
            f"<AllocationSetting id={self.allocation_setting_id} "
            f"round_setting_id={self.round_setting_id} age_id={self.age_id} grade_id={self.grade_id} "
            f"restricted={self.restricted} type={self.restriction_type!r}>"
        )
