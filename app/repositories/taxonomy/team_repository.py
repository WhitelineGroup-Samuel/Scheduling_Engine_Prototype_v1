from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from sqlalchemy import select

from app.models.taxonomy.teams import Team
from app.repositories.base import BaseRepository
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery
from app.schemas.taxonomy.teams import TeamCreate


class TeamRepository(BaseRepository[Team]):
    """
    Data access for Team rows.

    Helpers:
    - list_for_grade(grade_id): ordered by team_code ASC, then team_name ASC
    - list_ordered(): generic ordered list with optional filters
    - get_by_code_in_grade(grade_id, team_code): soft AK within a grade (None if not found)
    """

    model = Team

    # ---- Queries ----
    def list_for_grade(self, grade_id: int) -> list[Team]:
        stmt: SelectStmt = select(Team).where(Team.grade_id == grade_id)
        stmt = stmt.order_by(
            Team.team_code.asc(),
            Team.team_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Team]:
        stmt: SelectStmt = select(Team)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(
            Team.team_code.asc(),
            Team.team_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def get_by_code_in_grade(self, grade_id: int, team_code: str) -> Team | None:
        """
        Convenience lookup when UI treats team_code as unique within a grade.
        Returns None if there is no exact code match under this grade.
        """
        stmt: SelectStmt = select(Team).where(Team.grade_id == grade_id).where(Team.team_code == team_code)
        return cast(Team | None, self.session.execute(stmt).scalar_one_or_none())

    def list_for_grade_sorted(
        self,
        grade_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Team]:
        """
        Sorted list of teams for a grade.
        Allowed sort keys: 'code', 'name', 'created'.
        Default: code ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(Team).where(Team.grade_id == grade_id)

        allowed: Mapping[str, Any] = {
            "code": Team.team_code,
            "name": Team.team_name,
            "created": Team.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Team.team_code,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_grade_sorted_paged(
        self,
        grade_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Team], int]:
        """
        Sorted + paginated list of teams for a grade.
        Returns (items, total).
        """
        stmt: SelectStmt = select(Team).where(Team.grade_id == grade_id)

        allowed: Mapping[str, Any] = {
            "code": Team.team_code,
            "name": Team.team_name,
            "created": Team.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Team.team_code,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Team:
        vals = dict(values)
        if not vals.get("team_code"):
            try:
                norm = getattr(TeamCreate, "normalize_team_code", None)
            except Exception:
                norm = None

            name = vals.get("team_name") or vals.get("name")
            if not name or not isinstance(name, str):
                raise ValueError("team_name is required to derive team_code")
            if callable(norm):
                vals["team_code"] = norm(name)
            else:
                import re

                s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                vals["team_code"] = re.sub(r"-+", "-", s)
        return super().create(vals)
