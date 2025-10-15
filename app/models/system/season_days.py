# app/models/system/season_days.py

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD includes created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.taxonomy.ages import Age


class SeasonDay(CreatedStampedMixin, Base):
    """
    ERD TABLE: season_days
    PURPOSE: Per-season weekday configuration, label, and time window.
    Columns per ERD:
      - season_day_id SERIAL PK
      - season_id INTEGER NOT NULL FK -> seasons(season_id)
      - season_day_name TEXT NOT NULL  // MONDAY..SUNDAY
      - season_day_label TEXT NULLABLE
      - week_day INTEGER NOT NULL      // 1..7
      - window_start TIME NOT NULL
      - window_end TIME NOT NULL
      - active BOOLEAN NULLABLE DEFAULT FALSE
      - created_at TIMESTAMPTZ NULLABLE DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
    AKs:
      - UNIQUE (season_id, season_day_name)
      - UNIQUE (season_id, week_day)
    Indexes:
      - idx_season_days_season (season_id)
      - idx_season_days_week_day (week_day)
      - idx_season_days_active (active)
    """

    __tablename__ = "season_days"

    season_day_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.season_id"), nullable=False)
    season_day_name: Mapped[str] = mapped_column(Text, nullable=False)
    season_day_label: Mapped[str | None] = mapped_column(Text)
    week_day: Mapped[int] = mapped_column(Integer, nullable=False)
    window_start: Mapped[time] = mapped_column(Time, nullable=False)
    window_end: Mapped[time] = mapped_column(Time, nullable=False)
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("FALSE"))
    # created_at, created_by_user_id provided by CreatedStampedMixin

    __table_args__ = (
        UniqueConstraint("season_id", "season_day_name", name="uq_season_days_name"),
        UniqueConstraint("season_id", "week_day", name="uq_season_days_weekday"),
        Index("idx_season_days_season", "season_id"),
        Index("idx_season_days_week_day", "week_day"),
        Index("idx_season_days_active", "active"),
        CheckConstraint("week_day BETWEEN 1 AND 7", name="chk_season_days_week_day_range"),
    )

    # Relationships
    season = relationship("Season", back_populates="season_days")
    ages: Mapped[list[Age]] = relationship("Age", back_populates="season_day", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [SeasonDay.created_by_user_id])

    def __repr__(self) -> str:
        return f"<SeasonDay id={self.season_day_id} name={self.season_day_name!r} week_day={self.week_day}>"
