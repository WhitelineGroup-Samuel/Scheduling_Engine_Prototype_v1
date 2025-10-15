from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import select

from app.models.taxonomy.ages import Age
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, SeasonDayScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery
from app.schemas.taxonomy.ages import AgeCreate


class AgeRepository(BaseRepository[Age], SeasonDayScopedMixin, OrderingMixin):
    """
    Data access for Age rows.

    Scopes:
    - where_season_day(stmt, season_day_id)

    Helpers:
    - list_for_season_day(season_day_id): ordered by age_rank ASC, then age_name ASC
    - list_ordered(): generic ordered list with optional filters
    """

    model = Age

    # ---- SeasonDayScopedMixin contract ----
    def season_day_id_column(self) -> Any:
        return Age.season_day_id

    # ---- Queries ----
    def list_for_season_day(self, season_day_id: int) -> list[Age]:
        stmt: SelectStmt = select(Age)
        stmt = self.where_season_day(stmt, season_day_id)
        stmt = self.order_by(
            stmt,
            Age.age_rank.asc(),
            Age.age_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Age]:
        stmt: SelectStmt = select(Age)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(
            stmt,
            Age.age_rank.asc(),
            Age.age_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_day_sorted(
        self,
        season_day_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Age]:
        """
        Sorted list of ages for a season day.
        Allowed sort keys: 'rank', 'name', 'created'.
        Default: rank ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(Age).where(Age.season_day_id == season_day_id)

        allowed: Mapping[str, Any] = {
            "rank": Age.age_rank,
            "name": Age.age_name,
            "created": Age.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Age.age_rank,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_day_sorted_paged(
        self,
        season_day_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Age], int]:
        """
        Sorted + paginated list of ages for a season day.
        Returns (items, total).
        """
        stmt: SelectStmt = select(Age).where(Age.season_day_id == season_day_id)

        allowed: Mapping[str, Any] = {
            "rank": Age.age_rank,
            "name": Age.age_name,
            "created": Age.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Age.age_rank,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Age:
        vals = dict(values)
        if not vals.get("age_code"):
            try:
                norm = getattr(AgeCreate, "normalize_age_code", None)
            except Exception:
                norm = None

            name = vals.get("age_name") or vals.get("name")
            if not name or not isinstance(name, str):
                raise ValueError("age_name is required to derive age_code")
            if callable(norm):
                vals["age_code"] = norm(name)
            else:
                import re

                s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                vals["age_code"] = re.sub(r"-+", "-", s)
        return super().create(vals)
