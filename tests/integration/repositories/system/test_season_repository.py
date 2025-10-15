from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.repositories.system.competition_repository import CompetitionRepository
from app.repositories.system.organisation_repository import OrganisationRepository
from app.repositories.system.season_repository import SeasonRepository
from app.schemas._base import SortQuery
from app.schemas.enums import SeasonVisibility


def test_season_list_for_competition_and_sorting(db_session: Session) -> None:
    org_repo = OrganisationRepository(db_session)
    comp_repo = CompetitionRepository(db_session)
    season_repo = SeasonRepository(db_session)

    org = org_repo.create({"organisation_name": "Org Seasons", "slug": "org-seasons"})
    comp = comp_repo.create(
        {
            "organisation_id": org.organisation_id,
            "competition_name": "Premier",
            "slug": "premier",
        }
    )

    # Create seasons with explicit starting_date so we can assert chronological order
    _s1 = season_repo.create(
        {
            "competition_id": comp.competition_id,
            "season_name": "2024 Term 1",
            "starting_date": date(2024, 1, 10),
            "visibility": SeasonVisibility.PUBLIC,
            "slug": None,
        }
    )
    _s2 = season_repo.create(
        {
            "competition_id": comp.competition_id,
            "season_name": "2024 Term 3",
            "starting_date": date(2024, 7, 1),
            "visibility": SeasonVisibility.INTERNAL,
            "slug": None,
        }
    )
    _s3 = season_repo.create(
        {
            "competition_id": comp.competition_id,
            "season_name": "2024 Term 2",
            "starting_date": date(2024, 4, 15),
            "visibility": SeasonVisibility.PRIVATE,
            "slug": None,
        }
    )

    # list_for_competition: chronological then fallback by name (we only need chronological here)
    lst = season_repo.list_for_competition(comp.competition_id)
    assert [s.season_name for s in lst] == ["2024 Term 1", "2024 Term 2", "2024 Term 3"]

    # list_ordered mirrors that ordering for all rows
    ordered = season_repo.list_ordered()
    assert [s.season_name for s in ordered] == [
        "2024 Term 1",
        "2024 Term 2",
        "2024 Term 3",
    ]

    # list_for_competition_sorted (string sort "start" or default)
    sorted_default = season_repo.list_for_competition_sorted(comp.competition_id, sort=None)
    assert [s.season_name for s in sorted_default] == [
        "2024 Term 1",
        "2024 Term 2",
        "2024 Term 3",
    ]

    # list_for_competition_sorted_paged
    page1, total = season_repo.list_for_competition_sorted_paged(
        comp.competition_id,
        sort=SortQuery(order_by="start", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = season_repo.list_for_competition_sorted_paged(
        comp.competition_id,
        sort=SortQuery(order_by="start", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [s.season_name for s in page1] == ["2024 Term 1", "2024 Term 2"]
    assert [s.season_name for s in page2] == ["2024 Term 3"]
