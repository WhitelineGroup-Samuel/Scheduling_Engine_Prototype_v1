from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column


class CreatedStampedMixin:
    """Adds created_at and created_by_user_id."""

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=True,
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_account_id"),
        nullable=False,
    )


class UpdatedStampedMixin:
    """Adds updated_at and updated_by_user_id."""

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_account_id"),
        nullable=True,
    )
