from __future__ import annotations

from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SchedulingRunEvent(Base):
    """
    ERD TABLE: scheduling_run_events
    PURPOSE: Timeline of run events (info/warn/error) by stage.

    Columns:
      - event_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - event_time TIMESTAMPTZ NULLABLE [default NOW()]
      - stage TEXT NOT NULL        // CHECK: 'STEP1','STEP2','STEP3','STEP4','STEP5','FINALISE'
      - severity TEXT NOT NULL     // CHECK: 'INFO','WARN','ERROR'
      - event_message TEXT NOT NULL
      - context JSONB NULLABLE

    Indexes (per ERD):
      - idx_run_events_run (run_id)
      - idx_run_events_stage (stage)
      - idx_run_events_severity (severity)
      - idx_run_events_time (event_time DESC)  // modelled as simple index on event_time
    """

    __tablename__ = "scheduling_run_events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)

    event_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    stage: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(Text, nullable=False)
    event_message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    __table_args__ = (
        CheckConstraint(
            "stage IN ('STEP1','STEP2','STEP3','STEP4','STEP5','FINALISE')",
            name="chk_run_events_stage",
        ),
        CheckConstraint(
            "severity IN ('INFO','WARN','ERROR')",
            name="chk_run_events_severity",
        ),
        Index("idx_run_events_run", "run_id"),
        Index("idx_run_events_stage", "stage"),
        Index("idx_run_events_severity", "severity"),
        Index("idx_run_events_time", "event_time"),
    )

    # Relationships
    run = relationship("SchedulingRun", back_populates="run_events")

    def __repr__(self) -> str:
        return f"<SchedulingRunEvent id={self.event_id} run_id={self.run_id} stage={self.stage!r} severity={self.severity!r}>"
