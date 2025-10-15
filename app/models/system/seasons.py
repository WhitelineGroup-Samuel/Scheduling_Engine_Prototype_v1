# app/models/system/seasons.py

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD includes created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.system.season_days import SeasonDay


class Season(CreatedStampedMixin, Base):
    """
    ERD TABLE: seasons
    PURPOSE: Season window within a competition, with visibility and activation flags.
    Columns per ERD:
      - season_id SERIAL PK
      - competition_id INTEGER NOT NULL FK -> competitions(competition_id)
      - season_name TEXT NOT NULL
      - starting_date DATE NULLABLE
      - ending_date DATE NULLABLE
      - visibility TEXT NOT NULL  // 'PRIVATE' | 'INTERNAL' | 'PUBLIC'
      - active BOOLEAN NULLABLE DEFAULT TRUE
      - created_at TIMESTAMPTZ NULLABLE DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - slug VARCHAR(64) NOT NULL
    AKs:
      - UNIQUE (competition_id, season_name)
      - UNIQUE (competition_id, slug)
    Indexes:
      - idx_seasons_comp (competition_id)
      - idx_seasons_visibility_active (visibility, active)
      - idx_seasons_created_by (created_by_user_id)
    """

    __tablename__ = "seasons"

    season_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.competition_id"), nullable=False)
    season_name: Mapped[str] = mapped_column(Text, nullable=False)
    starting_date: Mapped[date | None] = mapped_column(Date)
    ending_date: Mapped[date | None] = mapped_column(Date)
    visibility: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    # created_at, created_by_user_id provided by CreatedStampedMixin
    slug: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("competition_id", "season_name", name="uq_seasons_competition_name"),
        UniqueConstraint("competition_id", "slug", name="uq_seasons_comp_slug"),
        Index("idx_seasons_comp", "competition_id"),
        Index("idx_seasons_visibility_active", "visibility", "active"),
        Index("idx_seasons_created_by", "created_by_user_id"),
    )

    # Relationships
    competition = relationship("Competition", back_populates="seasons")
    season_days: Mapped[list[SeasonDay]] = relationship("SeasonDay", back_populates="season", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [Season.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Season id={self.season_id} name={self.season_name!r} slug={self.slug!r}>"
