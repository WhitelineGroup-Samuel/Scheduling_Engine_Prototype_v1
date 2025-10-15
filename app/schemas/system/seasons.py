from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import SlugStr

# The ERD constrains visibility to PRIVATE/INTERNAL/PUBLIC.
SeasonVisibility = Literal["PRIVATE", "INTERNAL", "PUBLIC"]


class SeasonBase(ORMBase):
    """Shared, user-editable fields for a season."""

    season_name: str = Field(min_length=1)
    starting_date: date | None = None
    ending_date: date | None = None
    visibility: SeasonVisibility
    active: bool | None = True
    slug: SlugStr


class SeasonCreate(SeasonBase):
    """
    Create payload.
    Requires the parent competition id.
    """

    competition_id: int


class SeasonUpdate(ORMBase):
    """Partial update — all fields optional."""

    season_name: str | None = Field(default=None, min_length=1)
    starting_date: date | None = None
    ending_date: date | None = None
    visibility: SeasonVisibility | None = None
    active: bool | None = None
    slug: SlugStr | None = None


class SeasonRead(SeasonBase, CreatedStampedReadMixin):
    """Read payload with identifiers and audit fields."""

    season_id: int
    competition_id: int
