from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from sqlalchemy import select

from app.models.venues.courts import Court
from app.repositories.base import BaseRepository
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class CourtRepository(BaseRepository[Court]):
    """
    Data access for Court rows.

    Helpers:
    - list_for_venue(venue_id): ordered by display_order ASC, then court_name ASC
    - list_ordered(): generic ordered list with optional filters
    - get_by_name_in_venue(venue_id, court_name): soft AK within a venue
    """

    model = Court

    # ---- Queries ----
    def list_for_venue(self, venue_id: int) -> list[Court]:
        stmt: SelectStmt = select(Court).where(Court.venue_id == venue_id)
        stmt = stmt.order_by(
            Court.display_order.asc(),
            Court.court_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Court]:
        stmt: SelectStmt = select(Court)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(
            Court.display_order.asc(),
            Court.court_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def get_by_name_in_venue(self, venue_id: int, court_name: str) -> Court | None:
        """
        Convenience lookup when UI treats names as unique within a venue.
        Returns None if there is no exact name match in this venue.
        """
        stmt: SelectStmt = select(Court).where(Court.venue_id == venue_id).where(Court.court_name == court_name)
        return cast(Court | None, self.session.execute(stmt).scalar_one_or_none())

    def list_for_venue_sorted(
        self,
        venue_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Court]:
        """
        Sorted list of courts in a venue.
        Allowed sort keys: 'order' (display_order), 'name', 'created'.
        Default: display_order ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(Court).where(Court.venue_id == venue_id)

        allowed: Mapping[str, Any] = {
            "order": Court.display_order,
            "name": Court.court_name,
            "created": Court.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Court.display_order,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_venue_sorted_paged(
        self,
        venue_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Court], int]:
        """
        Sorted + paginated list of courts in a venue.
        Returns (items, total).
        """
        stmt: SelectStmt = select(Court).where(Court.venue_id == venue_id)

        allowed: Mapping[str, Any] = {
            "order": Court.display_order,
            "name": Court.court_name,
            "created": Court.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Court.display_order,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Court:
        vals = dict(values)
        if not vals.get("court_code"):
            # Try from court_name or a numeric field
            name = vals.get("court_name")
            number = vals.get("court_number")
            if isinstance(number, int):
                vals["court_code"] = f"C{number}"
            elif isinstance(name, str) and name.strip():
                vals["court_code"] = name.strip()
            else:
                vals["court_code"] = "Court"

        return super().create(vals)
