"""app.models.core
===================

SQLAlchemy ORM models for the Scheduling Engine prototype. This module
currently exposes the :class:`Organisation` entity which mirrors the ERD's
``organisations`` table and enables Alembic autogeneration to detect schema
changes during the initial development phase.
"""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

__all__ = ["Organisation"]


class Organisation(Base):
    """Concrete ORM mapping for the ``organisations`` table.

    Attributes
    ----------
    organisation_id:
        Surrogate primary key that auto-increments.
    organisation_name:
        Unique, human-readable name of the organisation.
    time_zone / country_code:
        Optional descriptive metadata matching the ERD specification.
    created_at / updated_at:
        Server managed timestamps (UTC) used for auditing.
    created_by_user_id:
        Identifier of the user that provisioned the organisation. The foreign
        key constraint is deferred until the ``users`` table becomes available
        within this service boundary.
    slug:
        Stable unique identifier suitable for CLI usage and URLs.
    """

    __tablename__ = "organisations"

    organisation_id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    organisation_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    time_zone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    country_code: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=True,
    )
    created_by_user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    slug: Mapped[str] = mapped_column(sa.Text, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        onupdate=sa.text("now()"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "organisation_name", name="uq_organisations_organisation_name"
        ),
        UniqueConstraint("slug", name="uq_organisations_slug"),
        sa.Index("ix_organisations_created_by_user_id", "created_by_user_id"),
    )

    def __repr__(self) -> str:
        """Return a helpful representation for debugging and logging."""

        return (
            "Organisation("
            f"id={self.organisation_id!r}, "
            f"name={self.organisation_name!r}, "
            f"slug={self.slug!r}"
            ")"
        )
