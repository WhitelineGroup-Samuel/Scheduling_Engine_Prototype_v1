from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.system.competition_repository import CompetitionRepository
from app.repositories.system.organisation_repository import OrganisationRepository
from app.schemas._base import SortQuery


def test_competition_list_scopes_and_sorting(db_session: Session) -> None:
    org_repo = OrganisationRepository(db_session)
    comp_repo = CompetitionRepository(db_session)

    org = org_repo.create({"organisation_name": "Comp Owner", "slug": "comp-owner"})
    # Create competitions deliberately out of order
    _c1 = comp_repo.create({"organisation_id": org.organisation_id, "competition_name": "Summer League"})
    _c2 = comp_repo.create({"organisation_id": org.organisation_id, "competition_name": "Autumn Cup"})
    _c3 = comp_repo.create({"organisation_id": org.organisation_id, "competition_name": "Winter Series"})

    # list_for_org: ordered by competition_name ASC
    lst = comp_repo.list_for_org(org.organisation_id)
    assert [c.competition_name for c in lst] == [
        "Autumn Cup",
        "Summer League",
        "Winter Series",
    ]

    # list_ordered should match same behavior without filters when no 'where' given
    ordered = comp_repo.list_ordered()
    assert [c.competition_name for c in ordered] == [
        "Autumn Cup",
        "Summer League",
        "Winter Series",
    ]

    # list_for_org_sorted (string sort key "name")
    sorted_by_name = comp_repo.list_for_org_sorted(org.organisation_id, sort=SortQuery(order_by="name", direction="asc"))
    assert [c.competition_name for c in sorted_by_name] == [
        "Autumn Cup",
        "Summer League",
        "Winter Series",
    ]

    # list_for_org_sorted_paged
    page1, total = comp_repo.list_for_org_sorted_paged(
        org.organisation_id,
        sort=SortQuery(order_by="name", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = comp_repo.list_for_org_sorted_paged(
        org.organisation_id,
        sort=SortQuery(order_by="name", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [c.competition_name for c in page1] == ["Autumn Cup", "Summer League"]
    assert [c.competition_name for c in page2] == ["Winter Series"]
