# app/models/taxonomy/ages.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.system.season_days import SeasonDay
    from app.models.taxonomy.grades import Grade


class Age(CreatedStampedMixin, Base):
    """
    ERD TABLE: ages
    PURPOSE: Age bands configured per season_day (e.g., U10 Boys, Miniball Mixed).

    Columns (per ERD):
      - age_id SERIAL PK
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - age_code VARCHAR(20) NOT NULL
      - age_name TEXT NOT NULL
      - gender TEXT NULL
      - age_rank INTEGER NOT NULL
      - age_required_games INTEGER NULL
      - active BOOLEAN NULL DEFAULT TRUE
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (season_day_id, age_code) -> uq_ages_code
      - UNIQUE (season_day_id, age_name) -> uq_ages_name
      - UNIQUE (season_day_id, age_rank) -> uq_ages_rank
      - INDEX  (active)                  -> idx_ages_active
    """

    __tablename__ = "ages"

    age_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)

    age_code: Mapped[str] = mapped_column(String(20), nullable=False)
    age_name: Mapped[str] = mapped_column(Text, nullable=False)
    gender: Mapped[str | None] = mapped_column(Text)
    age_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    age_required_games: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    # created_at, created_by_user_id provided by CreatedStampedMixin

    __table_args__ = (
        UniqueConstraint("season_day_id", "age_code", name="uq_ages_code"),
        UniqueConstraint("season_day_id", "age_name", name="uq_ages_name"),
        UniqueConstraint("season_day_id", "age_rank", name="uq_ages_rank"),
        Index("idx_ages_active", "active"),
    )

    # Relationships
    season_day: Mapped[SeasonDay] = relationship("SeasonDay", back_populates="ages")
    grades: Mapped[list[Grade]] = relationship("Grade", back_populates="age", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [Age.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Age id={self.age_id} code={self.age_code!r}>"
