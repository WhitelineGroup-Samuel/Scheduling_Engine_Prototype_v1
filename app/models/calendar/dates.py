# app/models/calendar/dates.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, Integer, Text, UniqueConstraint
from sqlalchemy import Date as SA_Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.calendar.public_holidays import PublicHoliday


class Date(Base):
    """
    ERD TABLE: dates
    PURPOSE: Canonical calendar dimension for all date logic (weekends, ISO week, holiday flags).

    Columns:
      - date_id SERIAL PK
      - date_value DATE NOT NULL [AK]
      - date_day TEXT NOT NULL  ('MONDAY'..'SUNDAY')
      - calendar_year INTEGER NOT NULL
      - iso_week_int INTEGER NOT NULL
      - is_weekend BOOLEAN NOT NULL
      - is_public_holiday BOOLEAN NOT NULL

    Indexes:
      - idx_dates_date_value (date_value)
    """

    __tablename__ = "dates"

    date_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_value: Mapped[SA_Date] = mapped_column(SA_Date, nullable=False)
    date_day: Mapped[str] = mapped_column(Text, nullable=False)
    calendar_year: Mapped[int] = mapped_column(Integer, nullable=False)
    iso_week_int: Mapped[int] = mapped_column(Integer, nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_public_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint("date_value", name="uq_dates_date_value"),
        Index("idx_dates_date_value", "date_value"),
    )

    # Relationships
    public_holidays: Mapped[list[PublicHoliday]] = relationship("PublicHoliday", back_populates="date", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Date id={self.date_id} value={self.date_value}>"
