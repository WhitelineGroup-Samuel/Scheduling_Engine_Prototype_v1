from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (  # ERD includes both created_* and updated_*
    CreatedStampedMixin,
    UpdatedStampedMixin,
)

if TYPE_CHECKING:
    from app.models.system.season_days import SeasonDay
    from app.models.timeplan.round_settings import RoundSetting
    from app.models.venues.courts import Court


class CourtRanking(CreatedStampedMixin, UpdatedStampedMixin, Base):
    """
    ERD: TABLE: court_rankings
    PURPOSE: Preferred court order per (season_day, round_setting) and court.

    Columns:
      - court_rank_id SERIAL PK
      - court_id INTEGER NOT NULL FK -> courts(court_id)
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - court_rank INTEGER NOT NULL
      - overridden BOOLEAN NULL DEFAULT FALSE
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - updated_at TIMESTAMPTZ NULL
      - updated_by_user_id INTEGER NULL FK -> users(user_account_id)

    Notes:
      - No AK defined in ERD; historical rows can exist with overridden=TRUE.
    """

    __tablename__ = "court_rankings"

    court_rank_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.court_id"), nullable=False)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)
    court_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    overridden: Mapped[bool | None] = mapped_column(Boolean, server_default=text("FALSE"))

    # Relationships
    court: Mapped[Court] = relationship("Court", back_populates="court_rankings")
    season_day: Mapped[SeasonDay] = relationship("SeasonDay")
    round_setting: Mapped[RoundSetting] = relationship("RoundSetting")

    # Attribution relationships
    created_by = relationship("UserAccount", foreign_keys=lambda: [CourtRanking.created_by_user_id])
    updated_by = relationship("UserAccount", foreign_keys=lambda: [CourtRanking.updated_by_user_id])

    def __repr__(self) -> str:
        return f"<CourtRanking id={self.court_rank_id} court_id={self.court_id} rank={self.court_rank}>"
