from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._base_mixins import (
    CreatedStampedMixin,  # ERD: created_at + created_by_user_id
)

if TYPE_CHECKING:
    from app.models.timeplan.round_settings import RoundSetting
    from app.models.timeplan.rounds import Round


class RoundGroup(CreatedStampedMixin, Base):
    """
    ERD TABLE: round_groups
    PURPOSE: Binds a round to a specific round_setting.

    Columns:
      - round_group_id SERIAL PK
      - round_id INTEGER NOT NULL FK -> rounds(round_id)
      - round_setting_id INTEGER NOT NULL FK -> round_settings(round_setting_id)
      - created_at TIMESTAMPTZ NULL DEFAULT NOW()
      - created_by_user_id INTEGER NOT NULL FK -> users(user_account_id)

    AKs / Indexes:
      - UNIQUE (round_id, round_setting_id) -> uq_round_groups_round_setting
      - INDEX  (round_id)                   -> idx_round_groups_round
      - INDEX  (round_setting_id)           -> idx_round_groups_setting
    """

    __tablename__ = "round_groups"

    round_group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.round_id"), nullable=False)
    round_setting_id: Mapped[int] = mapped_column(ForeignKey("round_settings.round_setting_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("round_id", "round_setting_id", name="uq_round_groups_round_setting"),
        Index("idx_round_groups_round", "round_id"),
        Index("idx_round_groups_setting", "round_setting_id"),
    )

    # Relationships
    round: Mapped[Round] = relationship("Round", back_populates="round_groups")
    round_setting: Mapped[RoundSetting] = relationship("RoundSetting", back_populates="round_groups")

    # Attribution
    created_by = relationship("UserAccount", foreign_keys=lambda: [RoundGroup.created_by_user_id])

    def __repr__(self) -> str:
        return f"<RoundGroup id={self.round_group_id} round_id={self.round_id} round_setting_id={self.round_setting_id}>"
