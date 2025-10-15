# app/models/taxonomy/grades.py

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
    from app.models.taxonomy.ages import Age
    from app.models.taxonomy.teams import Team


class Grade(CreatedStampedMixin, Base):
    """
    ERD TABLE: grades
    PURPOSE: Competitive band within an age (e.g., A/B/C grade).

    Columns (per ERD):
      - grade_id SERIAL PK
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_code VARCHAR(20) NOT NULL
      - grade_name TEXT NOT NULL
      - grade_rank INTEGER NOT NULL
      - grade_required_games INTEGER NULL
      - bye_requirement BOOLEAN NULL DEFAULT FALSE
      - active BOOLEAN NULL DEFAULT TRUE
      - display_colour TEXT NULL
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (age_id, grade_code) -> uq_grades_code
      - UNIQUE (age_id, grade_name) -> uq_grades_name
      - UNIQUE (age_id, grade_rank) -> uq_grades_rank
      - INDEX  (age_id)             -> idx_grades_age
    """

    __tablename__ = "grades"

    grade_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)

    grade_code: Mapped[str] = mapped_column(String(20), nullable=False)
    grade_name: Mapped[str] = mapped_column(Text, nullable=False)
    grade_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    grade_required_games: Mapped[int | None] = mapped_column(Integer)
    bye_requirement: Mapped[bool | None] = mapped_column(Boolean, server_default=text("FALSE"))
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    display_colour: Mapped[str | None] = mapped_column(Text)
    # created_at, created_by_user_id provided by CreatedStampedMixin

    __table_args__ = (
        UniqueConstraint("age_id", "grade_code", name="uq_grades_code"),
        UniqueConstraint("age_id", "grade_name", name="uq_grades_name"),
        UniqueConstraint("age_id", "grade_rank", name="uq_grades_rank"),
        Index("idx_grades_age", "age_id"),
    )

    # Relationships
    age: Mapped[Age] = relationship("Age", back_populates="grades")
    teams: Mapped[list[Team]] = relationship("Team", back_populates="grade", cascade="all, delete-orphan")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [Grade.created_by_user_id])

    def __repr__(self) -> str:
        return f"<Grade id={self.grade_id} code={self.grade_code!r}>"
