from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class P2Allocation(CreatedStampedMixin, Base):
    """
    ERD TABLE: p2_allocations
    PURPOSE: Phase 2 allocations of ages/grades to court_time per run/round.

    Columns:
      - p2_allocation_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - age_id INTEGER NOT NULL FK -> ages(age_id)
      - grade_id INTEGER NOT NULL FK -> grades(grade_id)
      - court_time_id INTEGER NOT NULL FK -> court_times(court_time_id)
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (run_id, round_id, court_time_id) -> uq_p2_allocations_run_round_ct
      - INDEX  (run_id, round_id)                -> idx_p2_allocations_run_round
      - INDEX  (court_time_id)                   -> idx_p2_allocations_ct
    """

    __tablename__ = "p2_allocations"

    p2_allocation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    age_id: Mapped[int] = mapped_column(ForeignKey("ages.age_id"), nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.grade_id"), nullable=False)
    court_time_id: Mapped[int] = mapped_column(ForeignKey("court_times.court_time_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("run_id", "round_id", "court_time_id", name="uq_p2_allocations_run_round_ct"),
        Index("idx_p2_allocations_run_round", "run_id", "round_id"),
        Index("idx_p2_allocations_ct", "court_time_id"),
    )

    # Relationships (one-way; no back_populates required in parent models)
    run = relationship("SchedulingRun")
    round = relationship("Round")
    age = relationship("Age")
    grade = relationship("Grade")
    court_time = relationship("CourtTime")

    # Attribution (from mixin)
    created_by = relationship("UserAccount", foreign_keys=lambda: [P2Allocation.created_by_user_id])

    def __repr__(self) -> str:
        return f"<P2Allocation id={self.p2_allocation_id} run_id={self.run_id} round_id={self.round_id} court_time_id={self.court_time_id}>"
