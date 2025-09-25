"""Organisation-specific DTOs and helpers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from pydantic import field_validator, model_validator

from app.schemas.common import (
    BaseDTO,
    PaginationMeta,
    TimestampsDTO,
    ensure_utc,
)

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from app.models.core import Organisation as OrganisationModel

__all__ = [
    "OrganisationInDTO",
    "OrganisationUpdateDTO",
    "OrganisationOutDTO",
    "OrganisationListOutDTO",
    "to_create_params",
]

_MAX_NAME_LENGTH = 200
_MAX_SLUG_LENGTH = 200
_SLUG_SANITISE_PATTERN = re.compile(r"[^a-z0-9]+")
_VALID_SLUG_PATTERN = re.compile(r"^[a-z0-9-]+$")


def _normalise_slug(value: str) -> str:
    """Normalise a string into the canonical slug representation."""

    candidate = value.strip().lower()
    candidate = _SLUG_SANITISE_PATTERN.sub("-", candidate)
    candidate = re.sub(r"-+", "-", candidate)
    candidate = candidate.strip("-")

    if not candidate:
        raise ValueError("Slug cannot be empty after normalisation")
    if len(candidate) > _MAX_SLUG_LENGTH:
        raise ValueError("Slug must be at most 200 characters long")
    if not _VALID_SLUG_PATTERN.fullmatch(candidate):
        raise ValueError("Slug may only contain lowercase letters, digits, and hyphens")
    return candidate


class OrganisationInDTO(BaseDTO):
    """Input DTO for provisioning a new organisation record."""

    name: str
    slug: str | None = None

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        """Ensure the organisation name meets formatting rules."""

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Organisation name cannot be empty")
        if len(cleaned) > _MAX_NAME_LENGTH:
            raise ValueError("Organisation name must be at most 200 characters long")
        return cleaned

    @field_validator("slug", mode="before")
    @classmethod
    def _validate_slug(cls, value: str | None) -> str | None:
        """Normalise provided slugs or defer derivation to the service layer."""

        if value is None:
            return None
        cleaned = value.strip()
        return _normalise_slug(cleaned) if cleaned else None


class OrganisationUpdateDTO(BaseDTO):
    """Patch-style DTO for updating an existing organisation."""

    name: str | None = None
    slug: str | None = None

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str | None) -> str | None:
        """Apply the same validation rules as creation when name is provided."""

        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Organisation name cannot be empty")
        if len(cleaned) > _MAX_NAME_LENGTH:
            raise ValueError("Organisation name must be at most 200 characters long")
        return cleaned

    @field_validator("slug", mode="before")
    @classmethod
    def _validate_slug(cls, value: str | None) -> str | None:
        """Normalise slugs on update to maintain canonical formatting."""

        if value is None:
            return None
        cleaned = value.strip()
        return _normalise_slug(cleaned) if cleaned else None

    @model_validator(mode="after")
    def _ensure_any_field(self) -> "OrganisationUpdateDTO":
        """Reject payloads that do not provide any fields to update."""

        if self.name is None and self.slug is None:
            raise ValueError("At least one of 'name' or 'slug' must be provided")
        return self


class OrganisationOutDTO(TimestampsDTO):
    """DTO used when returning organisation records to callers."""

    id: int
    name: str
    slug: str

    @classmethod
    def from_orm_row(cls, row: "OrganisationModel") -> "OrganisationOutDTO":
        """Create an output DTO from an ORM instance."""

        created_at = getattr(row, "created_at", None)
        updated_at = getattr(row, "updated_at", None)
        if created_at is None or updated_at is None:
            raise ValueError("Organisation row must include timestamps")
        return cls(
            id=int(getattr(row, "organisation_id")),
            name=str(getattr(row, "organisation_name")),
            slug=str(getattr(row, "slug")),
            created_at=ensure_utc(created_at),
            updated_at=ensure_utc(updated_at),
        )

    @staticmethod
    def normalize_slug(name_or_slug: str) -> str:
        """Public slug normalisation helper for service and CLI layers."""

        return _normalise_slug(name_or_slug)


class OrganisationListOutDTO(BaseDTO):
    """Paginated list response for organisation queries."""

    items: list[OrganisationOutDTO]
    meta: PaginationMeta


def to_create_params(dto: OrganisationInDTO) -> dict[str, Any]:
    """Render repository parameters for an organisation creation request."""

    slug = dto.slug or OrganisationOutDTO.normalize_slug(dto.name)
    return {
        "organisation_name": dto.name,
        "slug": slug,
    }
