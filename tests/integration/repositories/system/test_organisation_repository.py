from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.system.organisation_repository import OrganisationRepository
from app.schemas._base import SortQuery


def test_create_get_by_slug_and_list_sorted(db_session: Session) -> None:
    repo = OrganisationRepository(db_session)

    # Create a few orgs (deliberately out of order).
    _o1 = repo.create({"organisation_name": "Zeta Org", "slug": "zeta-org"})
    _o2 = repo.create({"organisation_name": "Alpha Org", "slug": "alpha-org"})
    o3 = repo.create({"organisation_name": "Beta Org", "slug": "beta-org"})

    # get_by_slug
    got = repo.get_by_slug("beta-org")
    assert got is not None and got.organisation_id == o3.organisation_id

    # list_ordered (by organisation_name ASC)
    ordered = repo.list_ordered()
    assert [o.organisation_name for o in ordered] == [
        "Alpha Org",
        "Beta Org",
        "Zeta Org",
    ]

    # list_sorted (string sort param; defaults to name ASC with tiebreaker)
    sorted_by_default = repo.list_sorted(sort=None)
    assert [o.organisation_name for o in sorted_by_default] == [
        "Alpha Org",
        "Beta Org",
        "Zeta Org",
    ]

    # list_sorted_paged
    page1, total = repo.list_sorted_paged(sort=SortQuery(order_by="name", direction="asc"), page=1, per_page=2)
    page2, total2 = repo.list_sorted_paged(sort=SortQuery(order_by="name", direction="asc"), page=2, per_page=2)
    assert total == 3 and total2 == 3
    assert [o.organisation_name for o in page1] == ["Alpha Org", "Beta Org"]
    assert [o.organisation_name for o in page2] == ["Zeta Org"]
