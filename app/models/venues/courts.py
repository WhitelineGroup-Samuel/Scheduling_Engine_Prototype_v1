# app/models/venues/courts.py

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
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id present
)

if TYPE_CHECKING:
    from app.models.venues.court_rankings import CourtRanking
    from app.models.venues.court_times import CourtTime
    from app.models.venues.venues import Venue


class Court(CreatedStampedMixin, Base):
    """
    ERD: TABLE: courts
    PURPOSE: Individual playing areas at a venue.

    Columns:
      - court_id SERIAL PK
      - venue_id INTEGER NOT NULL FK -> venues(venue_id)
      - court_code VARCHAR(20) NOT NULL
      - court_name TEXT NOT NULL
      - display_order INTEGER NOT NULL
      - surface TEXT NULL
      - indoor BOOLEAN NULL DEFAULT TRUE
      - active BOOLEAN NULL DEFAULT TRUE
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (venue_id, court_code)     -> uq_courts_venue_code
      - UNIQUE (venue_id, court_name)     -> uq_courts_venue_name
      - UNIQUE (venue_id, display_order)  -> uq_courts_venue_display
      - INDEX  (venue_id)                 -> idx_courts_venue
      - INDEX  (active)                   -> idx_courts_active
    """

    __tablename__ = "courts"

    court_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.venue_id"), nullable=False)
    court_code: Mapped[str] = mapped_column(String(20), nullable=False)
    court_name: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    surface: Mapped[str | None] = mapped_column(Text)
    indoor: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))

    __table_args__ = (
        UniqueConstraint("venue_id", "court_code", name="uq_courts_venue_code"),
        UniqueConstraint("venue_id", "court_name", name="uq_courts_venue_name"),
        UniqueConstraint("venue_id", "display_order", name="uq_courts_venue_display"),
        Index("idx_courts_venue", "venue_id"),
        Index("idx_courts_active", "active"),
    )

    # Relationships
    venue: Mapped[Venue] = relationship("Venue", back_populates="courts")
    court_times: Mapped[list[CourtTime]] = relationship("CourtTime", back_populates="court")
    court_rankings: Mapped[list[CourtRanking]] = relationship("CourtRanking", back_populates="court")

    # Attribution relationships
    created_by = relationship("UserAccount", foreign_keys=lambda: [Court.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Court id={self.court_id} code={self.court_code!r}>"
