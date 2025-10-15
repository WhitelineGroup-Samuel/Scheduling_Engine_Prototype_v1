from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy import select

from app.models.timeplan.rounds import Round
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, SeasonScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class RoundRepository(BaseRepository[Round], SeasonScopedMixin, OrderingMixin):
    """
    Data access for Round rows.

    Scopes:
    - where_season(stmt, season_id)

    Helpers:
    - list_for_season(season_id): ordered by round_number ASC (then PK as a tiebreaker)
    - list_ordered(): generic ordered list with optional filters
    """

    model = Round

    # ---- SeasonScopedMixin contract ----
    def season_id_column(self) -> Any:
        return Round.season_id

    # ---- Queries ----
    def list_for_season(self, season_id: int) -> list[Round]:
        stmt: SelectStmt = select(Round)
        stmt = self.where_season(stmt, season_id)
        stmt = self.order_by(
            stmt,
            Round.round_number.asc(),
            Round.round_id.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Round]:
        stmt: SelectStmt = select(Round)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(
            stmt,
            Round.round_number.asc(),
            Round.round_id.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_sorted(
        self,
        season_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Round]:
        """
        Sorted list of rounds for a season.
        Allowed sort keys: 'number' (round_number), 'created'.
        Default: number ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(Round).where(Round.season_id == season_id)

        allowed: Mapping[str, Any] = {
            "number": Round.round_number,
            "created": Round.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Round.round_number,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_season_sorted_paged(
        self,
        season_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Round], int]:
        """
        Sorted + paginated list of rounds for a season.
        Returns (items, total).
        """
        stmt: SelectStmt = select(Round).where(Round.season_id == season_id)

        allowed: Mapping[str, Any] = {
            "number": Round.round_number,
            "created": Round.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Round.round_number,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Round:
        vals = dict(values)
        if not vals.get("round_label"):
            # Prefer a semantic label if round_number exists
            rn = vals.get("round_number")
            if isinstance(rn, int) and rn > 0:
                vals["round_label"] = f"Round {rn}"
            else:
                # Fallback to something stable
                vals["round_label"] = "Round"
        return super().create(vals)
