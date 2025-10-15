from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.system.user_account_repository import UserAccountRepository
from app.schemas._base import SortQuery


def test_user_account_get_by_email_and_active_lists(db_session: Session) -> None:
    repo = UserAccountRepository(db_session)

    # Create a few users; mix active/inactive
    _u1 = repo.create({"email": "alpha@example.com", "is_active": True})
    u2 = repo.create({"email": "bravo@example.com", "is_active": False})
    _u3 = repo.create({"email": "charlie@example.com", "is_active": True})

    # get_by_email
    got = repo.get_by_email("bravo@example.com")
    assert got is not None and got.user_account_id == u2.user_account_id

    # list_active (ordered by email)
    active = repo.list_active()
    assert [u.email for u in active] == ["alpha@example.com", "charlie@example.com"]

    # list_sorted (string sort; default "email" ASC)
    sorted_default = repo.list_sorted(sort=None)
    assert [u.email for u in sorted_default] == [
        "alpha@example.com",
        "bravo@example.com",
        "charlie@example.com",
    ]

    # list_active_sorted_paged
    page1, total = repo.list_active_sorted_paged(sort=SortQuery(order_by="email", direction="asc"), page=1, per_page=1)
    page2, total2 = repo.list_active_sorted_paged(sort=SortQuery(order_by="email", direction="asc"), page=2, per_page=1)
    assert total == 2 and total2 == 2
    assert [u.email for u in page1] == ["alpha@example.com"]
    assert [u.email for u in page2] == ["charlie@example.com"]
