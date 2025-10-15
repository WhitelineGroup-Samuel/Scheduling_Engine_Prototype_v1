from __future__ import annotations

from datetime import date as dt_date

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class FinalByeSchedule(CreatedStampedMixin, Base):
    """
    ERD TABLE: final_bye_schedule
    PURPOSE: Denormalized, publish-ready bye rows (immutable snapshot).

    Columns:
      - final_bye_schedule_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - team_id INTEGER NOT NULL FK -> teams(team_id)
      - bye_date DATE NOT NULL
      - bye_name TEXT NOT NULL
      - organisation_name TEXT NOT NULL
      - competition_name TEXT NOT NULL
      - season_name TEXT NOT NULL
      - gender TEXT NULLABLE
      - age_name TEXT NOT NULL
      - grade_name TEXT NOT NULL
      - team_name TEXT NOT NULL
      - bye_reason TEXT NOT NULL  // CHECK: 'ODD_TEAMS','ERROR_LOOP','CONSTRAINT','MANUAL_OVERRIDE'
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - published_at TIMESTAMPTZ NULL
      - published_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (round_id, team_id) -> uq_final_byes_round_team
      - INDEX  (round_id)          -> idx_final_byes_round
      - INDEX  (team_id)           -> idx_final_byes_team
    """

    __tablename__ = "final_bye_schedule"

    final_bye_schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)

    bye_date: Mapped[dt_date] = mapped_column(Date, nullable=False)
    bye_name: Mapped[str] = mapped_column(Text, nullable=False)
    organisation_name: Mapped[str] = mapped_column(Text, nullable=False)
    competition_name: Mapped[str] = mapped_column(Text, nullable=False)
    season_name: Mapped[str] = mapped_column(Text, nullable=False)
    gender: Mapped[str | None] = mapped_column(Text)
    age_name: Mapped[str] = mapped_column(Text, nullable=False)
    grade_name: Mapped[str] = mapped_column(Text, nullable=False)
    team_name: Mapped[str] = mapped_column(Text, nullable=False)
    bye_reason: Mapped[str] = mapped_column(Text, nullable=False)

    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    published_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_account_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("round_id", "team_id", name="uq_final_byes_round_team"),
        Index("idx_final_byes_round", "round_id"),
        Index("idx_final_byes_team", "team_id"),
        CheckConstraint(
            "bye_reason IN ('ODD_TEAMS','ERROR_LOOP','CONSTRAINT','MANUAL_OVERRIDE')",
            name="chk_final_byes_reason",
        ),
    )

    # Relationships
    run = relationship("SchedulingRun")
    round = relationship("Round")
    age = relationship("Age")
    grade = relationship("Grade")
    team = relationship("Team")

    created_by = relationship("UserAccount", foreign_keys=lambda: [FinalByeSchedule.created_by_user_id])
    published_by = relationship("UserAccount", foreign_keys=lambda: [FinalByeSchedule.published_by_user_id])

    def __repr__(self) -> str:
        return f"<FinalByeSchedule id={self.final_bye_schedule_id} round_id={self.round_id} team_id={self.team_id} reason={self.bye_reason!r}>"
