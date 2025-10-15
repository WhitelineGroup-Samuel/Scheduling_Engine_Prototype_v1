## app/models/calendar/default_times.py

from __future__ import annotations

from datetime import time as dt_time

from sqlalchemy import Index, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DefaultTime(Base):
    """
    ERD TABLE: default_times
    PURPOSE: Normalized catalog of times-of-day (lookup).

    Columns:
      - time_id SERIAL PK
      - time_value TIME NOT NULL [AK]

    Indexes:
      - idx_default_times_time_value (time_value)
    """

    __tablename__ = "default_times"

    time_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time_value: Mapped[dt_time] = mapped_column(Time, nullable=False)

    __table_args__ = (
        UniqueConstraint("time_value", name="uq_default_times_time_value"),
        Index("idx_default_times_time_value", "time_value"),
    )

    def __repr__(self) -> str:
        return f"<DefaultTime id={self.time_id} value={self.time_value}>"
