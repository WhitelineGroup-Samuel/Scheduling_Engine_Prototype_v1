from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import Select, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.repositories.base import BaseRepository
from app.schemas._base import SortQuery

# --- Test model & repo with real in-memory DB --------------------------------


class _Base(DeclarativeBase):
    pass


class Row(_Base):
    __tablename__ = "rows"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column()


class RowRepository(BaseRepository[Row]):
    model = Row

    def sort_and_paginate(self, stmt: Select[Any], sort: SortQuery | None, page: int, per_page: int) -> tuple[list[Row], int]:
        stmt_sorted: Select[Any] = self.apply_sorting(
            stmt,
            sort,
            allowed={"id": Row.id, "label": Row.label},
            default=Row.id,
        )
        return self.paginate_items_total(stmt_sorted, page=page, per_page=per_page)


# --- Fixtures ----------------------------------------------------------------


@pytest.fixture()
def mem_session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    _Base.metadata.create_all(engine)
    with Session(engine) as s:
        # Seed 23 rows
        s.add_all(Row(label=f"row-{i:02d}") for i in range(1, 24))
        s.commit()
        yield s


# --- Tests -------------------------------------------------------------------


def test_paginate_first_and_last_pages(mem_session: Session) -> None:
    repo = RowRepository(mem_session)
    stmt = select(Row)

    # Page 1, per_page 10
    items_p1, total = repo.paginate_items_total(stmt, page=1, per_page=10)
    assert total == 23
    assert [r.id for r in items_p1] == list(range(1, 11))

    # Page 3, per_page 10 (last partial page)
    items_p3, total2 = repo.paginate_items_total(stmt, page=3, per_page=10)
    assert total2 == 23
    assert [r.id for r in items_p3] == [21, 22, 23]


def test_apply_sort_and_paginate_desc(mem_session: Session) -> None:
    repo = RowRepository(mem_session)
    stmt = select(Row)

    items, total = repo.sort_and_paginate(stmt, sort=SortQuery(order_by="id", direction="desc"), page=1, per_page=5)
    assert total == 23
    assert [r.id for r in items] == [23, 22, 21, 20, 19]


def test_per_page_validation(mem_session: Session) -> None:
    repo = RowRepository(mem_session)
    stmt = select(Row)

    with pytest.raises(ValueError):
        _ = repo.paginate_items_total(stmt, page=1, per_page=0)

    # If your helper enforces a ceiling, this should raise; otherwise adjust.
    with pytest.raises(ValueError):
        _ = repo.paginate_items_total(stmt, page=1, per_page=10_000)
