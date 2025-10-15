from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.system.organisation_repository import OrganisationRepository
from app.repositories.system.user_account_repository import UserAccountRepository
from app.repositories.system.user_permission_repository import UserPermissionRepository
from app.schemas._base import SortQuery


def test_user_permissions_scopes_and_sorting(db_session: Session) -> None:
    org_repo = OrganisationRepository(db_session)
    user_repo = UserAccountRepository(db_session)
    perm_repo = UserPermissionRepository(db_session)

    org = org_repo.create({"organisation_name": "Perm Org", "slug": "perm-org"})
    u1 = user_repo.create({"email": "alice@example.com", "is_active": True, "display_name": "Alice"})
    u2 = user_repo.create({"email": "bob@example.com", "is_active": True, "display_name": "Bob"})

    # One row per (user, org) with boolean flags
    p1 = perm_repo.create(
        {
            "organisation_id": org.organisation_id,
            "user_account_id": u1.user_account_id,
            "can_schedule": True,
            "can_approve": False,
            "can_export": True,
        }
    )
    _p2 = perm_repo.create(
        {
            "organisation_id": org.organisation_id,
            "user_account_id": u2.user_account_id,
            "can_schedule": False,
            "can_approve": True,
            "can_export": False,
        }
    )

    # list_for_user_in_org: should return (at most) the single row for that user+org
    u1_perms = perm_repo.list_for_user_in_org(u1.user_account_id, org.organisation_id)
    assert len(u1_perms) == 1
    assert u1_perms[0].user_account_id == u1.user_account_id
    assert u1_perms[0].organisation_id == org.organisation_id
    assert u1_perms[0].can_schedule is True
    assert u1_perms[0].can_approve is False
    assert u1_perms[0].can_export is True

    # list_for_org: ordered by user_account_id ASC
    org_perms = perm_repo.list_for_org(org.organisation_id)
    assert [(p.user_account_id, p.can_schedule, p.can_approve, p.can_export) for p in org_perms] == [
        (u1.user_account_id, True, False, True),
        (u2.user_account_id, False, True, False),
    ]

    # list_for_user_in_org_sorted: defaults to created_at ASC; but there is only one row anyway
    u1_sorted = perm_repo.list_for_user_in_org_sorted(u1.user_account_id, org.organisation_id, sort=None)
    assert [p.permission_id for p in u1_sorted] == [p1.permission_id]

    # list_for_org_sorted_paged — use a real SortQuery (by user asc), and paginate
    page1, total = perm_repo.list_for_org_sorted_paged(
        org.organisation_id,
        sort=SortQuery(order_by="user", direction="asc"),
        page=1,
        per_page=1,
    )
    page2, total2 = perm_repo.list_for_org_sorted_paged(
        org.organisation_id,
        sort=SortQuery(order_by="user", direction="asc"),
        page=2,
        per_page=1,
    )
    assert total == 2 and total2 == 2
    assert [(p.user_account_id, p.can_schedule, p.can_approve, p.can_export) for p in page1] == [(u1.user_account_id, True, False, True)]
    assert [(p.user_account_id, p.can_schedule, p.can_approve, p.can_export) for p in page2] == [(u2.user_account_id, False, True, False)]
