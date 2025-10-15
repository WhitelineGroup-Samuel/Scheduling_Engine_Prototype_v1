from __future__ import annotations

from datetime import date as dt_date
from datetime import time as dt_time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class FinalGameSchedule(CreatedStampedMixin, Base):
    """
    ERD TABLE: final_game_schedule
    PURPOSE: Denormalized, publish-ready fixture rows (immutable snapshot).

    Columns:
      - final_game_schedule_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - team_a_id INTEGER NOT NULL FK -> teams(team_id)
      - team_b_id INTEGER NOT NULL FK -> teams(team_id)
      - court_time_id INTEGER NOT NULL FK -> court_times(court_time_id)
      - game_date DATE NOT NULL
      - game_name TEXT NOT NULL
      - organisation_name TEXT NOT NULL
      - competition_name TEXT NOT NULL
      - season_name TEXT NOT NULL
      - gender TEXT NULLABLE
      - venue_name TEXT NOT NULL
      - court_name TEXT NOT NULL
      - start_time TIME NOT NULL
      - age_name TEXT NOT NULL
      - grade_name TEXT NOT NULL
      - team_a_name TEXT NOT NULL
      - team_b_name TEXT NOT NULL
      - game_status TEXT NULLABLE [default: 'FINALISED']  // CHECK: 'FINALISED','CANCELLED','FORFEITED','COMPLETED'
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - published_at TIMESTAMPTZ NULL
      - published_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (round_id, court_time_id) -> uq_final_games_round_ct
      - INDEX  (round_id)                -> idx_final_games_round
      - INDEX  (court_time_id)           -> idx_final_games_ct
    """

    __tablename__ = "final_game_schedule"

    final_game_schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)
    court_time_id: Mapped[int] = mapped_column(ForeignKey("court_times.court_time_id"), nullable=False)

    game_date: Mapped[dt_date] = mapped_column(Date, nullable=False)
    game_name: Mapped[str] = mapped_column(Text, nullable=False)
    organisation_name: Mapped[str] = mapped_column(Text, nullable=False)
    competition_name: Mapped[str] = mapped_column(Text, nullable=False)
    season_name: Mapped[str] = mapped_column(Text, nullable=False)
    gender: Mapped[str | None] = mapped_column(Text)
    venue_name: Mapped[str] = mapped_column(Text, nullable=False)
    court_name: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    age_name: Mapped[str] = mapped_column(Text, nullable=False)
    grade_name: Mapped[str] = mapped_column(Text, nullable=False)
    team_a_name: Mapped[str] = mapped_column(Text, nullable=False)
    team_b_name: Mapped[str] = mapped_column(Text, nullable=False)
    game_status: Mapped[str | None] = mapped_column(Text, server_default=text("'FINALISED'"))

    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    published_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_account_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("round_id", "court_time_id", name="uq_final_games_round_ct"),
        Index("idx_final_games_round", "round_id"),
        Index("idx_final_games_ct", "court_time_id"),
        CheckConstraint(
            "(game_status IS NULL) OR (game_status IN ('FINALISED','CANCELLED','FORFEITED','COMPLETED'))",
            name="chk_final_games_game_status",
        ),
    )

    # Relationships
    run = relationship("SchedulingRun")
    round = relationship("Round")
    age = relationship("Age")
    grade = relationship("Grade")
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    court_time = relationship("CourtTime")

    created_by = relationship("UserAccount", foreign_keys=lambda: [FinalGameSchedule.created_by_user_id])
    published_by = relationship("UserAccount", foreign_keys=lambda: [FinalGameSchedule.published_by_user_id])

    def __repr__(self) -> str:
        return f"<FinalGameSchedule id={self.final_game_schedule_id} round_id={self.round_id} ct_id={self.court_time_id} status={self.game_status!r}>"
