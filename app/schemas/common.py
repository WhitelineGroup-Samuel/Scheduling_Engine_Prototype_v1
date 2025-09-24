"""
===============================================================================
File: app/schemas/common.py
Purpose
-------
Provide **shared DTO primitives** and configuration for all schemas:
- Base model config (Pydantic v2)
- Timestamps mixin (created_at, updated_at)
- Pagination + sorting query objects and response metadata
- Healthcheck ping payload (for check-env/diag)
- Error envelope for consistent machine output (future HTTP compatibility)

Pydantic v2 configuration (Codex must implement)
------------------------------------------------
class BaseDTO(BaseModel):
    model_config = ConfigDict(
        frozen=False,               # DTOs are mutable by default
        extra="forbid",             # reject unknown fields
        populate_by_name=False,     # we keep snake_case everywhere in v1
        str_strip_whitespace=True,  # trim strings
        validate_default=True,      # validate defaults
        ser_json_timedelta="iso8601",
        ser_json_inf_nan=False,
    )

UTC datetime policy
-------------------
- All datetimes are **aware** in UTC.
- Serializer must produce ISO8601 with "Z".
- Provide validators/helpers:
    - def ensure_utc(dt: datetime) -> datetime
    - @field_validator("created_at", "updated_at", mode="before") to coerce to UTC

DTO primitives (Codex must implement)
-------------------------------------
1) class TimestampsDTO(BaseDTO):
       created_at: datetime
       updated_at: datetime
   - Validators ensure both are UTC-aware.

2) class PaginationQuery(BaseDTO):
       page: int = 1
       page_size: int = 50
       sort: str | None = None   # e.g., "name", "-created_at"
       search: str | None = None
   - Validate: page >= 1, 1 <= page_size <= 100 (raise ValueError otherwise).

3) class PaginationMeta(BaseDTO):
       page: int
       page_size: int
       total: int

4) class SortQuery(BaseDTO):
       sort: str | None = None
   - Placeholder type (some commands may only accept sorting).

5) class HealthcheckPingDTO(BaseDTO):
       ok: bool
       database: str
       server_version: str
       duration_ms: float
   - **Exact** keys/types match Phase H Step 17.
   - Provide @classmethod from_dict(d: dict) -> "HealthcheckPingDTO" for adapter.

6) class ErrorEnvelopeDTO(BaseDTO):
       code: str                 # e.g., "SENG-DB-001"
       message: str              # safe, user-facing error
       exit_code: int
       severity: Literal["INFO","WARN","ERROR","CRITICAL"]
       context: dict[str, object] | None = None

Mapping helpers (non-ORM specific)
----------------------------------
- def to_json(obj: BaseDTO) -> str: JSON dumps with the correct config.
- Optional: def now_utc() -> datetime for convenience in DTO factories.

Testing expectations
--------------------
- Pagination validation (boundaries enforced).
- Timestamps are UTC-aware after model creation.
- HealthcheckPingDTO.from_dict returns a valid DTO with correct types.
- ErrorEnvelopeDTO round-trips to JSON cleanly.
===============================================================================
"""
