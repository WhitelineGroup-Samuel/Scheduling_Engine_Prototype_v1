"""Concrete repository for interacting with :class:`Organisation` rows."""

from __future__ import annotations

import re
from typing import Any, cast

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement

from app.models.core import Organisation
from app.repositories.base_repository import BaseRepository

__all__ = ["OrganisationRepository"]

_MAX_SLUG_LENGTH = 200
_SLUG_SANITISE_PATTERN = re.compile(r"[^a-z0-9]+")
_VALID_SLUG_PATTERN = re.compile(r"^[a-z0-9-]+$")


def _normalise_name(value: str) -> str:
    """Normalise organisation names before persistence or lookup."""

    cleaned = " ".join(value.split()) if value else ""
    cleaned = cleaned.strip()
    if not cleaned:
        raise ValueError("name required")
    return cleaned


def _normalise_slug(value: str) -> str:
    """Normalise slug strings to the canonical lowercase hyphenated form."""

    candidate = value.strip().lower()
    candidate = _SLUG_SANITISE_PATTERN.sub("-", candidate)
    candidate = re.sub(r"-+", "-", candidate)
    candidate = candidate.strip("-")
    if not candidate:
        raise ValueError("slug required")
    if len(candidate) > _MAX_SLUG_LENGTH:
        raise ValueError("slug must be at most 200 characters long")
    if not _VALID_SLUG_PATTERN.fullmatch(candidate):
        raise ValueError("slug may only contain lowercase letters, digits, and hyphens")
    return candidate


class OrganisationRepository(BaseRepository):
    """Data-access helpers for the ``organisations`` table."""

    def get_by_id(self, session: Session, organisation_id: int) -> Organisation | None:
        # Good as-is, but if mypy still complains, wrap with cast:
        # return cast(Organisation | None, session.get(Organisation, organisation_id))
        result: Organisation | None = session.get(Organisation, organisation_id)
        return result

    def get_by_name(self, session: Session, name: str) -> Organisation | None:
        cleaned = _normalise_name(name)
        stmt: Select[Any] = select(Organisation).where(
            Organisation.organisation_name == cleaned
        )
        # ↓↓↓ switch to scalars().one_or_none() so the result is typed as Organisation | None
        return cast(Organisation | None, session.execute(stmt).scalars().one_or_none())

    def get_by_slug(self, session: Session, slug: str) -> Organisation | None:
        normalised = _normalise_slug(slug)
        stmt: Select[Any] = select(Organisation).where(Organisation.slug == normalised)
        # ↓↓↓ same pattern here
        return cast(Organisation | None, session.execute(stmt).scalars().one_or_none())

    def list(
        self,
        session: Session,
        *,
        page: int = 1,
        page_size: int = 50,
        sort: str | None = "name",
        search: str | None = None,
    ) -> tuple[list[Organisation], int]:
        """Return a paginated collection of organisations."""

        stmt: Select[Any] = select(Organisation)
        if search:
            term = search.strip()
            if term:
                like_pattern = f"%{term}%"
                stmt = stmt.where(
                    Organisation.organisation_name.ilike(like_pattern)
                    | Organisation.slug.ilike(like_pattern)
                )
        allowed: dict[str, ColumnElement[Any]] = {
            "name": cast(ColumnElement[Any], Organisation.organisation_name),
            "created_at": cast(ColumnElement[Any], Organisation.created_at),
            "updated_at": cast(ColumnElement[Any], Organisation.updated_at),
        }
        effective_sort = sort or "name"
        stmt = self.apply_sorting(stmt, sort=effective_sort, allowed=allowed)
        stmt = stmt.order_by(Organisation.organisation_id.asc())
        raw_items, total = self.apply_pagination(
            stmt,
            session=session,
            page=page,
            page_size=page_size,
            max_page_size=100,
        )
        items = [cast(Organisation, item) for item in raw_items]
        return items, total

    def create(
        self,
        session: Session,
        *,
        name: str,
        slug: str | None = None,
    ) -> Organisation:
        """Insert a new organisation row."""

        cleaned_name = _normalise_name(name)
        final_slug = (
            _normalise_slug(slug) if slug is not None else _normalise_slug(cleaned_name)
        )
        instance = Organisation(
            organisation_name=cleaned_name,
            slug=final_slug,
        )
        self.add(session, instance)
        session.flush()
        return self.refresh(session, instance)

    def update(
        self,
        session: Session,
        organisation_id: int,
        *,
        name: str | None = None,
        slug: str | None = None,
    ) -> Organisation:
        """Update an existing organisation by primary key."""

        stmt: Select[Any] = select(Organisation).where(
            Organisation.organisation_id == organisation_id
        )
        instance: Organisation = session.execute(stmt).scalar_one()

        if name is not None:
            instance.organisation_name = _normalise_name(name)
        if slug is not None:
            instance.slug = _normalise_slug(slug)

        session.flush()
        session.refresh(instance)
        return instance

    def upsert_by_name(
        self,
        session: Session,
        *,
        name: str,
        slug: str | None = None,
    ) -> Organisation:
        """Create or update an organisation addressed by its name."""

        cleaned_name = _normalise_name(name)
        existing = self.get_by_name(session, cleaned_name)
        if existing is not None:
            slug_changed = False
            normalised_slug: str | None = None
            if slug is not None:
                normalised_slug = _normalise_slug(slug)
                slug_changed = normalised_slug != existing.slug
            name_changed = existing.organisation_name != cleaned_name
            if name_changed or slug_changed:
                return self.update(
                    session,
                    existing.organisation_id,
                    name=cleaned_name if name_changed else None,
                    slug=normalised_slug if slug_changed else None,
                )
            return existing

        try:
            return self.create(session, name=cleaned_name, slug=slug)
        except IntegrityError:
            refetched = self.get_by_name(session, cleaned_name)
            if refetched is not None:
                return refetched
            raise

    def delete(self, session: Session, instance: Organisation) -> None:
        """Delete an organisation instance."""
        super().delete(session, instance)

    def delete_by_id(self, session: Session, organisation_id: int) -> None:
        """Delete an organisation by its primary key."""
        stmt: Select[Any] = select(Organisation).where(
            Organisation.organisation_id == organisation_id
        )
        instance: Organisation = session.execute(stmt).scalar_one()
        self.delete(session, instance)
