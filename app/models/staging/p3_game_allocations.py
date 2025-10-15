from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class P3GameAllocation(CreatedStampedMixin, Base):
    """
    ERD TABLE: p3_game_allocations
    PURPOSE: Phase 3 team pairings on allocated slots.

    Columns:
      - p3_game_allocation_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - p2_allocation_id INTEGER NULL FK -> p2_allocations(p2_allocation_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - team_a_id INTEGER NOT NULL FK -> teams(team_id)
      - team_b_id INTEGER NOT NULL FK -> teams(team_id)
      - court_time_id INTEGER NOT NULL FK -> court_times(court_time_id)
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (run_id, round_id, court_time_id) -> uq_p3_games_run_round_ct
      - INDEX  (run_id, round_id)                -> idx_p3_games_run_round
      - INDEX  (court_time_id)                   -> idx_p3_games_ct
      - INDEX  (team_a_id, team_b_id)            -> idx_p3_games_teams
    """

    __tablename__ = "p3_game_allocations"

    p3_game_allocation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    p2_allocation_id: Mapped[int | None] = mapped_column(ForeignKey("p2_allocations.p2_allocation_id"))
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), nullable=False)
    court_time_id: Mapped[int] = mapped_column(ForeignKey("court_times.court_time_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("run_id", "round_id", "court_time_id", name="uq_p3_games_run_round_ct"),
        Index("idx_p3_games_run_round", "run_id", "round_id"),
        Index("idx_p3_games_ct", "court_time_id"),
        Index("idx_p3_games_teams", "team_a_id", "team_b_id"),
    )

    # Relationships (one-way)
    run = relationship("SchedulingRun")
    p2_allocation = relationship("P2Allocation")
    round = relationship("Round")
    age = relationship("Age")
    grade = relationship("Grade")
    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
    court_time = relationship("CourtTime")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [P3GameAllocation.created_by_user_id])

    def __repr__(self) -> str:
        return f"<P3GameAllocation id={self.p3_game_allocation_id} run_id={self.run_id} round_id={self.round_id} court_time_id={self.court_time_id}>"
