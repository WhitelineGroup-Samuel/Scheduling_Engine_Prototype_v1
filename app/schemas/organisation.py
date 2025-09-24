"""
===============================================================================
File: app/schemas/organisation.py
Purpose
-------
Define **Organisation** DTOs for the first entity scope. These represent the
boundary shapes used by CLI/services to pass inputs to repositories and to
return results back to callers.

Entity recap (from database_erd.md / Phase E Step 12)
-----------------------------------------------------
- Table: organisations
- Fields (representative):
    id: UUID (PK)
    name: TEXT, NOT NULL, UNIQUE
    slug: TEXT, NOT NULL, UNIQUE
    created_at: TIMESTAMPTZ (UTC)
    updated_at: TIMESTAMPTZ (UTC)

DTOs (Codex must implement)
---------------------------
1) class OrganisationInDTO(BaseDTO):
       Input for creating a new Organisation.
       name: str
       slug: str | None = None
   - Validation:
       * name: strip, ensure non-empty after trim, max length (e.g., 200)
       * slug (optional): if provided, normalize to lowercase, hyphenated,
         strip leading/trailing hyphens; enforce `[a-z0-9-]+`, length <= 200.
       * If slug is None, callers may derive it from name at the service layer.

2) class OrganisationUpdateDTO(BaseDTO):
       Input for updating an existing Organisation.
       Only provided fields are updated.
       name: str | None = None
       slug: str | None = None
   - Validation:
       * If provided, same constraints as OrganisationInDTO.
       * Must not be all None (raise ValueError).

3) class OrganisationOutDTO(TimestampsDTO):
       Output shape for a single Organisation, suitable for CLI/diagnostics.
       id: UUID
       name: str
       slug: str
   - Inherits created_at, updated_at (UTC).

4) class OrganisationListOutDTO(BaseDTO):
       Paginated list of Organisations.
       items: list[OrganisationOutDTO]
       meta: PaginationMeta

Mapping helpers (Codex must implement)
--------------------------------------
- @classmethod OrganisationOutDTO.from_orm_row(row) -> "OrganisationOutDTO":
      - Accepts an ORM instance (Organisation) and builds the DTO.
      - MUST NOT leak lazy relationships (only the fields defined above).
      - Ensure created_at/updated_at are UTC-aware; convert if necessary.

- @staticmethod def normalize_slug(name_or_slug: str) -> str:
      - Lowercase, trim, replace internal whitespace/invalid chars with '-'
      - Collapse multiple '-' to a single '-', strip leading/trailing '-'
      - Enforce `[a-z0-9-]+` (raise ValueError if cannot normalize)

- Optional convenience:
  def to_create_params(dto: OrganisationInDTO) -> dict:
      - Returns dict for repository.create() with a derived slug if dto.slug is None.

DTO/Repository boundary contract
--------------------------------
- Repositories expect **validated** inputs (DTOs handle normalization/validation).
- Repositories return ORM rows; callers convert to DTOs via from_orm_row().
- Uniqueness/constraint errors are surfaced as SQLAlchemy exceptions; CLI/service
  layer maps them to AppError types (ConflictError) via handlers.

Testing expectations
--------------------
- OrganisationInDTO validation: empty/whitespace-only name rejected; slug normalization.
- OrganisationUpdateDTO: all None rejected; valid partial updates accepted.
- OrganisationOutDTO.from_orm_row: correct field mapping and UTC datetimes.
- OrganisationListOutDTO: correct pagination meta with items list.

Serialization rules
-------------------
- JSON keys are snake_case; datetimes ISO8601 UTC.
- UUID serialized as canonical string.

Notes
-----
- Keep DTOs lightweight and portable; avoid importing heavy modules here.
- If aliasing is introduced later (e.g., camelCase for HTTP), we’ll use field
  aliases and `populate_by_name=True` in a v2 of these DTOs.
===============================================================================
"""
