## app/repositories/system/user_permission_repository.py

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import asc, select

from app.models.system.user_permissions import UserPermission
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, OrgScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class UserPermissionRepository(BaseRepository[UserPermission], OrgScopedMixin, OrderingMixin):
    """
    Data access for UserPermission rows.

    Scopes:
    - where_org(stmt, organisation_id)

    Helpers:
    - list_for_user_in_org(user_account_id, organisation_id): returns the (single) row for that user+org (if present),
      ordered deterministically.
    - list_for_org(organisation_id): rows ordered by user_account_id (then PK).
    """

    model = UserPermission

    # ---- OrgScopedMixin contract ----
    def org_id_column(self) -> Any:
        return UserPermission.organisation_id

    # ---- Queries ----
    def list_for_user_in_org(self, user_account_id: int, organisation_id: int) -> list[UserPermission]:
        """
        For this schema there is at most one row per (user, org).
        We still return a list for API consistency and determinism.
        """
        stmt: SelectStmt = select(UserPermission).where(
            UserPermission.organisation_id == organisation_id,
            UserPermission.user_account_id == user_account_id,
        )
        # Deterministic ordering even if DB returns ties (use PK as tiebreaker)
        stmt = self.order_by(stmt, asc(UserPermission.created_at), asc(UserPermission.permission_id))
        return list(self.session.execute(stmt).scalars())

    def list_for_org(self, organisation_id: int) -> list[UserPermission]:
        """
        All permission rows for an organisation ordered by user then PK.
        """
        stmt: SelectStmt = select(UserPermission).where(UserPermission.organisation_id == organisation_id)
        stmt = self.order_by(stmt, asc(UserPermission.user_account_id), asc(UserPermission.permission_id))
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[UserPermission]:
        stmt: SelectStmt = select(UserPermission)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(stmt, asc(UserPermission.user_account_id), asc(UserPermission.permission_id))
        return list(self.session.execute(stmt).scalars())

    def list_for_user_in_org_sorted(
        self,
        user_account_id: int,
        organisation_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[UserPermission]:
        """
        Sort keys available:
            - "user"     -> user_account_id
            - "created"  -> created_at
            - "schedule" -> can_schedule
            - "approve"  -> can_approve
            - "export"   -> can_export
        Default: created_at ASC (with PK tiebreaker via BaseRepository.apply_sorting).
        """
        stmt: SelectStmt = select(UserPermission).where(
            UserPermission.organisation_id == organisation_id,
            UserPermission.user_account_id == user_account_id,
        )
        allowed: Mapping[str, Any] = {
            "user": UserPermission.user_account_id,
            "created": UserPermission.created_at,
            "schedule": UserPermission.can_schedule,
            "approve": UserPermission.can_approve,
            "export": UserPermission.can_export,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=UserPermission.created_at,  # must be a column (not a tuple)
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_org_sorted_paged(
        self,
        organisation_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[UserPermission], int]:
        """
        Sort keys available:
            - "user"     -> user_account_id
            - "created"  -> created_at
            - "schedule" -> can_schedule
            - "approve"  -> can_approve
            - "export"   -> can_export
        Default: user_account_id ASC.
        """
        stmt: SelectStmt = select(UserPermission).where(UserPermission.organisation_id == organisation_id)
        allowed: Mapping[str, Any] = {
            "user": UserPermission.user_account_id,
            "created": UserPermission.created_at,
            "schedule": UserPermission.can_schedule,
            "approve": UserPermission.can_approve,
            "export": UserPermission.can_export,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=UserPermission.user_account_id,  # must be a column (not a tuple)
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)
