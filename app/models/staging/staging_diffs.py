from __future__ import annotations

from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import CreatedStampedMixin


class StagingDiff(CreatedStampedMixin, Base):
    """
    ERD TABLE: staging_diffs
    PURPOSE: Change log for staging entities (add/change/remove) with before/after JSON.

    Columns:
      - diff_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - entity_type TEXT NOT NULL   // CHECK: 'P2_ALLOCATION','P3_ALLOCATION','COMPOSITE_ALLOCATION'
      - entity_id TEXT NOT NULL
      - change_type TEXT NOT NULL   // CHECK: 'ADD','CHANGE','REMOVE'
      - before_json JSONB NULL
      - after_json JSONB NULL
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    Indexes:
      - idx_staging_diffs_run (run_id)
      - idx_staging_diffs_entity (entity_type, entity_id)
    """

    __tablename__ = "staging_diffs"

    diff_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)

    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(Text, nullable=False)

    before_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('P2_ALLOCATION','P3_ALLOCATION','COMPOSITE_ALLOCATION')",
            name="chk_staging_diffs_entity_type",
        ),
        CheckConstraint(
            "change_type IN ('ADD','CHANGE','REMOVE')",
            name="chk_staging_diffs_change_type",
        ),
        Index("idx_staging_diffs_run", "run_id"),
        Index("idx_staging_diffs_entity", "entity_type", "entity_id"),
    )

    # Relationships
    run = relationship("SchedulingRun")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [StagingDiff.created_by_user_id])

    def __repr__(self) -> str:
        return f"<StagingDiff id={self.diff_id} run_id={self.run_id} type={self.entity_type!r} change={self.change_type!r}>"
