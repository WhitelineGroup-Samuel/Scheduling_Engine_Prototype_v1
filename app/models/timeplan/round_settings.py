# app/models/timeplan/round_settings.py

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.system.season_days import SeasonDay
    from app.models.timeplan.round_groups import RoundGroup


class RoundSetting(CreatedStampedMixin, Base):
    """
    ERD TABLE: round_settings
    PURPOSE: Configuration bundle per season_day and setting number.

    Columns:
      - round_setting_id SERIAL PK
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - round_settings_number INTEGER NOT NULL
      - rules JSONB NULL
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (season_day_id, round_settings_number) -> uq_round_settings_day_number
      - INDEX  (season_day_id)                        -> idx_round_settings_day
    """

    __tablename__ = "round_settings"

    round_setting_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)
    round_settings_number: Mapped[int] = mapped_column(Integer, nullable=False)
    rules: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint(
            "season_day_id",
            "round_settings_number",
            name="uq_round_settings_day_number",
        ),
        Index("idx_round_settings_day", "season_day_id"),
    )

    # Relationships
    season_day: Mapped[SeasonDay] = relationship("SeasonDay")
    round_groups: Mapped[list[RoundGroup]] = relationship("RoundGroup", back_populates="round_setting", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [RoundSetting.created_by_user_id])

    def __repr__(self) -> str:
        return f"<RoundSetting id={self.round_setting_id} season_day_id={self.season_day_id} number={self.round_settings_number}>"
