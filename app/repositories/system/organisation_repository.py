from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

from sqlalchemy import select

from app.models.system.organisations import Organisation
from app.repositories.base import BaseRepository
from app.repositories.typing import SelectStmt
from app.schemas._base import SortQuery


class OrganisationRepository(BaseRepository[Organisation]):
    """
    Data access for Organisation rows.

    Helpers:
    - get_by_slug(slug): alternate-key lookup
    - list_ordered(): ordered by organisation_name ASC
    """

    model = Organisation

    def get_by_slug(self, slug: str) -> Organisation | None:
        stmt: SelectStmt = select(Organisation).where(Organisation.slug == slug)
        return cast(Organisation | None, self.session.execute(stmt).scalar_one_or_none())

    def list_ordered(self, *, where: Iterable[Any] = ()) -> list[Organisation]:
        stmt: SelectStmt = select(Organisation)
        for cond in where:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(Organisation.organisation_name.asc())
        return list(self.session.execute(stmt).scalars())

    def list_sorted(self, *, sort: SortQuery | None) -> list[Organisation]:
        stmt: SelectStmt = select(Organisation)
        allowed: Mapping[str, Any] = {
            "name": Organisation.organisation_name,
            "slug": Organisation.slug,
            "created": Organisation.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Organisation.organisation_name,  # <- column-like default
        )
        return list(self.session.execute(stmt).scalars())

    def list_sorted_paged(self, *, sort: SortQuery | None, page: int, per_page: int) -> tuple[list[Organisation], int]:
        stmt: SelectStmt = select(Organisation)
        allowed: Mapping[str, Any] = {
            "name": Organisation.organisation_name,
            "slug": Organisation.slug,
            "created": Organisation.created_at,
        }
        stmt = self.apply_sorting(
            stmt,
            sort=sort,
            allowed=allowed,
            default=Organisation.organisation_name,
        )
        return self.paginate_items_total(stmt, page=page, per_page=per_page)

    def create(self, values: dict[str, Any]) -> Organisation:
        """
        Create an Organisation, deriving a slug from the name if not provided.
        Also benefits from BaseRepository auto-attribution for created_by_user_id.
        """
        vals = dict(values)
        # Derive slug if missing
        if "slug" not in vals or not vals["slug"]:
            from app.schemas.system.organisations import (
                OrganisationCreate,  # local import
            )

            # Prefer the DTO's normaliser if present; else basic fallback
            normaliser = getattr(OrganisationCreate, "normalize_slug", None)
            name = vals.get("organisation_name") or vals.get("name")
            if not name or not isinstance(name, str):
                raise ValueError("organisation_name is required to derive slug")
            if callable(normaliser):
                vals["slug"] = normaliser(name)
            else:
                import re

                slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                slug = re.sub(r"-+", "-", slug)
                if not slug:
                    raise ValueError("Unable to derive slug from organisation_name")
                vals["slug"] = slug

        return super().create(vals)
