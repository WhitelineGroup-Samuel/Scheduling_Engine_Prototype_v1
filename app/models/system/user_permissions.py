## app/models/system/user_permissions.py

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserPermission(Base):
    """
    ERD TABLE: user_permissions
    PURPOSE: Per-organisation capability flags for a user.
    Columns per ERD:
      - permission_id SERIAL PK
      - user_account_id INTEGER NOT NULL FK -> users(user_account_id)
      - organisation_id INTEGER NOT NULL FK -> organisations(organisation_id)
      - can_schedule BOOLEAN NOT NULL DEFAULT TRUE
      - can_approve  BOOLEAN NOT NULL DEFAULT TRUE
      - can_export   BOOLEAN NOT NULL DEFAULT TRUE
      - created_at TIMESTAMPTZ NULLABLE DEFAULT NOW()
    AKs:
      - UNIQUE (user_account_id, organisation_id)
    Indexes:
      - idx_user_permissions_user (user_account_id)
      - idx_user_permissions_org (organisation_id)
    """

    __tablename__ = "user_permissions"

    permission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_account_id: Mapped[int] = mapped_column(ForeignKey("users.user_account_id"), nullable=False)
    organisation_id: Mapped[int] = mapped_column(ForeignKey("organisations.organisation_id"), nullable=False)
    can_schedule: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    can_approve: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    can_export: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    __table_args__ = (
        UniqueConstraint("user_account_id", "organisation_id", name="uq_user_permissions_user_org"),
        Index("idx_user_permissions_user", "user_account_id"),
        Index("idx_user_permissions_org", "organisation_id"),
    )

    # Relationships
    user = relationship("UserAccount", back_populates="permissions")
    organisation = relationship("Organisation", back_populates="user_permissions")

    def __repr__(self) -> str:
        return f"<UserPermission id={self.permission_id} user_account_id={self.user_account_id} organisation_id={self.organisation_id}>"
