from __future__ import annotations

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import SlugStr


class CompetitionBase(ORMBase):
    """Shared, user-editable fields for a competition."""

    competition_name: str = Field(min_length=1)
    active: bool | None = True
    slug: SlugStr


class CompetitionCreate(CompetitionBase):
    """
    Create payload.
    Requires the parent organisation id.
    """

    organisation_id: int


class CompetitionUpdate(ORMBase):
    """Partial update — all fields optional."""

    competition_name: str | None = Field(default=None, min_length=1)
    active: bool | None = None
    slug: SlugStr | None = None


class CompetitionRead(CompetitionBase, CreatedStampedReadMixin):
    """Read payload with identifiers and audit fields."""

    competition_id: int
    organisation_id: int
