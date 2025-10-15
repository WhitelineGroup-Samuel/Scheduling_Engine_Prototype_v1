# app/models/venues/venues.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
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
    from app.models.venues.courts import Court


class Venue(CreatedStampedMixin, Base):
    """
    ERD: TABLE: venues
    PURPOSE: Physical sites hosting courts; maintains a live count of courts.

    Columns:
      - venue_id SERIAL PK
      - organisation_id INTEGER NOT NULL FK -> organisations(organisation_id)
      - venue_name TEXT NOT NULL
      - venue_address TEXT NOT NULL
      - display_order INTEGER NOT NULL
      - latitude NUMERIC(9,6) NULL
      - longitude NUMERIC(9,6) NULL
      - indoor BOOLEAN NULL DEFAULT TRUE
      - accessible BOOLEAN NULL DEFAULT TRUE
      - total_courts INTEGER NOT NULL
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (venue_name, venue_address)  -> uq_venues_name_address
      - INDEX  (created_by_user_id)         -> idx_venues_created_by
    """

    __tablename__ = "venues"

    venue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organisation_id: Mapped[int] = mapped_column(ForeignKey("organisations.organisation_id"), nullable=False)
    venue_name: Mapped[str] = mapped_column(Text, nullable=False)
    venue_address: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    indoor: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    accessible: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    total_courts: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("venue_name", "venue_address", name="uq_venues_name_address"),
        Index("idx_venues_created_by", "created_by_user_id"),
    )

    # Relationships
    courts: Mapped[list[Court]] = relationship("Court", back_populates="venue", cascade="all, delete-orphan")

    # Attribution relationships
    created_by = relationship("UserAccount", foreign_keys=lambda: [Venue.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Venue id={self.venue_id} name={self.venue_name!r}>"
