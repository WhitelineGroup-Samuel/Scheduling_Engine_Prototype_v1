from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (  # ERD includes both created_* and updated_*
    CreatedStampedMixin,
    UpdatedStampedMixin,
)

if TYPE_CHECKING:
    from app.models.system.season_days import SeasonDay
    from app.models.timeplan.round_settings import RoundSetting
    from app.models.timeplan.time_slots import TimeSlot
    from app.models.venues.courts import Court


class CourtTime(CreatedStampedMixin, UpdatedStampedMixin, Base):
    """
    ERD: TABLE: court_times
    PURPOSE: Concrete schedulable cells (season_day × round_setting × court × time_slot),
             with availability/lock state.

    Columns:
      - court_time_id SERIAL PK
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - court_id INTEGER NOT NULL FK -> courts(court_id)
      - time_slot_id INTEGER NOT NULL FK -> time_slots(time_slot_id)
      - availability_status TEXT NOT NULL DEFAULT 'AVAILABLE'  // 'AVAILABLE','BLOCKED','MAINTENANCE','EVENT'
      - lock_state TEXT NOT NULL DEFAULT 'OPEN'                 // 'OPEN','LOCKED'
      - block_reason TEXT NULL
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)
      - updated_at TIMESTAMPTZ NULL
      - updated_by_user_id INTEGER NULL FK -> users(user_account_id)

    AK / Indexes:
      - UNIQUE (season_day_id, round_setting_id, court_id, time_slot_id) -> uq_court_times_key
      - INDEX  (season_day_id, round_setting_id)                          -> idx_court_times_day_setting
      - INDEX  (court_id)                                                 -> idx_court_times_court
      - INDEX  (time_slot_id)                                             -> idx_court_times_time_slot
    """

    __tablename__ = "court_times"

    court_time_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.court_id"), nullable=False)
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.time_slot_id"), nullable=False)

    availability_status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'AVAILABLE'"))
    lock_state: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'OPEN'"))
    block_reason: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "season_day_id",
            "round_setting_id",
            "court_id",
            "time_slot_id",
            name="uq_court_times_key",
        ),
        Index("idx_court_times_day_setting", "season_day_id", "round_setting_id"),
        Index("idx_court_times_court", "court_id"),
        Index("idx_court_times_time_slot", "time_slot_id"),
    )

    # Relationships
    season_day: Mapped[SeasonDay] = relationship("SeasonDay")
    round_setting: Mapped[RoundSetting] = relationship("RoundSetting")
    court: Mapped[Court] = relationship("Court", back_populates="court_times")
    time_slot: Mapped[TimeSlot] = relationship("TimeSlot")

    # Attribution relationships
    created_by = relationship("UserAccount", foreign_keys=lambda: [CourtTime.created_by_user_id])
    updated_by = relationship("UserAccount", foreign_keys=lambda: [CourtTime.updated_by_user_id])

    def __repr__(self) -> str:
        return f"<CourtTime id={self.court_time_id} court_id={self.court_id} time_slot_id={self.time_slot_id} status={self.availability_status!r}>"
