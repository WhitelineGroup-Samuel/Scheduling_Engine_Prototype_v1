from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class AgeCourtRestriction(CreatedStampedMixin, Base):
    """
    ERD TABLE: age_court_restrictions
    PURPOSE: Forbid or explicitly scope Age to specific court_time under a round_setting.

    Columns:
      - age_court_restriction_id SERIAL PK
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - court_time_id INTEGER NOT NULL FK -> court_times(court_time_id)
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (round_setting_id, age_id, court_time_id) -> uq_age_court_restrictions_key
      - INDEX  (round_setting_id, age_id, court_time_id) -> idx_age_court_restrictions_keys
    """

    __tablename__ = "age_court_restrictions"

    age_court_restriction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    court_time_id: Mapped[int] = mapped_column(ForeignKey("court_times.court_time_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "round_setting_id",
            "age_id",
            "court_time_id",
            name="uq_age_court_restrictions_key",
        ),
        Index(
            "idx_age_court_restrictions_keys",
            "round_setting_id",
            "age_id",
            "court_time_id",
        ),
    )

    # Relationships
    round_setting = relationship("RoundSetting")
    age = relationship("Age")
    court_time = relationship("CourtTime")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [AgeCourtRestriction.created_by_user_id])

    def __repr__(self) -> str:
        return (
            f"<AgeCourtRestriction id={self.age_court_restriction_id} "
            f"round_setting_id={self.round_setting_id} age_id={self.age_id} court_time_id={self.court_time_id}>"
        )
