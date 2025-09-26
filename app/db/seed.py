"""
===============================================================================
File: app/db/seed.py
Purpose
-------
Deterministic, idempotent seed routines for development and test databases.
===============================================================================
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.organisation_repository import OrganisationRepository
from app.schemas.organisation import OrganisationInDTO

__all__ = ["OrganisationSeed", "SeedPlan", "seed_minimal", "seed_from_plan"]

_DEFAULT_ORG_NAME = "Whiteline Demo"
_SLUG_SANITISE_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class OrganisationSeed:
    """Declarative description of an organisation to ensure exists."""

    name: str
    slug: str | None = None


@dataclass(slots=True)
class SeedPlan:
    organisations: Sequence[OrganisationSeed] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        self.organisations = tuple(self.organisations)


def _fallback_normalize_slug(value: str) -> str:
    """Best-effort slug normaliser mirroring DTO behaviour."""

    slug = _SLUG_SANITISE_RE.sub("-", value.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise ValueError("Unable to derive slug from organisation name")
    return slug


def _normalize_inputs(name: str, slug: str | None) -> tuple[str, str]:
    """Validate and normalise organisation name/slug values via DTO rules."""

    dto = OrganisationInDTO(name=name, slug=slug)
    normalised_name = dto.name
    derived_slug = dto.slug
    if not derived_slug:
        normaliser = getattr(OrganisationInDTO, "normalize_slug", None)
        if callable(normaliser):
            derived_slug = normaliser(normalised_name)
        else:
            derived_slug = _fallback_normalize_slug(normalised_name)
    assert isinstance(derived_slug, str)
    return normalised_name, derived_slug


def _get_attr(entity: Any, *candidates: str) -> Any:
    for candidate in candidates:
        if hasattr(entity, candidate):
            return getattr(entity, candidate)
    return None


def _summarise_org(entity: Any) -> dict[str, Any]:
    identifier = _get_attr(entity, "id", "organisation_id")
    name_value = _get_attr(entity, "name", "organisation_name")
    slug_value = _get_attr(entity, "slug", "organisation_slug")
    return {
        "id": str(identifier) if identifier is not None else None,
        "name": name_value,
        "slug": slug_value,
    }


def _ensure_organisation(
    session: Session,
    repository: OrganisationRepository,
    *,
    name: str,
    slug: str | None,
) -> tuple[str, Any]:
    """Insert or update an organisation record, returning the resulting action."""

    normalised_name, normalised_slug = _normalize_inputs(name, slug)
    existing = repository.get_by_name(session, normalised_name)
    if existing is None:
        created = repository.create(session, name=normalised_name, slug=normalised_slug)
        session.flush()
        session.refresh(created)
        return "inserted", created

    updates: dict[str, str] = {}
    current_name = _get_attr(existing, "name", "organisation_name")
    if current_name != normalised_name:
        updates["name"] = normalised_name
    current_slug = _get_attr(existing, "slug", "organisation_slug")
    if current_slug != normalised_slug:
        updates["slug"] = normalised_slug

    if updates:
        identifier = _get_attr(existing, "id", "organisation_id")
        if identifier is None:
            raise ValueError("Organisation row is missing a primary key identifier")
        updated = repository.update(session, identifier, **updates)
        session.flush()
        session.refresh(updated)
        return "updated", updated

    return "skipped", existing


def seed_minimal(session: Session, *, org_name: str | None = None) -> dict[str, Any]:
    """Ensure the presence of a single demonstration organisation.

    Parameters
    ----------
    session:
        Active SQLAlchemy session opened by the caller.
    org_name:
        Optional explicit organisation name. When omitted the default
        ``Whiteline Demo`` name is used.

    Returns
    -------
    dict[str, Any]
        Summary containing ``inserted``, ``updated``, ``skipped`` counters and
        a list of affected organisation descriptors.
    """

    base_name = org_name if org_name is not None else _DEFAULT_ORG_NAME
    effective_name = base_name.strip()
    if not effective_name:
        raise ValueError("Organisation name must not be empty")

    plan = SeedPlan(organisations=(OrganisationSeed(name=effective_name),))
    return seed_from_plan(session, plan)


def seed_from_plan(session: Session, plan: SeedPlan) -> dict[str, Any]:
    """Execute the provided seed plan within the caller's transaction.

    Parameters
    ----------
    session:
        Active SQLAlchemy session supplied by the caller.
    plan:
        Declarative plan containing the entities that must exist.

    Returns
    -------
    dict[str, Any]
        Aggregated summary of insert/update/skip counts and entity descriptors.
    """

    repository = OrganisationRepository()
    counts: dict[str, int] = {"inserted": 0, "updated": 0, "skipped": 0}
    items: list[dict[str, Any]] = []

    for org_seed in plan.organisations:
        action, entity = _ensure_organisation(
            session,
            repository,
            name=org_seed.name,
            slug=org_seed.slug,
        )
        counts[action] += 1
        items.append(_summarise_org(entity))

    return {**counts, "items": items}
