# app/schemas/system/organisations.py

from __future__ import annotations

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import SlugStr


class OrganisationBase(ORMBase):
    """Shared, user-editable fields for an organisation."""

    organisation_name: str = Field(min_length=1)
    time_zone: str | None = None
    country_code: str | None = None
    slug: SlugStr


class OrganisationCreate(OrganisationBase):
    """
    Create payload.
    `created_by_user_id` is set by the service layer from the current user.
    """

    pass


class OrganisationUpdate(ORMBase):
    """Partial update — all fields optional."""

    organisation_name: str | None = Field(default=None, min_length=1)
    time_zone: str | None = None
    country_code: str | None = None
    slug: SlugStr | None = None


class OrganisationRead(OrganisationBase, CreatedStampedReadMixin):
    """Read payload with identifiers and audit fields."""

    organisation_id: int
