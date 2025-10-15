from __future__ import annotations

from typing import Any

from app.repositories.typing import SelectStmt


class OrgScopedMixin:
    """
    Mixin for repositories whose rows carry an `organisation_id` column.

    Child class must implement:
        def org_id_column(self): return <Model.organisation_id>
    """

    def org_id_column(self) -> Any:  # pragma: no cover - abstract-ish
        raise NotImplementedError

    def where_org(self, stmt: SelectStmt, organisation_id: int) -> SelectStmt:
        return stmt.where(self.org_id_column() == organisation_id)


class CompetitionScopedMixin:
    """
    Mixin for repositories whose rows carry a `competition_id` column.
    """

    def competition_id_column(self) -> Any:  # pragma: no cover
        raise NotImplementedError

    def where_competition(self, stmt: SelectStmt, competition_id: int) -> SelectStmt:
        return stmt.where(self.competition_id_column() == competition_id)


class SeasonScopedMixin:
    """
    Mixin for repositories whose rows carry a `season_id` column.
    """

    def season_id_column(self) -> Any:  # pragma: no cover
        raise NotImplementedError

    def where_season(self, stmt: SelectStmt, season_id: int) -> SelectStmt:
        return stmt.where(self.season_id_column() == season_id)


class SeasonDayScopedMixin:
    """
    Mixin for repositories whose rows carry a `season_day_id` column.
    """

    def season_day_id_column(self) -> Any:  # pragma: no cover
        raise NotImplementedError

    def where_season_day(self, stmt: SelectStmt, season_day_id: int) -> SelectStmt:
        return stmt.where(self.season_day_id_column() == season_day_id)


class OrderingMixin:
    """
    Small helpers to attach ORDER BY clauses consistently.
    Use from repos where you already have Column objects at hand.
    """

    @staticmethod
    def order_by(stmt: SelectStmt, *cols: Any) -> SelectStmt:
        """Apply ORDER BY for provided columns in sequence."""
        for col in cols:
            stmt = stmt.order_by(col)
        return stmt

    @staticmethod
    def order_by_asc(stmt: SelectStmt, *cols: Any) -> SelectStmt:
        """Alias of order_by (Column default .asc() is implicit for simple columns)."""
        return OrderingMixin.order_by(stmt, *cols)
