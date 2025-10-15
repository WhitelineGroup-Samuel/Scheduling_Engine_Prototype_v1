from __future__ import annotations

from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RunConstraintsSnapshot(Base):
    """
    ERD TABLE: run_constraints_snapshot
    PURPOSE: JSON snapshot of constraints at key phases for a run.

    Columns:
      - snapshot_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - phase TEXT NOT NULL           // CHECK: 'P2','P3','COMPOSITE'
      - constraints_json JSONB NOT NULL
      - created_at TIMESTAMPTZ NULLABLE [default NOW()]

    Indexes (per ERD):
      - idx_run_constraints_snapshot_run (run_id)
    """

    __tablename__ = "run_constraints_snapshot"

    snapshot_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    phase: Mapped[str] = mapped_column(Text, nullable=False)
    constraints_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    __table_args__ = (
        CheckConstraint(
            "phase IN ('P2','P3','COMPOSITE')",
            name="chk_run_constraints_snapshot_phase",
        ),
        Index("idx_run_constraints_snapshot_run", "run_id"),
    )

    # Relationships
    run = relationship("SchedulingRun", back_populates="constraint_snapshots")

    def __repr__(self) -> str:
        return f"<RunConstraintsSnapshot id={self.snapshot_id} run_id={self.run_id} phase={self.phase!r}>"
