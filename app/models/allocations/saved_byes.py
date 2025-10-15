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


class SavedBye(CreatedStampedMixin, Base):
    """
    ERD TABLE: saved_byes
    PURPOSE: Persisted bye rows at checkpoints.

    Columns:
      - saved_bye_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - team_id INTEGER NOT NULL FK -> teams(team_id)
      - bye_reason TEXT NULLABLE     // CHECK: 'ODD_TEAMS','ERROR_LOOP','CONSTRAINT','MANUAL_OVERRIDE'
      - game_status TEXT NOT NULL    // CHECK: 'AFTER_P2_BEFORE_P3','AFTER_P3_BEFORE_FINALISE','FINALISED'
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (run_id, round_id, team_id) -> uq_saved_byes_run_round_team
      - INDEX  (run_id, round_id)          -> idx_saved_byes_run_round
      - INDEX  (team_id)                   -> idx_saved_byes_team
    """

    __tablename__ = "saved_byes"

    saved_bye_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)

    bye_reason: Mapped[str | None] = mapped_column(Text)
    game_status: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("run_id", "round_id", "team_id", name="uq_saved_byes_run_round_team"),
        Index("idx_saved_byes_run_round", "run_id", "round_id"),
        Index("idx_saved_byes_team", "team_id"),
        CheckConstraint(
            "(bye_reason IS NULL) OR (bye_reason IN ('ODD_TEAMS','ERROR_LOOP','CONSTRAINT','MANUAL_OVERRIDE'))",
            name="chk_saved_byes_bye_reason",
        ),
        CheckConstraint(
            "game_status IN ('AFTER_P2_BEFORE_P3','AFTER_P3_BEFORE_FINALISE','FINALISED')",
            name="chk_saved_byes_game_status",
        ),
    )

    # Relationships
    run = relationship("SchedulingRun")
    round = relationship("Round")
    age = relationship("Age")
    grade = relationship("Grade")
    team = relationship("Team")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [SavedBye.created_by_user_id])

    def __repr__(self) -> str:
        return f"<SavedBye id={self.saved_bye_id} run_id={self.run_id} round_id={self.round_id} team_id={self.team_id} status={self.game_status!r}>"
