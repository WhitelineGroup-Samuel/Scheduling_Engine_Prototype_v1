from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class SavedGame(CreatedStampedMixin, Base):
    """
    ERD TABLE: saved_games
    PURPOSE: Persisted game rows at checkpoints (after P2, after P3, finalised).

    Columns:
      - saved_game_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - team_a_id INTEGER NOT NULL FK -> teams(team_id)
      - team_b_id INTEGER NOT NULL FK -> teams(team_id)
      - court_time_id INTEGER NOT NULL FK -> court_times(court_time_id)
      - game_status TEXT NOT NULL  // CHECK: 'AFTER_P2_BEFORE_P3','AFTER_P3_BEFORE_FINALISE','FINALISED'
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (run_id, round_id, court_time_id) -> uq_saved_games_run_round_ct
      - INDEX  (run_id, round_id)                -> idx_saved_games_run_round
      - INDEX  (court_time_id)                   -> idx_saved_games_ct
    """

    __tablename__ = "saved_games"

    saved_game_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)
    court_time_id: Mapped[int] = mapped_column(ForeignKey("court_times.court_time_id"), nullable=False)

    game_status: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("run_id", "round_id", "court_time_id", name="uq_saved_games_run_round_ct"),
        Index("idx_saved_games_run_round", "run_id", "round_id"),
        Index("idx_saved_games_ct", "court_time_id"),
        CheckConstraint(
            "game_status IN ('AFTER_P2_BEFORE_P3','AFTER_P3_BEFORE_FINALISE','FINALISED')",
            name="chk_saved_games_game_status",
        ),
    )

    # Convenience relationships (no back_populates required in parents)
    run = relationship("SchedulingRun")
    round = relationship("Round")
    age = relationship("Age")
    grade = relationship("Grade")
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    court_time = relationship("CourtTime")

    # Attribution from mixin
    created_by = relationship("UserAccount", foreign_keys=lambda: [SavedGame.created_by_user_id])

    def __repr__(self) -> str:
        return (
            f"<SavedGame id={self.saved_game_id} run_id={self.run_id} "
            f"round_id={self.round_id} court_time_id={self.court_time_id} status={self.game_status!r}>"
        )
