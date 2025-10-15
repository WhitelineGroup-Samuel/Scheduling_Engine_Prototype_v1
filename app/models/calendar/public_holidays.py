from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PublicHoliday(Base):
    """
    ERD TABLE: public_holidays
    PURPOSE: Named public holidays per date and Australian region.

    Columns:
      - public_holiday_id SERIAL PK
      - date_id INTEGER NOT NULL FK -> dates(date_id)
      - holiday_name TEXT NOT NULL
      - holiday_region TEXT NOT NULL  ('CTH','TAS','VIC','NSW','ACT','QLD','SA','NT','WA')

    Indexes:
      - (none defined in ERD)
    """

    __tablename__ = "public_holidays"

    public_holiday_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_id: Mapped[int] = mapped_column(ForeignKey("dates.date_id"), nullable=False)
    holiday_name: Mapped[str] = mapped_column(Text, nullable=False)
    holiday_region: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    date = relationship("Date", back_populates="public_holidays")

    def __repr__(self) -> str:
        return f"<PublicHoliday id={self.public_holiday_id} date_id={self.date_id} region={self.holiday_region!r}>"
