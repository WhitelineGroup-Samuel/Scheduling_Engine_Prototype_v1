"""
===============================================================================
File: app/repositories/base_repository.py
Purpose
-------
Provide shared helpers and a light contract for repository classes. This base
does **not** manage sessions or transactions—callers do via app.db.session.

Public API (Codex must implement)
---------------------------------
class BaseRepository:
    Base for repositories. Optionally holds a Session (when constructed with one),
    but **each method** should also accept an explicit `session: Session` parameter
    to keep usage flexible (pattern: prefer explicit `session` argument).

    # Construction:
    #   def __init__(self, session: Session | None = None):
    #       self._session = session

    # Session accessor (helpers):
    #   def require_session(self, session: Session | None) -> Session:
    #       Return the explicit `session` if provided; else `self._session` if set;
    #       otherwise raise RuntimeError("Session required").

    # CRUD helper patterns (to be used by concrete repos):
    #   - def add(self, session: Session, instance: Base) -> Base
    #   - def delete(self, session: Session, instance: Base) -> None
    #   - def refresh(self, session: Session, instance: Base) -> Base

    # Pagination utility:
    #   def apply_pagination(self, query, *, page: int, page_size: int, max_page_size: int = 100) -> tuple[list, int]:
    #       Enforce sane bounds (page>=1, 1<=page_size<=max_page_size).
    #       Return (items, total_count). Use subquery or count() efficiently.

    # Sorting utility:
    #   def apply_sorting(self, query, *, sort: str | None, allowed: dict[str, ColumnElement]) -> Any:
    #       Accept strings like "name" or "-created_at".
    #       Map field names via `allowed` to actual columns; raise ValueError for invalid fields.

    # Existence/uniqueness helper:
    #   def exists(self, session: Session, stmt) -> bool:
    #       Efficient SQL EXISTS pattern.

Contracts & safety
------------------
- Do **not** swallow SQLAlchemy exceptions; let them propagate.
- Avoid N+1: when returning collections, eager-load relationships only when explicitly needed.
- Sanitize/validate user input (sort fields, page sizes) at the repo boundary.

Testing guidance
----------------
- Unit: feed a Session from a fixture; assert pagination and sorting.
- Integration: verify constraints (unique keys) raise IntegrityError.
===============================================================================
"""
