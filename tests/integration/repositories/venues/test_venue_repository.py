from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.venues.venues import Venue
from app.repositories.system.organisation_repository import OrganisationRepository
from app.repositories.venues.venue_repository import VenueRepository
from app.schemas._base import SortQuery


def test_venue_repository_scopes_sorting_paging(db_session: Session) -> None:
    org_repo = OrganisationRepository(db_session)
    venue_repo = VenueRepository(db_session)

    org = org_repo.create({"organisation_name": "Venues Org", "slug": "venues-org"})

    # Create three venues deliberately unsorted by display_order
    v_a = venue_repo.create(
        {
            "organisation_id": org.organisation_id,
            "venue_name": "Zeta Arena",
            "venue_address": "123 Main St",
            "display_order": 2,
            "total_courts": None,
        }
    )
    v_b = venue_repo.create(
        {
            "organisation_id": org.organisation_id,
            "venue_name": "Alpha Court",
            "venue_address": "124 Second Rd",
            "display_order": 1,
            "total_courts": None,
        }
    )
    v_c = venue_repo.create(
        {
            "organisation_id": org.organisation_id,
            "venue_name": "Beta Hall",
            "venue_address": "78 Willow Ct",
            "display_order": 3,
            "total_courts": None,
        }
    )

    # list_for_org: ordered by display_order ASC, then venue_name ASC
    rows = venue_repo.list_for_org(org.organisation_id)
    assert [r.venue_name for r in rows] == ["Alpha Court", "Zeta Arena", "Beta Hall"]

    # get_by_name_in_org convenience
    got = venue_repo.get_by_name_in_org(org.organisation_id, "Beta Hall")
    assert got is not None and got.venue_id == v_c.venue_id

    # list_for_org_sorted with sort='name' → alphabetical by name (tiebreaker stable by PK)
    rows_by_name = venue_repo.list_for_org_sorted(org.organisation_id, sort=SortQuery(order_by="name", direction="asc"))
    assert [r.venue_name for r in rows_by_name] == [
        "Alpha Court",
        "Beta Hall",
        "Zeta Arena",
    ]

    # list_for_org_sorted_paged (items + total)
    p1, total = venue_repo.list_for_org_sorted_paged(
        org.organisation_id,
        sort=SortQuery(order_by="name", direction="asc"),
        page=1,
        per_page=2,
    )
    p2, total2 = venue_repo.list_for_org_sorted_paged(
        org.organisation_id,
        sort=SortQuery(order_by="name", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [r.venue_name for r in p1] == ["Alpha Court", "Beta Hall"]
    assert [r.venue_name for r in p2] == ["Zeta Arena"]

    # list_ordered with a WHERE filter (restrict to this org)
    rows_ordered = venue_repo.list_ordered(where=(Venue.organisation_id == org.organisation_id,))
    # display_order ASC → IDs align to b(1), a(2), c(3)
    assert [r.venue_id for r in rows_ordered] == [
        v_b.venue_id,
        v_a.venue_id,
        v_c.venue_id,
    ]
