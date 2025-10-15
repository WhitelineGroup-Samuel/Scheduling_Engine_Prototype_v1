# app/models/system/organisations.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD includes created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.system.competitions import Competition
    from app.models.system.user_permissions import UserPermission


class Organisation(CreatedStampedMixin, Base):
    """
    ERD TABLE: organisations
    PURPOSE: Tenant boundary; top-level owner of competitions/venues.
    Columns per ERD:
      - organisation_id SERIAL PK
      - organisation_name TEXT NOT NULL (AK)
      - time_zone TEXT NULLABLE
      - country_code TEXT NULLABLE
      - created_at TIMESTAMPTZ NULLABLE DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - slug VARCHAR(64) NOT NULL (AK)
    Indexes:
      - (created_by_user_id) idx_organisations_created_by
    """

    __tablename__ = "organisations"

    organisation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organisation_name: Mapped[str] = mapped_column(Text, nullable=False)
    time_zone: Mapped[str | None] = mapped_column(Text)
    country_code: Mapped[str | None] = mapped_column(Text)
    # created_at, created_by_user_id provided by CreatedStampedMixin
    slug: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("organisation_name", name="uq_organisations_organisation_name"),
        UniqueConstraint("slug", name="uq_organisations_slug"),
        Index("idx_organisations_created_by", "created_by_user_id"),
    )

    # Relationships
    competitions: Mapped[list[Competition]] = relationship("Competition", back_populates="organisation", cascade="all, delete-orphan")
    user_permissions: Mapped[list[UserPermission]] = relationship("UserPermission", back_populates="organisation", cascade="all, delete-orphan")

    # Attribution relationships (FKs declared via mixin)
    created_by = relationship("UserAccount", foreign_keys=lambda: [Organisation.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Organisation id={self.organisation_id} name={self.organisation_name!r} slug={self.slug!r}>"
