# app/models/timeplan/rounds.py

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
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
    from app.models.system.seasons import Season
    from app.models.timeplan.round_dates import RoundDate
    from app.models.timeplan.round_groups import RoundGroup


class Round(CreatedStampedMixin, Base):
    """
    ERD TABLE: rounds
    PURPOSE: Logical round markers for a season (grading, regular, finals).

    Columns:
      - round_id SERIAL PK
      - season_id INTEGER NOT NULL FK -> seasons(season_id)
      - round_number INTEGER NOT NULL
      - round_label TEXT NOT NULL
      - round_type TEXT NOT NULL         // 'GRADING','REGULAR','FINALS'
      - round_status TEXT NOT NULL       // 'PLANNED','SCHEDULED','PUBLISHED','COMPLETED','CANCELLED' (default: 'PLANNED')
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - published_at TIMESTAMPTZ NULL

    AKs:
      - UNIQUE (season_id, round_number)
      - UNIQUE (season_id, round_label)
    """

    __tablename__ = "rounds"

    round_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.season_id"), nullable=False)

    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    round_label: Mapped[str] = mapped_column(Text, nullable=False)
    round_type: Mapped[str] = mapped_column(Text, nullable=False)
    round_status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'PLANNED'"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("season_id", "round_number", name="uq_rounds_season_number"),
        UniqueConstraint("season_id", "round_label", name="uq_rounds_season_label"),
        CheckConstraint(
            "round_type IN ('GRADING','REGULAR','FINALS')",
            name="chk_rounds_round_type",
        ),
        CheckConstraint(
            "round_status IN ('PLANNED','SCHEDULED','PUBLISHED','COMPLETED','CANCELLED')",
            name="chk_rounds_round_status",
        ),
    )

    # Relationships
    season: Mapped[Season] = relationship("Season")
    round_groups: Mapped[list[RoundGroup]] = relationship("RoundGroup", back_populates="round", cascade="all, delete-orphan")
    round_dates: Mapped[list[RoundDate]] = relationship("RoundDate", back_populates="round", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [Round.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Round id={self.round_id} season_id={self.season_id} number={self.round_number} type={self.round_type!r}>"
