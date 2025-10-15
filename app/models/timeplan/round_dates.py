from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.timeplan.rounds import Round


class RoundDate(CreatedStampedMixin, Base):
    """
    ERD TABLE: round_dates
    PURPOSE: Assign one or more calendar dates to a round.

    Columns:
      - round_date_id SERIAL PK
      - date_id INTEGER NOT NULL FK -> dates(date_id)
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (round_id, date_id) -> uq_round_dates_round_date
      - INDEX  (round_id)          -> idx_round_dates_round
      - INDEX  (date_id)           -> idx_round_dates_date
    """

    __tablename__ = "round_dates"

    round_date_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_id: Mapped[int] = mapped_column(ForeignKey("dates.date_id"), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("round_id", "date_id", name="uq_round_dates_round_date"),
        Index("idx_round_dates_round", "round_id"),
        Index("idx_round_dates_date", "date_id"),
    )

    # Relationships
    round: Mapped[Round] = relationship("Round", back_populates="round_dates")
    date = relationship("Date")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [RoundDate.created_by_user_id])

    def __repr__(self) -> str:
        return f"<RoundDate id={self.round_date_id} round_id={self.round_id} date_id={self.date_id}>"
