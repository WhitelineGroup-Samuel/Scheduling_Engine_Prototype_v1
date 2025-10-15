from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import select

from app.models.system.competitions import Competition
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, OrgScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery
from app.schemas.system.competitions import CompetitionCreate


class CompetitionRepository(BaseRepository[Competition], OrgScopedMixin, OrderingMixin):
    """
    Data access for Competition rows.

    Scopes:
    - where_org(stmt, organisation_id)

    Helpers:
    - list_for_org(organisation_id): ordered by competition_name ASC
    """

    model = Competition

    # ---- OrgScopedMixin contract ----
    def org_id_column(self) -> Any:
        return Competition.organisation_id

    # ---- Queries ----
    def list_for_org(self, organisation_id: int) -> list[Competition]:
        stmt: SelectStmt = select(Competition)
        stmt = self.where_org(stmt, organisation_id)
        stmt = self.order_by(stmt, Competition.competition_name.asc())
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Competition]:
        stmt: SelectStmt = select(Competition)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(stmt, Competition.competition_name.asc())
        return list(self.session.execute(stmt).scalars())

    def list_for_org_sorted(
        self,
        organisation_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Competition]:
        stmt: SelectStmt = select(Competition).where(Competition.organisation_id == organisation_id)
        allowed: Mapping[str, Any] = {
            "name": Competition.competition_name,
            "created": Competition.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Competition.competition_name,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_org_sorted_paged(
        self,
        organisation_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Competition], int]:
        stmt: SelectStmt = select(Competition).where(Competition.organisation_id == organisation_id)
        allowed: Mapping[str, Any] = {
            "name": Competition.competition_name,
            "created": Competition.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Competition.competition_name,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Competition:
        vals = dict(values)
        if not vals.get("slug"):
            # Prefer a DTO normaliser if you have one:
            try:
                norm = getattr(CompetitionCreate, "normalize_slug", None)
            except Exception:
                norm = None

            name = vals.get("competition_name") or vals.get("name")
            if not name or not isinstance(name, str):
                raise ValueError("competition_name is required to derive slug")

            if callable(norm):
                vals["slug"] = norm(name)
            else:
                import re

                s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                vals["slug"] = re.sub(r"-+", "-", s)
        return super().create(vals)
