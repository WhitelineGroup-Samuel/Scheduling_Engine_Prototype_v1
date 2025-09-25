"""Repository base utilities and shared helpers."""

from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement

__all__ = ["BaseRepository"]

_T = TypeVar("_T")


class BaseRepository:
    """Provide shared helpers for repository implementations."""

    def __init__(self, session: Session | None = None) -> None:
        """Initialise the repository with an optional :class:`Session`."""

        self._session = session

    def require_session(self, session: Session | None) -> Session:
        """Return a usable :class:`~sqlalchemy.orm.Session` instance.

        Parameters
        ----------
        session:
            An explicit session provided by the caller. When ``None`` the
            repository-level session (if configured) is used.

        Raises
        ------
        RuntimeError
            If no session is available.
        """

        if session is not None:
            return session
        if self._session is not None:
            return self._session
        raise RuntimeError("Session required")

    def add(self, session: Session, instance: _T) -> _T:
        """Add an ORM instance to the identity map and return it."""

        session.add(instance)
        return instance

    def delete(self, session: Session, instance: Any) -> None:
        """Mark the provided ORM instance for deletion."""

        session.delete(instance)

    def refresh(self, session: Session, instance: _T) -> _T:
        """Refresh an ORM instance from the database and return it."""

        session.refresh(instance)
        return instance

    def apply_pagination(
        self,
        query: Select[Any],
        *,
        session: Session | None = None,
        page: int,
        page_size: int,
        max_page_size: int = 100,
    ) -> tuple[list[Any], int]:
        """Apply pagination to ``query`` and return the paged items and total count.

        Parameters
        ----------
        query:
            The SQLAlchemy :class:`~sqlalchemy.sql.Select` object to paginate.
        session:
            Explicit session to use for execution. Falls back to the repository
            session if omitted.
        page:
            One-based page index.
        page_size:
            Number of rows per page. Must be between 1 and ``max_page_size``.
        max_page_size:
            Upper bound for ``page_size`` to prevent unbounded queries.

        Returns
        -------
        tuple[list[Any], int]
            ``(items, total_count)`` where ``items`` are ORM objects produced by
            the query and ``total_count`` represents the total number of rows
            available without pagination.

        Raises
        ------
        ValueError
            If ``page`` or ``page_size`` fall outside the allowed bounds.
        RuntimeError
            When no session is available.
        """

        working_session = self.require_session(session)
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        if page_size > max_page_size:
            raise ValueError("page_size exceeds maximum allowed value")

        offset = (page - 1) * page_size
        count_subquery = query.order_by(None).subquery()
        total_stmt = select(func.count()).select_from(count_subquery)
        total = int(working_session.execute(total_stmt).scalar_one())

        paged_stmt = query.limit(page_size).offset(offset)
        items = list(working_session.execute(paged_stmt).scalars().all())
        return items, total

    def apply_sorting(
        self,
        query: Select[Any],
        *,
        sort: str | None,
        allowed: dict[str, ColumnElement[Any]],
    ) -> Select[Any]:
        """Apply ordering to ``query`` using an allowed mapping of sort keys.

        Parameters
        ----------
        query:
            The statement to modify.
        sort:
            Sort directive supplied by the caller. A leading ``-`` requests
            descending order.
        allowed:
            Mapping of allowed sort keys to SQLAlchemy column expressions.

        Returns
        -------
        Select[Any]
            A new select with the appropriate ``ORDER BY`` clause applied.

        Raises
        ------
        ValueError
            If the provided ``sort`` value is not present in ``allowed``.
        """

        if sort is None:
            return query
        descending = sort.startswith("-")
        field = sort[1:] if descending else sort
        if field not in allowed:
            raise ValueError(f"Invalid sort field: {field}")
        column = allowed[field]
        order_clause = column.desc() if descending else column.asc()
        return query.order_by(order_clause)

    def exists(self, session: Session, stmt: Select[Any]) -> bool:
        """Return ``True`` when the provided statement yields at least one row."""

        exists_stmt = select(stmt.exists())
        return bool(session.execute(exists_stmt).scalar_one())
