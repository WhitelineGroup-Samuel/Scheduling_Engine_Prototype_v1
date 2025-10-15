from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SchedulingLock(Base):
    """
    ERD TABLE: scheduling_locks
    PURPOSE: Enforces exclusive orchestration per season_day.

    Columns:
      - lock_id SERIAL PK
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - locked_at TIMESTAMPTZ NULLABLE [default NOW()]
      - locked_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (season_day_id) -> uq_scheduling_locks_season_day
      - (ERD: no additional indexes)
    """

    __tablename__ = "scheduling_locks"

    lock_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)
    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    locked_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    locked_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_account_id"), nullable=False)

    __table_args__ = (
        # Only one runner may hold the lock for a given season_day
        Index("uq_scheduling_locks_season_day", "season_day_id", unique=True),
    )

    # Relationships
    season_day = relationship("SeasonDay")
    run = relationship("SchedulingRun")
    locked_by = relationship("UserAccount")

    def __repr__(self) -> str:
        return f"<SchedulingLock id={self.lock_id} season_day_id={self.season_day_id} run_id={self.run_id}>"
