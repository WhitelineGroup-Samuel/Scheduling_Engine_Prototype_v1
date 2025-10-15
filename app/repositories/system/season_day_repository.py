from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import asc, select

from app.models.system.season_days import SeasonDay
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, SeasonScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class SeasonDayRepository(BaseRepository[SeasonDay], SeasonScopedMixin, OrderingMixin):
    """
    Data access for SeasonDay rows.

    Scopes:
    - where_season(stmt, season_id)

    Helpers:
    - list_for_season(season_id): ordered by date_id ASC (stable)
    """

    model = SeasonDay

    # ---- SeasonScopedMixin contract ----
    def season_id_column(self) -> Any:
        return SeasonDay.season_id

    # ---- Queries ----
    def list_for_season(self, season_id: int) -> list[SeasonDay]:
        stmt: SelectStmt = select(SeasonDay).where(SeasonDay.season_id == season_id)
        # Stable, domain-correct ordering: Monday(1) .. Sunday(7)
        stmt = self.order_by(stmt, asc(SeasonDay.week_day))
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[SeasonDay]:
        stmt: SelectStmt = select(SeasonDay)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(stmt, asc(SeasonDay.week_day))
        return list(self.session.execute(stmt).scalars())

    def list_for_season_sorted(self, season_id: int, *, sort: SortQuery | None) -> list[SeasonDay]:
        stmt: SelectStmt = select(SeasonDay).where(SeasonDay.season_id == season_id)
        allowed: Mapping[str, Any] = {
            "weekday": SeasonDay.week_day,
            "name": SeasonDay.season_day_name,
            "created": SeasonDay.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_sorted_paged(
        self,
        season_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[SeasonDay], int]:
        stmt: SelectStmt = select(SeasonDay).where(SeasonDay.season_id == season_id)
        allowed: Mapping[str, Any] = {
            "weekday": SeasonDay.week_day,
            "name": SeasonDay.season_day_name,
            "created": SeasonDay.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=allowed["weekday"],
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)
