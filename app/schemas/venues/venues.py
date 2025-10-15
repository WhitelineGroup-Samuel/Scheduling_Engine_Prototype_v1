from __future__ import annotations

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.types import Latitude, Longitude, NonEmptyStr, NonNegInt


class VenueBase(ORMBase):
    """
    Client-editable fields for a venue.
    """

    organisation_id: int
    venue_name: NonEmptyStr
    venue_address: NonEmptyStr
    display_order: NonNegInt
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    indoor: bool | None = True
    accessible: bool | None = True
    total_courts: NonNegInt = Field(..., description="Maintained count of courts at the venue")


class VenueCreate(VenueBase):
    """
    Create payload for Venue.
    `created_by_user_id` is set by the service layer from the current user.
    """

    pass


class VenueUpdate(ORMBase):
    """
    Partial update for Venue — all fields optional.
    """

    organisation_id: int | None = None
    venue_name: NonEmptyStr | None = None
    venue_address: NonEmptyStr | None = None
    display_order: NonNegInt | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    indoor: bool | None = None
    accessible: bool | None = None
    total_courts: NonNegInt | None = None


class VenueRead(VenueBase, CreatedStampedReadMixin):
    """
    Read payload for Venue (includes identifiers and audit fields).
    """

    venue_id: int
