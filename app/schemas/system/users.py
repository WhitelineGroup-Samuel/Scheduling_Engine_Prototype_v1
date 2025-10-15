from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas._base import ORMBase


class UserAccountBase(ORMBase):
    """Shared, user-editable fields for a user account."""

    display_name: str = Field(min_length=1)
    email: EmailStr
    is_active: bool | None = True


class UserAccountCreate(UserAccountBase):
    """
    What the API accepts to create a user.
    Note: `created_at` is DB-managed and not accepted from clients.
    """

    pass


class UserAccountUpdate(ORMBase):
    """Partial update — all fields optional."""

    display_name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    is_active: bool | None = None


class UserAccountRead(UserAccountBase):
    """What the API returns for a user."""

    user_account_id: int
    created_at: datetime | None = None
