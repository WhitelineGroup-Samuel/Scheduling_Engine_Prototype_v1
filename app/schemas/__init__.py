# pyright: reportUnusedImport=false
# flake8: noqa
"""
Top-level exports for the app.schemas package.

Design:
- Export common base/util classes & helpers (ORMBase, audit read mixins, pagination, error envelope, healthcheck).
- Expose subpackages as *namespaces* (system, calendar, venues, timeplan, taxonomy, constraints, scheduling, staging, allocations).
  This keeps imports tidy while avoiding a giant star-reexport of every DTO.

Usage examples:
    from app.schemas import system
    org = system.OrganisationRead.model_validate(orm_row)

    from app.schemas import PaginationQuery, PaginationMeta
"""

# ---- Shared base & utilities ----
from app.schemas._base import (
    ORMBase,
    CreatedStampedReadMixin,
    UpdatedStampedReadMixin,
    PaginationQuery,
    PaginationMeta,
    SortQuery,
    ErrorEnvelopeDTO,
    HealthcheckPingDTO,
    ensure_utc,
    now_utc,
)

# ---- Common enums & types (as modules) ----
from app.schemas import enums as enums
from app.schemas import types as types

# ---- Subpackages as namespaces ----
from app.schemas import system as system
from app.schemas import calendar as calendar
from app.schemas import venues as venues
from app.schemas import timeplan as timeplan
from app.schemas import taxonomy as taxonomy
from app.schemas import constraints as constraints
from app.schemas import scheduling as scheduling
from app.schemas import staging as staging
from app.schemas import allocations as allocations

__all__ = [
    # Shared base & utilities
    "ORMBase",
    "CreatedStampedReadMixin",
    "UpdatedStampedReadMixin",
    "PaginationQuery",
    "PaginationMeta",
    "SortQuery",
    "ErrorEnvelopeDTO",
    "HealthcheckPingDTO",
    "ensure_utc",
    "now_utc",
    # Modules (import-as-namespace)
    "enums",
    "types",
    "system",
    "calendar",
    "venues",
    "timeplan",
    "taxonomy",
    "constraints",
    "scheduling",
    "staging",
    "allocations",
]
