# app/models/system/competitions.py

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
    CreatedStampedMixin,  # ERD includes created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.system.seasons import Season


class Competition(CreatedStampedMixin, Base):
    """
    ERD TABLE: competitions
    PURPOSE: Competition/program within an organisation.
    Columns per ERD:
      - competition_id SERIAL PK
      - organisation_id INTEGER NOT NULL FK -> organisations(organisation_id)
      - competition_name TEXT NOT NULL
      - active BOOLEAN NULLABLE DEFAULT TRUE
      - created_at TIMESTAMPTZ NULLABLE DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - slug VARCHAR(64) NOT NULL
    AKs:
      - UNIQUE (organisation_id, competition_name)
      - UNIQUE (organisation_id, slug)
    Indexes:
      - idx_competitions_org (organisation_id)
      - idx_competitions_created_by (created_by_user_id)
    """

    __tablename__ = "competitions"

    competition_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organisation_id: Mapped[int] = mapped_column(ForeignKey("organisations.organisation_id"), nullable=False)
    competition_name: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    # created_at, created_by_user_id provided by CreatedStampedMixin
    slug: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("organisation_id", "competition_name", name="uq_competitions_org_name"),
        UniqueConstraint("organisation_id", "slug", name="uq_competitions_org_slug"),
        Index("idx_competitions_org", "organisation_id"),
        Index("idx_competitions_created_by", "created_by_user_id"),
    )

    # Relationships
    organisation = relationship("Organisation", back_populates="competitions")
    seasons: Mapped[list[Season]] = relationship("Season", back_populates="competition", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [Competition.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Competition id={self.competition_id} name={self.competition_name!r} slug={self.slug!r}>"
