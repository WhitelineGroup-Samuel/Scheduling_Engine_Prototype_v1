from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.venues.courts import Court
from app.repositories.system.organisation_repository import OrganisationRepository
from app.repositories.venues.court_repository import CourtRepository
from app.repositories.venues.venue_repository import VenueRepository
from app.schemas._base import SortQuery


def test_court_repository_scopes_sorting_paging(db_session: Session) -> None:
    org_repo = OrganisationRepository(db_session)
    venue_repo = VenueRepository(db_session)
    court_repo = CourtRepository(db_session)

    org = org_repo.create({"organisation_name": "Court Org", "slug": "court-org"})
    venue = venue_repo.create(
        {
            "organisation_id": org.organisation_id,
            "venue_name": "Main Venue",
            "display_order": 1,
            "venue_address": "123 Main St",
            "total_courts": 3,
        }
    )

    c1 = court_repo.create({"venue_id": venue.venue_id, "court_name": "Zeta", "display_order": 2})
    c2 = court_repo.create({"venue_id": venue.venue_id, "court_name": "Alpha", "display_order": 1})
    c3 = court_repo.create({"venue_id": venue.venue_id, "court_name": "Beta", "display_order": 3})

    # list_for_venue: ordered by display_order ASC, then court_name ASC
    rows = court_repo.list_for_venue(venue.venue_id)
    assert [r.court_name for r in rows] == ["Alpha", "Zeta", "Beta"]

    # get_by_name_in_venue convenience
    got = court_repo.get_by_name_in_venue(venue.venue_id, "Beta")
    assert got is not None and got.court_id == c3.court_id

    # list_for_venue_sorted with sort='name'
    rows_by_name = court_repo.list_for_venue_sorted(venue.venue_id, sort=SortQuery(order_by="name", direction="asc"))
    assert [r.court_name for r in rows_by_name] == ["Alpha", "Beta", "Zeta"]

    # list_for_venue_sorted_paged (items + total)
    p1, total = court_repo.list_for_venue_sorted_paged(
        venue.venue_id,
        sort=SortQuery(order_by="name", direction="asc"),
        page=1,
        per_page=2,
    )
    p2, total2 = court_repo.list_for_venue_sorted_paged(
        venue.venue_id,
        sort=SortQuery(order_by="name", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [r.court_name for r in p1] == ["Alpha", "Beta"]
    assert [r.court_name for r in p2] == ["Zeta"]

    # list_ordered with a WHERE filter (restrict to this venue)
    rows_ordered = court_repo.list_ordered(where=(Court.venue_id == venue.venue_id,))
    # display_order ASC → IDs align to c2(1), c1(2), c3(3)
    assert [r.court_id for r in rows_ordered] == [c2.court_id, c1.court_id, c3.court_id]
