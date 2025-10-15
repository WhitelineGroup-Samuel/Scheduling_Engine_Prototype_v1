from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import select

from app.models.timeplan.round_settings import RoundSetting
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, SeasonDayScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class RoundSettingRepository(BaseRepository[RoundSetting], SeasonDayScopedMixin, OrderingMixin):
    """
    Data access for RoundSetting rows.

    Scopes:
    - where_season_day(stmt, season_day_id)

    Helpers:
    - list_for_season_day(season_day_id): ordered by PK for stability
    - list_ordered(): generic ordered list with optional filters
    """

    model = RoundSetting

    # ---- SeasonDayScopedMixin contract ----
    def season_day_id_column(self) -> Any:
        return RoundSetting.season_day_id

    # ---- Queries ----
    def list_for_season_day(self, season_day_id: int) -> list[RoundSetting]:
        stmt: SelectStmt = select(RoundSetting)
        stmt = self.where_season_day(stmt, season_day_id)
        stmt = self.order_by(stmt, RoundSetting.round_setting_id.asc())
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[RoundSetting]:
        stmt: SelectStmt = select(RoundSetting)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(stmt, RoundSetting.round_setting_id.asc())
        return list(self.session.execute(stmt).scalars())

    def list_for_season_day_sorted(
        self,
        season_day_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[RoundSetting]:
        """
        Sorted list of round settings for a season day.
        Allowed sort keys: 'id' (round_setting_id), 'created'.
        Default: id ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(RoundSetting).where(RoundSetting.season_day_id == season_day_id)

        allowed: Mapping[str, Any] = {
            "id": RoundSetting.round_setting_id,
            "created": RoundSetting.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=RoundSetting.round_setting_id,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_day_sorted_paged(
        self,
        season_day_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[RoundSetting], int]:
        """
        Sorted + paginated list of round settings for a season day.
        Returns (items, total).
        """
        stmt: SelectStmt = select(RoundSetting).where(RoundSetting.season_day_id == season_day_id)

        allowed: Mapping[str, Any] = {
            "id": RoundSetting.round_setting_id,
            "created": RoundSetting.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=RoundSetting.round_setting_id,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)
