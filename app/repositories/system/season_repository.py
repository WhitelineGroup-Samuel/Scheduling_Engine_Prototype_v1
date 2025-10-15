from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import select

from app.models.system.seasons import Season
from app.repositories.base import BaseRepository
from app.repositories.mixins import CompetitionScopedMixin, OrderingMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery
from app.schemas.system.seasons import SeasonCreate


class SeasonRepository(BaseRepository[Season], CompetitionScopedMixin, OrderingMixin):
    """
    Data access for Season rows.

    Scopes:
    - where_competition(stmt, competition_id)

    Helpers:
    - list_for_competition(competition_id): ordered by starting_date ASC NULLS LAST, then season_name
    """

    model = Season

    # ---- CompetitionScopedMixin contract ----
    def competition_id_column(self) -> Any:
        return Season.competition_id

    # ---- Queries ----
    def list_for_competition(self, competition_id: int) -> list[Season]:
        stmt: SelectStmt = select(Season)
        stmt = self.where_competition(stmt, competition_id)
        # Prefer chronological ordering; fall back to name
        stmt = self.order_by(
            stmt,
            Season.starting_date.asc().nulls_last(),  # if column exists in your model
            Season.season_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Season]:
        stmt: SelectStmt = select(Season)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(
            stmt,
            Season.starting_date.asc().nulls_last(),
            Season.season_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_competition_sorted(
        self,
        competition_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Season]:
        stmt: SelectStmt = select(Season).where(Season.competition_id == competition_id)
        allowed: Mapping[str, Any] = {
            "start": Season.starting_date,  # if your model has it
            "name": Season.season_name,
            "created": Season.created_at,
        }
        default_col = Season.starting_date if hasattr(Season, "starting_date") else Season.season_name
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=default_col,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_competition_sorted_paged(
        self,
        competition_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Season], int]:
        stmt: SelectStmt = select(Season).where(Season.competition_id == competition_id)
        allowed: Mapping[str, Any] = {
            "start": Season.starting_date,  # if present
            "name": Season.season_name,
            "created": Season.created_at,
        }
        default_col = Season.starting_date if hasattr(Season, "starting_date") else Season.season_name
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=default_col,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Season:
        vals = dict(values)
        if not vals.get("slug"):
            try:
                norm = getattr(SeasonCreate, "normalize_slug", None)
            except Exception:
                norm = None

            name = vals.get("season_name") or vals.get("name")
            if not name or not isinstance(name, str):
                raise ValueError("season_name is required to derive slug")
            if callable(norm):
                vals["slug"] = norm(name)
            else:
                import re

                s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                vals["slug"] = re.sub(r"-+", "-", s)
        return super().create(vals)
