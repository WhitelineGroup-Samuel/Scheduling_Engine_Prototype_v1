"""
===============================================================================
File: app/repositories/organisation_repository.py
Purpose
-------
Data-access for the `organisations` table — the **first entity scope** used to
validate the end-to-end pipeline. Implements create/read/update/delete (CRUD),
lookup by business keys, list with pagination/sorting, and simple upsert.

Model assumptions (from database_erd.md / Phase E Step 12)
----------------------------------------------------------
- Table: organisations
- Columns (representative):
    id           : UUID (PK, generated app-side or DB-side)
    name         : TEXT, NOT NULL, UNIQUE (business key)
    slug         : TEXT, NOT NULL, UNIQUE (url-safe; derived from name)
    created_at   : TIMESTAMPTZ, NOT NULL, default NOW() AT TIME ZONE 'UTC'
    updated_at   : TIMESTAMPTZ, NOT NULL, default NOW() AT TIME ZONE 'UTC'
- Indexes: unique on (name), unique on (slug), standard pk index.
- Timestamps managed by DB defaults or application on update.

Public API (Codex must implement)
---------------------------------
class OrganisationRepository(BaseRepository):
    Concrete repository for Organisation model.
    Usage:
        repo = OrganisationRepository()
        with get_session(SessionLocal) as s:
            org = repo.create(s, name="Acme FC", slug="acme-fc")

    # -- Read methods ---------------------------------------------------------
    def get_by_id(self, session, organisation_id) -> "Organisation | None":
        Fetch by primary key. Return None if not found.

    def get_by_name(self, session, name: str) -> "Organisation | None":
        Fetch by unique business name (case-sensitive or normalized as per model).

    def get_by_slug(self, session, slug: str) -> "Organisation | None":
        Fetch by unique slug.

    def list(
        self,
        session,
        *,
        page: int = 1,
        page_size: int = 50,
        sort: str | None = "name",  # supports "-name", "created_at", "-created_at"
        search: str | None = None,   # optional ILIKE filter on name/slug
    ) -> tuple[list["Organisation"], int]:
        Return (items, total_count) with pagination & sorting applied.
        - Enforce bounds: page>=1; 1<=page_size<=max_page_size (100).
        - Sorting: map "name", "created_at", "updated_at"; prefix "-" for DESC.
        - Search (optional): case-insensitive ILIKE on name OR slug.

    # -- Write methods --------------------------------------------------------
    def create(self, session, *, name: str, slug: str | None = None) -> "Organisation":
        Insert a new Organisation and return it (refreshed).
        - Generate slug from name if not provided (use app.utils.validators/io helpers optionally).
        - On UNIQUE violation (name/slug), SQLAlchemy raises IntegrityError.
        - Do not catch IntegrityError here; let callers/handlers map it to ConflictError.

    def update(
        self,
        session,
        organisation_id,
        *,
        name: str | None = None,
        slug: str | None = None,
    ) -> "Organisation":
        Update an existing Organisation. Return the updated row.
        - Must raise sqlalchemy.exc.NoResultFound if organisation_id does not exist.
        - Update `updated_at` timestamp (DB default trigger or explicit app-side update).
        - UNIQUE violations bubble as IntegrityError.

    def upsert_by_name(
        self,
        session,
        *,
        name: str,
        slug: str | None = None,
    ) -> "Organisation":
        Idempotent create-or-update by business key (name).
        Strategy (portable v1, no ON CONFLICT):
          1) Try get_by_name(); if found and slug differs, update; else return found.
          2) If not found, create().
        Optional (Postgres-specific): Provide an alternative path using ON CONFLICT DO UPDATE
        if you decide to add dialect-specific SQL later (not required in v1).

    def delete(self, session, organisation_id) -> None:
        Hard delete by PK.
        - Raise sqlalchemy.exc.NoResultFound if id not found.
        - For v1, physical delete is acceptable (no soft-delete requirement).

Implementation details & constraints
------------------------------------
- Import the Organisation model from app.models.core (or appropriate module).
- Use SQLAlchemy Core/ORM query patterns (2.x style recommended).
- Keep methods small; apply helpers from BaseRepository for pagination/sorting.
- Do not log within repo methods; callers log at CLI/service layer.

Input validation & normalization
--------------------------------
- `name` trimming and collapse internal whitespace (optional helper).
- `slug` normalization to lowercase, hyphenated (use a simple utility if available).
- Reject empty strings for required fields with ValueError (before touching DB).

Performance & indexes
---------------------
- Ensure list() orders by an indexed column where possible (name); avoid table scans
  for large tables by combining pagination with deterministic sort columns.

Testing (what the tests should cover)
-------------------------------------
- Creating an org and fetching by id/name/slug.
- Unique constraint violations on duplicate name or slug (IntegrityError).
- list() pagination boundaries and total_count accuracy.
- Search filter returns matching subsets (case-insensitive).
- update() modifies fields and bumps updated_at.
- delete() removes the row (subsequent get returns None).
===============================================================================
"""
