from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from sqlalchemy import select

from app.models.taxonomy.grades import Grade
from app.repositories.base import BaseRepository
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery
from app.schemas.taxonomy.grades import GradeCreate


class GradeRepository(BaseRepository[Grade]):
    """
    Data access for Grade rows.

    Helpers:
    - list_for_age_ordered(age_id): ordered by grade_rank ASC, then grade_name ASC
    - list_ordered(): generic ordered list with optional filters
    - get_by_name_in_age(age_id, grade_name): optional convenience lookup
    """

    model = Grade

    # ---- Queries ----
    def list_for_age_ordered(self, age_id: int) -> list[Grade]:
        stmt: SelectStmt = select(Grade).where(Grade.age_id == age_id)
        stmt = stmt.order_by(
            Grade.grade_rank.asc(),
            Grade.grade_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Grade]:
        stmt: SelectStmt = select(Grade)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(
            Grade.grade_rank.asc(),
            Grade.grade_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def get_by_name_in_age(self, age_id: int, grade_name: str) -> Grade | None:
        """
        Convenience lookup when UI treats names as unique within an age group.
        Returns None if there is no exact name match under this age.
        """
        stmt: SelectStmt = select(Grade).where(Grade.age_id == age_id).where(Grade.grade_name == grade_name)
        return cast(Grade | None, self.session.execute(stmt).scalar_one_or_none())

    def list_for_age_sorted(
        self,
        age_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Grade]:
        """
        Sorted list of grades for an age.
        Allowed sort keys: 'rank', 'name', 'created'.
        Default: rank ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(Grade).where(Grade.age_id == age_id)

        allowed: Mapping[str, Any] = {
            "rank": Grade.grade_rank,
            "name": Grade.grade_name,
            "created": Grade.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Grade.grade_rank,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_age_sorted_paged(
        self,
        age_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Grade], int]:
        """
        Sorted + paginated list of grades for an age.
        Returns (items, total).
        """
        stmt: SelectStmt = select(Grade).where(Grade.age_id == age_id)

        allowed: Mapping[str, Any] = {
            "rank": Grade.grade_rank,
            "name": Grade.grade_name,
            "created": Grade.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Grade.grade_rank,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Grade:
        vals = dict(values)
        if not vals.get("grade_code"):
            try:
                norm = getattr(GradeCreate, "normalize_grade_code", None)
            except Exception:
                norm = None

            name = vals.get("grade_name") or vals.get("name")
            if not name or not isinstance(name, str):
                raise ValueError("grade_name is required to derive grade_code")
            if callable(norm):
                vals["grade_code"] = norm(name)
            else:
                import re

                s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                vals["grade_code"] = re.sub(r"-+", "-", s)
        return super().create(vals)
