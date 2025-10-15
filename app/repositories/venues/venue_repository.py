from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from sqlalchemy import select

from app.models.venues.venues import Venue
from app.repositories.base import BaseRepository
from app.repositories.mixins import OrderingMixin, OrgScopedMixin
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class VenueRepository(BaseRepository[Venue], OrgScopedMixin, OrderingMixin):
    """
    Data access for Venue rows.

    Scopes:
    - where_org(stmt, organisation_id)

    Helpers:
    - list_for_org(organisation_id): ordered by display_order ASC, then venue_name ASC
    - get_by_name_in_org(organisation_id, venue_name): soft AK within org (None if not found)
    """

    model = Venue

    # ---- OrgScopedMixin contract ----
    def org_id_column(self) -> Any:
        return Venue.organisation_id

    # ---- Queries ----
    def list_for_org(self, organisation_id: int) -> list[Venue]:
        stmt: SelectStmt = select(Venue)
        stmt = self.where_org(stmt, organisation_id)
        stmt = self.order_by(
            stmt,
            Venue.display_order.asc(),
            Venue.venue_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Venue]:
        stmt: SelectStmt = select(Venue)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = self.order_by(
            stmt,
            Venue.display_order.asc(),
            Venue.venue_name.asc(),
        )
        return list(self.session.execute(stmt).scalars())

    def get_by_name_in_org(self, organisation_id: int, venue_name: str) -> Venue | None:
        """
        Convenience lookup when UI treats names as unique within an org.
        Returns None if there is no exact name match in this organisation.
        """
        stmt: SelectStmt = select(Venue).where(Venue.organisation_id == organisation_id).where(Venue.venue_name == venue_name)
        return cast(Venue | None, self.session.execute(stmt).scalar_one_or_none())

    def list_for_org_sorted(
        self,
        organisation_id: int,
        *,
        sort: SortQuery | None,
    ) -> list[Venue]:
        """
        Sorted list of venues within an organisation.
        Allowed sort keys: 'order' (display_order), 'name', 'created'.
        Default: display_order ASC (PK tie added automatically if needed).
        """
        stmt: SelectStmt = select(Venue).where(Venue.organisation_id == organisation_id)

        allowed: Mapping[str, Any] = {
            "order": Venue.display_order,
            "name": Venue.venue_name,
            "created": Venue.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Venue.display_order,
        )
        return list(self.session.execute(stmt).scalars())

    def list_for_org_sorted_paged(
        self,
        organisation_id: int,
        *,
        sort: SortQuery | None,
        page: int,
        per_page: int,
    ) -> tuple[list[Venue], int]:
        """
        Sorted + paginated list of venues within an organisation.
        Returns (items, total).
        """
        stmt: SelectStmt = select(Venue).where(Venue.organisation_id == organisation_id)

        allowed: Mapping[str, Any] = {
            "order": Venue.display_order,
            "name": Venue.venue_name,
            "created": Venue.created_at,
        }

        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Venue.display_order,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Venue:
        vals = dict(values)
        if not vals.get("total_courts"):
            # Conservative default; tests can override
            vals["total_courts"] = 1

        return super().create(vals)
