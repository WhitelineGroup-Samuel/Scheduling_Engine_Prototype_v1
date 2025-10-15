from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.scheduling.run_constraints_snapshot import RunConstraintsSnapshot
    from app.models.scheduling.run_exports import RunExport
    from app.models.scheduling.scheduling_run_events import SchedulingRunEvent


class SchedulingRun(CreatedStampedMixin, Base):
    """
    ERD TABLE: scheduling_runs
    PURPOSE: Orchestrated scheduling attempt state, idempotency, metrics, and lifecycle.

    Columns:
      - run_id SERIAL PK
      - season_id INTEGER NOT NULL FK -> seasons(season_id)
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - run_status TEXT NOT NULL        // CHECK: 'PENDING','RUNNING','FAILED','SUCCEEDED','ABANDONED'
      - process_type TEXT NOT NULL      // CHECK: 'INITIAL','MID'
      - run_type TEXT NULLABLE          // CHECK: 'I_RUN_1','I_RUN_2','M_RUN_1','M_RUN_2','M_RUN_3'
      - s1_check_results TEXT NOT NULL  // enum-like (ERD list)
      - round_ids JSONB NOT NULL
      - seed_master TEXT NOT NULL
      - resume_checkpoint TEXT NOT NULL // CHECK: 'BEFORE_P2','AFTER_P2_BEFORE_P3','AFTER_P3_BEFORE_FINALISE','FINALISED'
      - config_hash TEXT NULLABLE
      - idempotency_key TEXT NOT NULL   [AK]
      - metrics JSONB NULLABLE
      - error_code TEXT NULLABLE
      - error_details JSONB NULLABLE
      - started_at TIMESTAMPTZ NULLABLE
      - finished_at TIMESTAMPTZ NULLABLE
      - created_at TIMESTAMPTZ NULLABLE [default NOW()]
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    Indexes (per ERD):
      - idx_runs_season_day (season_day_id)
      - idx_runs_status (run_status)
      - idx_runs_created_at (created_at)
      - idx_runs_created_by (created_by_user_id)
    """

    __tablename__ = "scheduling_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.season_id"), nullable=False)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)

    run_status: Mapped[str] = mapped_column(Text, nullable=False)
    process_type: Mapped[str] = mapped_column(Text, nullable=False)
    run_type: Mapped[str | None] = mapped_column(Text)
    s1_check_results: Mapped[str] = mapped_column(Text, nullable=False)

    round_ids: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    seed_master: Mapped[str] = mapped_column(Text, nullable=False)
    resume_checkpoint: Mapped[str] = mapped_column(Text, nullable=False)

    config_hash: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error_code: Mapped[str | None] = mapped_column(Text)
    error_details: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # created_at, created_by_user_id supplied by CreatedStampedMixin

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_scheduling_runs_idempotency_key"),
        CheckConstraint(
            "run_status IN ('PENDING','RUNNING','FAILED','SUCCEEDED','ABANDONED')",
            name="chk_scheduling_runs_run_status",
        ),
        CheckConstraint(
            "process_type IN ('INITIAL','MID')",
            name="chk_scheduling_runs_process_type",
        ),
        CheckConstraint(
            "(run_type IS NULL) OR (run_type IN ('I_RUN_1','I_RUN_2','M_RUN_1','M_RUN_2','M_RUN_3'))",
            name="chk_scheduling_runs_run_type",
        ),
        CheckConstraint(
            "resume_checkpoint IN ('BEFORE_P2','AFTER_P2_BEFORE_P3','AFTER_P3_BEFORE_FINALISE','FINALISED')",
            name="chk_scheduling_runs_resume_checkpoint",
        ),
        # s1_check_results has a long enumerated set in the ERD; modelled as free text.
        Index("idx_runs_season_day", "season_day_id"),
        Index("idx_runs_status", "run_status"),
        Index("idx_runs_created_at", "created_at"),
        Index("idx_runs_created_by", "created_by_user_id"),
    )

    # Relationships
    season = relationship("Season")
    season_day = relationship("SeasonDay")

    run_events: Mapped[list[SchedulingRunEvent]] = relationship("SchedulingRunEvent", back_populates="run", cascade="all, delete-orphan")
    exports: Mapped[list[RunExport]] = relationship("RunExport", back_populates="run", cascade="all, delete-orphan")
    constraint_snapshots: Mapped[list[RunConstraintsSnapshot]] = relationship(
        "RunConstraintsSnapshot", back_populates="run", cascade="all, delete-orphan"
    )

    created_by = relationship("UserAccount", foreign_keys=lambda: [SchedulingRun.created_by_user_id])

    def __repr__(self) -> str:
        return f"<SchedulingRun id={self.run_id} season_day_id={self.season_day_id} status={self.run_status!r} process={self.process_type!r}>"
