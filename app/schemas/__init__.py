"""
===============================================================================
Package: app.schemas
Purpose
-------
Define **DTOs** (Data Transfer Objects) used at boundaries:
- CLI/diagnostics outputs (e.g., check-env, diag, seed summaries)
- Service/repository input/output shapes (e.g., organisations CRUD)
- Healthcheck/infra summaries

Design rules (Pydantic v2)
--------------------------
- Pydantic BaseModel used for all DTOs.
- **Snake_case** in Python; **JSON** also snake_case (no aliasing required in v1).
- Datetimes are timezone-aware UTC (ISO8601 with "Z" when serialized).
- UUIDs serialized as standard strings.
- No ORM objects leak outside: use explicit mapping functions.

Module layout
-------------
- common.py       : shared types, base config, helpers (timestamps, pagination,
                    healthcheck payload, error envelope)
- organisation.py : DTOs specific to organisations CRUD/listing (entity scope #1)

Export contract (Codex must implement)
--------------------------------------
from .common import (
    BaseDTO,
    TimestampsDTO,
    PaginationQuery,
    PaginationMeta,
    SortQuery,
    HealthcheckPingDTO,
    ErrorEnvelopeDTO,
)
from .organisation import (
    OrganisationInDTO,
    OrganisationUpdateDTO,
    OrganisationOutDTO,
    OrganisationListOutDTO,
)
===============================================================================
"""
