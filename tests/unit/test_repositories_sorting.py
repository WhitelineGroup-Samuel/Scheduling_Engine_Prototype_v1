from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Any

import pytest
from sqlalchemy import Select, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.repositories.base import BaseRepository
from app.schemas._base import SortQuery

# --- Test model & repo -------------------------------------------------------


class _Base(DeclarativeBase):
    pass


class Item(_Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    rank: Mapped[int] = mapped_column()


class ItemRepository(BaseRepository[Item]):
    """Small repo that only needs sorting helper for unit tests."""

    model = Item

    # expose a tiny wrapper so we can call apply_sorting in tests
    def sort_stmt(
        self,
        stmt: Select[Any],
        sort: SortQuery | None,
        allowed: Mapping[str, Any],
        default: Any | None = None,
    ) -> Select[Any]:
        sorted_stmt: Select[Any] = self.apply_sorting(stmt, sort, allowed, default=default)
        return sorted_stmt


# --- Fixtures ----------------------------------------------------------------


@pytest.fixture()
def dummy_session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with Session(engine) as s:
        yield s


# --- Helpers -----------------------------------------------------------------


def _sql(stmt: Select[Any]) -> str:
    """Render SQL (dialect-agnostic enough for order_by assertions)."""
    s = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    # squeeze whitespace for simpler matching
    return re.sub(r"\s+", " ", s).strip()


# --- Tests -------------------------------------------------------------------


def test_apply_sorting_valid_keys_asc_desc(dummy_session: Session) -> None:
    repo = ItemRepository(dummy_session)  # session not used, but typed
    stmt = select(Item)
    allowed: dict[str, Any] = {
        "name": Item.name,
        "rank": Item.rank,
        "id": Item.id,
    }

    # ASC by name + tiebreaker by PK (id)
    s1 = repo.sort_stmt(stmt, SortQuery(order_by="name", direction="asc"), allowed, default=Item.name)
    sql1 = _sql(s1)
    assert "ORDER BY items.name ASC, items.id ASC" in sql1

    # DESC by rank + tiebreaker by PK (id)
    s2 = repo.sort_stmt(stmt, SortQuery(order_by="rank", direction="desc"), allowed, default=Item.name)
    sql2 = _sql(s2)
    assert "ORDER BY items.rank DESC, items.id ASC" in sql2


def test_apply_sorting_unknown_key_raises_value_error(dummy_session: Session) -> None:
    repo = ItemRepository(dummy_session)
    stmt = select(Item)
    allowed: dict[str, Any] = {"name": Item.name}

    with pytest.raises(ValueError, match="Unknown sort key"):
        _ = repo.sort_stmt(
            stmt,
            SortQuery(order_by="oops", direction="asc"),
            allowed,
            default=Item.name,
        )


def test_apply_sorting_appends_pk_tiebreaker_once(dummy_session: Session) -> None:
    repo = ItemRepository(dummy_session)
    stmt = select(Item)
    allowed: dict[str, Any] = {"id": Item.id, "name": Item.name}

    # Sorting primarily by a different column should append PK
    s1 = repo.sort_stmt(stmt, SortQuery(order_by="name", direction="asc"), allowed, default=Item.name)
    sql1 = _sql(s1)
    assert "ORDER BY items.name ASC, items.id ASC" in sql1

    # Sorting primarily by PK itself should *not* duplicate PK order
    s2 = repo.sort_stmt(stmt, SortQuery(order_by="id", direction="asc"), allowed, default=Item.name)
    sql2 = _sql(s2)
    # Expect exactly "... ORDER BY items.id ASC" without an extra ", items.id ASC"
    assert "ORDER BY items.id ASC" in sql2
    assert ", items.id ASC, items.id ASC" not in sql2
