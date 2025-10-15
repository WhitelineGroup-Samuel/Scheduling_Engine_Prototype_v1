# app/models/taxonomy/teams.py

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
    from app.models.taxonomy.grades import Grade


class Team(CreatedStampedMixin, Base):
    """
    ERD TABLE: teams
    PURPOSE: Individual teams registered in a grade.

    Columns (per ERD):
      - team_id SERIAL PK
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - team_code VARCHAR(20) NOT NULL
      - team_name TEXT NULL
      - active BOOLEAN NULL DEFAULT TRUE
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (grade_id, team_code) -> uq_teams_grade_code
      - UNIQUE (grade_id, team_name) -> uq_teams_grade_name
      - INDEX  (grade_id)            -> idx_teams_grade
      - INDEX  (active)              -> idx_teams_active
    """

    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)

    team_code: Mapped[str] = mapped_column(String(20), nullable=False)
    team_name: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    # created_at, created_by_user_id provided by CreatedStampedMixin

    __table_args__ = (
        UniqueConstraint("grade_id", "team_code", name="uq_teams_grade_code"),
        UniqueConstraint("grade_id", "team_name", name="uq_teams_grade_name"),
        Index("idx_teams_grade", "grade_id"),
        Index("idx_teams_active", "active"),
    )

    # Relationships
    grade: Mapped[Grade] = relationship("Grade", back_populates="teams")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [Team.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Team id={self.team_id} code={self.team_code!r}>"
