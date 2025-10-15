from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.timeplan.rounds import Round
from app.repositories.system.competition_repository import CompetitionRepository
from app.repositories.system.organisation_repository import OrganisationRepository
from app.repositories.system.season_repository import SeasonRepository
from app.repositories.timeplan.round_repository import RoundRepository
from app.schemas._base import SortQuery
from app.schemas.enums import RoundType, SeasonVisibility


def test_round_repository_scopes_sorting_paging(db_session: Session) -> None:
    org_repo = OrganisationRepository(db_session)
    comp_repo = CompetitionRepository(db_session)
    season_repo = SeasonRepository(db_session)
    round_repo = RoundRepository(db_session)

    org = org_repo.create({"organisation_name": "Timeplan Org", "slug": "timeplan-org"})
    comp = comp_repo.create(
        {
            "organisation_id": org.organisation_id,
            "competition_name": "League A",
            "slug": "league-a",
        }
    )
    season = season_repo.create(
        {
            "competition_id": comp.competition_id,
            "season_name": "2025 Term 1",
            "visibility": SeasonVisibility.PUBLIC,
            "slug": "2025-term-1",
        }
    )

    r2 = round_repo.create(
        {
            "season_id": season.season_id,
            "round_number": 2,
            "round_label": None,
            "round_type": RoundType.REGULAR,
        }
    )
    r1 = round_repo.create(
        {
            "season_id": season.season_id,
            "round_number": 1,
            "round_label": None,
            "round_type": RoundType.FINALS,
        }
    )
    r3 = round_repo.create(
        {
            "season_id": season.season_id,
            "round_number": 3,
            "round_label": None,
            "round_type": RoundType.GRADING,
        }
    )

    # list_for_season → by round_number ASC, then PK
    rows: list[Round] = round_repo.list_for_season(season.season_id)
    assert [r.round_number for r in rows] == [1, 2, 3]

    # list_ordered with WHERE filter
    rows2: list[Round] = round_repo.list_ordered(where=(Round.season_id == season.season_id,))
    assert [r.round_id for r in rows2] == [r1.round_id, r2.round_id, r3.round_id]

    # list_for_season_sorted (default / explicit "number")
    by_default: list[Round] = round_repo.list_for_season_sorted(season.season_id, sort=None)
    by_number: list[Round] = round_repo.list_for_season_sorted(season.season_id, sort=SortQuery(order_by="number", direction="asc"))
    assert [r.round_number for r in by_default] == [1, 2, 3]
    assert [r.round_number for r in by_number] == [1, 2, 3]

    # list_for_season_sorted_paged
    page1, total = round_repo.list_for_season_sorted_paged(
        season.season_id,
        sort=SortQuery(order_by="number", direction="asc"),
        page=1,
        per_page=2,
    )
    page2, total2 = round_repo.list_for_season_sorted_paged(
        season.season_id,
        sort=SortQuery(order_by="number", direction="asc"),
        page=2,
        per_page=2,
    )
    assert total == 3 and total2 == 3
    assert [r.round_number for r in page1] == [1, 2]
    assert [r.round_number for r in page2] == [3]
