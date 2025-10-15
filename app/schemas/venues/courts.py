from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import Code20, NonEmptyStr, NonNegInt


class CourtBase(ORMBase):
    """
    Client-editable fields for a court.
    """

    venue_id: int
    court_code: Code20
    court_name: NonEmptyStr
    display_order: NonNegInt
    surface: str | None = None
    indoor: bool | None = True
    active: bool | None = True


class CourtCreate(CourtBase):
    """
    Create payload for Court.
    """

    pass


class CourtUpdate(ORMBase):
    """
    Partial update for Court — all fields optional.
    """

    venue_id: int | None = None
    court_code: Code20 | None = None
    court_name: NonEmptyStr | None = None
    display_order: NonNegInt | None = None
    surface: str | None = None
    indoor: bool | None = None
    active: bool | None = None


class CourtRead(CourtBase, CreatedStampedReadMixin):
    """
    Read payload for Court (includes identifiers and audit fields).
    """

    court_id: int
