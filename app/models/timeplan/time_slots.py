## app/models/timeplan/time_slots.py

from __future__ import annotations

from datetime import time as dt_time
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.calendar.default_times import DefaultTime
    from app.models.system.season_days import SeasonDay


class TimeSlot(CreatedStampedMixin, Base):
    """
    ERD TABLE: time_slots
    PURPOSE: Time windows available for a season_day (with both normalized IDs and denormalized times).

    Columns:
      - time_slot_id SERIAL PK
      - season_day_id INTEGER NOT NULL FK -> season_days(season_day_id)
      - start_time_id INTEGER NOT NULL FK -> default_times(time_id)
      - end_time_id INTEGER NOT NULL FK -> default_times(time_id)
      - start_time TIME NOT NULL
      - end_time TIME NOT NULL
      - time_slot_label TEXT NOT NULL
      - buffer_minutes INTEGER NOT NULL
      - duration_minutes INTEGER NOT NULL
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (season_day_id, start_time, end_time)  -> uq_time_slots_day_window
      - UNIQUE (season_day_id, time_slot_label)       -> uq_time_slots_day_label
      - INDEX  (season_day_id)                         -> idx_time_slots_day
      - INDEX  (start_time, end_time)                  -> idx_time_slots_start_end
    """

    __tablename__ = "time_slots"

    time_slot_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_day_id: Mapped[int] = mapped_column(ForeignKey("season_days.season_day_id"), nullable=False)

    start_time_id: Mapped[int] = mapped_column(ForeignKey("default_times.time_id"), nullable=False)
    end_time_id: Mapped[int] = mapped_column(ForeignKey("default_times.time_id"), nullable=False)

    start_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    end_time: Mapped[dt_time] = mapped_column(Time, nullable=False)

    time_slot_label: Mapped[str] = mapped_column(Text, nullable=False)
    buffer_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("season_day_id", "start_time", "end_time", name="uq_time_slots_day_window"),
        UniqueConstraint("season_day_id", "time_slot_label", name="uq_time_slots_day_label"),
        Index("idx_time_slots_day", "season_day_id"),
        Index("idx_time_slots_start_end", "start_time", "end_time"),
    )

    # Relationships
    season_day: Mapped[SeasonDay] = relationship("SeasonDay")

    start_time_ref: Mapped[DefaultTime] = relationship("DefaultTime", foreign_keys=[start_time_id])
    end_time_ref: Mapped[DefaultTime] = relationship("DefaultTime", foreign_keys=[end_time_id])

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [TimeSlot.created_by_user_id])

    def __repr__(self) -> str:
        return (
            f"<TimeSlot id={self.time_slot_id} season_day_id={self.season_day_id} {self.start_time}-{self.end_time} label={self.time_slot_label!r}>"
        )
