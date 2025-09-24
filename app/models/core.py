"""
===============================================================================
File: app/models/core.py
Purpose:
  Define the first concrete ORM entity for visibility & migration validation.

Entity Scope (from database_erd.md)
-----------------------------------
TABLE: organisations
PURPOSE: Tenant boundary; top-level owner of competitions/venues.

Columns (mirror ERD exactly for v1)
-----------------------------------
- organisation_id : INTEGER PRIMARY KEY (SERIAL in ERD)
    - SQLAlchemy: Integer, primary_key=True, autoincrement=True
- organisation_name : TEXT NOT NULL
    - Unique constraint (alternate key in ERD) → enforce UNIQUE
- time_zone : TEXT NULL
- country_code : TEXT NULL
- created_at : TIMESTAMPTZ NULL DEFAULT now()
    - Model: timezone-aware DateTime (timezone=True) with server_default=sa.text("now()")
- created_by_user_id : INTEGER NOT NULL  (FK → users(user_account_id))
    - Index on (created_by_user_id) as per ERD
    - FK addition may be deferred if the users table is not yet present in this service.
      If users table is outside this service scope, create as a plain Integer + index now,
      and add the FK constraint in a later revision when the users table is available.

Modeling Requirements
---------------------
- Use SQLAlchemy **2.x** Declarative with type annotations.
- `__tablename__ = "organisations"`.
- Column names should match the ERD names exactly for easier SQL parity.
- Add a __repr__ helper with key fields for debugging.
- Do NOT import Base at module import time from anywhere other than app.db.base.
  (Correct import: `from app.db.base import Base`.)

Indexes & Constraints
---------------------
- UNIQUE(organisation_name)
- INDEX(created_by_user_id) named via naming convention (ix_organisations_created_by_user_id)
- Optional: future functional index LOWER(organisation_name) if case-insensitive search is needed.

Migration Expectations (autogenerate)
-------------------------------------
- Alembic autogenerate should create:
  - organisations table with the above columns & constraints
  - unique constraint on organisation_name
  - btree index on created_by_user_id
  - (FK only if users table is present; otherwise omit FK now to avoid broken refs)
- No data seeding in this initial revision.

Testing Notes
-------------
- Integration test should SELECT current_database() and ensure table exists once migrations are applied.
- Repository smoke test can insert/select/rollback using db_session fixture when enabled.

Dependencies
------------
- app.db.base.Base  (Declarative Base)
- SQLAlchemy 2.x (sqlalchemy and sqlalchemy.orm)
===============================================================================
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Organisation(Base):
    """
    ORM class for `organisations` matching the ERD.
    See header block for full specification and migration expectations.
    """

    __tablename__ = "organisations"

    organisation_id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    organisation_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    time_zone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    country_code: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped["sa.DateTime"] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=True,  # ERD marks NULLABLE; keep parity for v1
    )
    created_by_user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("organisation_name"),
        sa.Index("ix_organisations_created_by_user_id", "created_by_user_id"),
        # FK deferred until users table exists locally; enable later:
        # sa.ForeignKeyConstraint(["created_by_user_id"], ["users.user_account_id"]),
    )

    def __repr__(self) -> str:
        return (
            f"Organisation(id={self.organisation_id!r}, "
            f"name={self.organisation_name!r}, tz={self.time_zone!r})"
        )
