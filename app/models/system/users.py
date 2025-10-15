# app/models/system/users.py

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.system.user_permissions import UserPermission


class UserAccount(Base):
    """
    ERD TABLE: users
    PURPOSE: Application user accounts (creators, publishers, run owners, etc.).
    Columns per ERD:
      - user_account_id SERIAL PK
      - display_name TEXT NOT NULL
      - email TEXT NOT NULL (AK)
      - is_active BOOLEAN NULLABLE DEFAULT TRUE
      - created_at TIMESTAMPTZ NULLABLE DEFAULT NOW()
    """

    __tablename__ = "users"

    user_account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    # Relationships
    permissions: Mapped[list[UserPermission]] = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    def __repr__(self) -> str:
        return f"<UserAccount id={self.user_account_id} email={self.email!r}>"
