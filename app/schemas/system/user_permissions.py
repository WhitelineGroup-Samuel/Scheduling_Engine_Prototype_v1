## app/schemas/system/user_permissions.py

from __future__ import annotations

from datetime import datetime

from app.schemas._base import ORMBase


class UserPermissionBase(ORMBase):
    """Shared, user-editable fields for a user's permission flags within an organisation."""

    can_schedule: bool = True
    can_approve: bool = True
    can_export: bool = True


class UserPermissionCreate(UserPermissionBase):
    """
    Create payload.
    Requires both the user and organisation identifiers.
    """

    user_account_id: int
    organisation_id: int


class UserPermissionUpdate(ORMBase):
    """Partial update — all fields optional."""

    can_schedule: bool | None = None
    can_approve: bool | None = None
    can_export: bool | None = None


class UserPermissionRead(UserPermissionBase):
    """Read payload with identifiers and DB-managed timestamp."""

    permission_id: int
    user_account_id: int
    organisation_id: int
    created_at: datetime | None = None
