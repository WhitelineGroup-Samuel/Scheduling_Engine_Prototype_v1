## app/repositories/base.py

from __future__ import annotations

import builtins
from collections.abc import Iterable, Mapping, Sequence
from typing import (
    Any,
    NoReturn,
    TypeVar,
    cast,
)

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from app.errors import NotFoundError  # map to your concrete AppError classes
from app.repositories.typing import SelectStmt  # <- use Select[Any]
from app.schemas._base import SortQuery

TModel = TypeVar("TModel")


class BaseRepository[TModel]:
    """
    Generic, minimal repository base.

    Conventions:
    - Repositories are constructed with an active SQLAlchemy Session.
    - Methods return ORM model instances (services convert to DTOs).
    - Transactions/commits are owned by the service layer. Repos may call `flush()` to materialize PKs.

    Implementors must set:
        model: type[TModel]
    """

    model: type[TModel]

    def __init__(self, session: Session) -> None:
        self.session = session

    # -----------------------------
    # CRUD
    # -----------------------------

    def get(self, pk: int) -> TModel:
        """Fetch one row by primary key or raise NotFoundError."""
        stmt: SelectStmt = select(self.model).where(self._pk_column() == pk)
        obj = cast(TModel | None, self.session.execute(stmt).scalar_one_or_none())
        if obj is None:
            raise NotFoundError(f"{self.model.__name__}({pk}) not found")
        return obj

    def get_or_none(self, pk: int) -> TModel | None:
        """Fetch one row by primary key or return None."""
        stmt: SelectStmt = select(self.model).where(self._pk_column() == pk)
        return cast(TModel | None, self.session.execute(stmt).scalar_one_or_none())

    def list(
        self,
        *,
        where: Iterable[Any] = (),
        order_by: Iterable[Any] = (),
        limit: int | None = None,
        offset: int | None = None,
    ) -> builtins.list[TModel]:
        stmt: SelectStmt = select(self.model)
        for cond in where:
            stmt = stmt.where(cond)
        for ob in order_by:
            stmt = stmt.order_by(ob)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = self.session.execute(stmt).scalars()
        return list(cast(Iterable[TModel], result))

    def count(self, *, where: Iterable[Any] = ()) -> int:
        """Count rows matching optional WHERE conditions."""
        stmt: SelectStmt = select(func.count(self._pk_column()))
        for cond in where:
            stmt = stmt.where(cond)
        return int(self.session.execute(stmt).scalar_one())

    def exists(self, *, where: Iterable[Any]) -> bool:
        """True if any row matches provided WHERE conditions."""
        stmt: SelectStmt = select(func.count(self._pk_column()))
        for cond in where:
            stmt = stmt.where(cond)
        return int(self.session.execute(stmt).scalar_one()) > 0

    def create(self, values: dict[str, Any]) -> TModel:
        """Create a new row from a values dict (use dto.model_dump(...))."""

        # Make a shallow copy to avoid mutating caller data
        vals = dict(values)

        # If the model supports created_by_user_id and it's missing, attribute it
        if hasattr(self.model, "created_by_user_id") and "created_by_user_id" not in vals:
            actor_id = self._resolve_actor_user_id()
            if actor_id is not None:
                vals["created_by_user_id"] = actor_id

        obj = self.model(**vals)
        self.session.add(obj)
        try:
            self.session.flush()  # materialize PKs / defaults
        except IntegrityError as ie:
            self._raise_integrity_error(ie, "create")
        return obj

    def bulk_create(self, values_list: Sequence[dict[str, Any]]) -> builtins.list[TModel]:
        """Create many rows efficiently. Returns the persisted objects."""
        objs = [self.model(**vals) for vals in values_list]
        self.session.add_all(objs)
        try:
            self.session.flush()
        except IntegrityError as ie:
            self._raise_integrity_error(ie, "bulk_create")
        return objs

    def update(self, pk: int, values: dict[str, Any]) -> TModel:
        """Load-mutate-flush update (preserves ORM events/defaults)."""
        obj = self.get(pk)
        for k, v in values.items():
            setattr(obj, k, v)
        try:
            self.session.flush()
        except IntegrityError as ie:
            self._raise_integrity_error(ie, "update")
        return obj

    def delete(self, pk: int) -> None:
        """Delete by primary key; flush to execute."""
        obj = self.get(pk)
        self.session.delete(obj)
        self.session.flush()

    # -----------------------------
    # Helpers
    # -----------------------------

    @staticmethod
    def apply_pagination(stmt: SelectStmt, *, offset: int, limit: int) -> SelectStmt:
        """Attach OFFSET/LIMIT to a Select."""
        return stmt.offset(offset).limit(limit)

    def apply_sorting(
        self,
        stmt: SelectStmt,
        sort: SortQuery | None,
        allowed: Mapping[str, Any],
        default: Any | None = None,
    ) -> SelectStmt:
        """
        Attach ORDER BY to `stmt` based on a SortQuery (order_by/direction) or a default column.

        Args:
            stmt: The Select statement to order.
            sort: Optional SortQuery with `order_by` (key into `allowed`) and `direction` ("asc"/"desc").
            allowed: Mapping of sort keys -> column-like objects (InstrumentedAttribute/ColumnElement).
            default: Optional column-like to use when `sort` is None. If omitted, PK ASC is used.

        Behavior:
            - Applies primary ORDER BY from `sort` if provided, else from `default`, else PK ASC.
            - Appends PK ASC as a deterministic tiebreaker **only if** the primary column is not the PK.
            - Raises ValueError if `order_by` is not in `allowed`.

        Returns:
            The Select statement with ORDER BY applied.
        """
        pk_col = self._pk_column()

        def _key_like(col: Any) -> str | None:
            """Best-effort extraction of a comparable key name from SQLAlchemy column-ish objects."""
            try:
                if isinstance(col, InstrumentedAttribute):
                    key_obj: object = col.key
                else:
                    key_obj = getattr(col, "key", None)
                return key_obj if isinstance(key_obj, str) else None
            except Exception:
                return None

        # Choose primary column + direction
        if sort is not None:
            key = sort.order_by
            if key not in allowed:
                raise ValueError(f"Unknown sort key: {key}")
            primary_col = allowed[key]
            is_desc = (getattr(sort, "direction", "asc") or "asc").lower() == "desc"
            stmt = stmt.order_by(primary_col.desc() if is_desc else primary_col.asc())
            primary_is_pk = _key_like(primary_col) == _key_like(pk_col)
            if not primary_is_pk:
                stmt = stmt.order_by(pk_col.asc())
            return stmt

        # No SortQuery provided: use default or PK
        if default is not None:
            primary_col = default
            stmt = stmt.order_by(primary_col.asc())
            primary_is_pk = _key_like(primary_col) == _key_like(pk_col)
            if not primary_is_pk:
                stmt = stmt.order_by(pk_col.asc())
            return stmt

        # Fallback: PK ASC only
        return stmt.order_by(pk_col.asc())

    def paginate_items_total(
        self,
        stmt: SelectStmt,
        *,
        page: int,
        per_page: int,
        max_per_page: int = 500,
    ) -> tuple[builtins.list[TModel], int]:
        """
        Return (items, total) for the provided Select statement.

        Notes:
        - Uses a subquery COUNT(*) with ORDER BY removed for accuracy and performance.
        - Do NOT pass an already-paginated statement.
        - Repo returns ORM models; DTO conversion belongs in services.

        Raises:
            ValueError: if pagination params are invalid.
        """
        if page < 1:
            raise ValueError("page must be >= 1")
        if per_page < 1 or per_page > max_per_page:
            raise ValueError(f"per_page must be between 1 and {max_per_page}")

        offset = (page - 1) * per_page

        # Count total rows (ignore ORDER BY to avoid planner penalties)
        count_subq = stmt.order_by(None).subquery()
        total = int(self.session.execute(select(func.count()).select_from(count_subq)).scalar_one())

        # Fetch page of items
        page_stmt = stmt.limit(per_page).offset(offset)
        result = self.session.execute(page_stmt).scalars()
        items = list(cast(Iterable[TModel], result))

        return items, total

    def _pk_column(self) -> ColumnElement[Any]:
        """Return the model's primary key Column clause."""
        mapper = cast(Any, self.model).__mapper__
        return cast(ColumnElement[Any], mapper.primary_key[0])

    def _raise_integrity_error(self, ie: IntegrityError, _op: str | None = None) -> NoReturn:
        """
        Pass through raw DB IntegrityError so callers/tests can assert on it.
        (We can add mapping in higher layers if/when needed.)
        """
        raise ie

    def _resolve_actor_user_id(self) -> int | None:
        """
        Determine which user to attribute creates to:
        1) Prefer an explicit actor set on the session (session.info["actor_user_id"]).
        2) Otherwise fall back to a stable 'System' user, creating it if needed.
        Returns the user id or None if attribution isn't applicable.
        """
        # 1) Session-provided actor
        actor = self.session.info.get("actor_user_id")
        if actor is not None:
            try:
                return int(actor)
            except Exception:
                pass  # ignore bad value and fall back

        # 2) System user fallback
        try:
            # Local import avoids circulars at module import time
            from app.repositories.system.user_account_repository import (
                UserAccountRepository,
            )

            user_repo = UserAccountRepository(self.session)
            user = user_repo.get_by_email("system@whiteline.local")
            if user is None:
                user = user_repo.create(
                    {
                        "email": "system@whiteline.local",
                        "display_name": "System",
                    }
                )
                self.session.flush()
            return int(user.user_account_id)
        except Exception:
            # If anything goes wrong, don't crash create(); just return None.
            return None
