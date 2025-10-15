from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from sqlalchemy import select

from app.models.system.users import UserAccount
from app.repositories.base import BaseRepository
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class UserAccountRepository(BaseRepository[UserAccount]):
    """
    Data access for UserAccount rows.

    Helpers:
    - get_by_email(email): alternate-key lookup
    - list_active(): ordered by email ASC
    """

    model = UserAccount

    def get_by_email(self, email: str) -> UserAccount | None:
        stmt: SelectStmt = select(UserAccount).where(UserAccount.email == email)
        return cast(UserAccount | None, self.session.execute(stmt).scalar_one_or_none())

    def list_active(self) -> list[UserAccount]:
        stmt: SelectStmt = select(UserAccount).where(UserAccount.is_active.is_(True))
        stmt = stmt.order_by(UserAccount.email.asc())
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[UserAccount]:
        stmt: SelectStmt = select(UserAccount)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(UserAccount.email.asc())
        return list(self.session.execute(stmt).scalars())

    def list_sorted(self, *, sort: SortQuery | None) -> list[UserAccount]:
        stmt: SelectStmt = select(UserAccount)
        allowed: dict[str, Any] = {
            "email": UserAccount.email,
            "created": UserAccount.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=UserAccount.email,
        )
        return list(self.session.execute(stmt).scalars())

    def list_sorted_paged(self, *, sort: SortQuery | None, page: int, per_page: int) -> tuple[list[UserAccount], int]:
        stmt: SelectStmt = select(UserAccount)
        allowed: dict[str, Any] = {
            "email": UserAccount.email,
            "created": UserAccount.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=UserAccount.email,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def list_active_sorted_paged(self, *, sort: SortQuery | None, page: int, per_page: int) -> tuple[list[UserAccount], int]:
        stmt: SelectStmt = select(UserAccount).where(UserAccount.is_active.is_(True))
        allowed: dict[str, Any] = {
            "email": UserAccount.email,
            "created": UserAccount.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=UserAccount.email,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> UserAccount:
        """
        Create a user; derive display_name from the email local-part if missing.
        Also benefits from BaseRepository auto-attribution for created_by_user_id (if present on the model).
        """
        vals = dict(values)
        if not vals.get("display_name"):
            email = vals.get("email")
            if not email or "@" not in email:
                raise ValueError("email is required to derive display_name")
            local_part = email.split("@", 1)[0]
            # Keep it simple: use the local-part as-is; tests don't assert on display_name formatting
            vals["display_name"] = local_part
        return super().create(vals)
