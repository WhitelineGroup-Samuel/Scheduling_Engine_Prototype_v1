# flake8: noqa
"""
Public exports for Staging DTOs.
Import from here when you need schema types in routes/services.
"""

from app.schemas.staging.p2_allocations import (
    P2AllocationBase,
    P2AllocationCreate,
    P2AllocationUpdate,
    P2AllocationRead,
)

from app.schemas.staging.p3_game_allocations import (
    P3GameAllocationBase,
    P3GameAllocationCreate,
    P3GameAllocationUpdate,
    P3GameAllocationRead,
)

from app.schemas.staging.p3_bye_allocations import (
    P3ByeAllocationBase,
    P3ByeAllocationCreate,
    P3ByeAllocationUpdate,
    P3ByeAllocationRead,
)

from app.schemas.staging.staging_diffs import (
    StagingDiffBase,
    StagingDiffCreate,
    StagingDiffUpdate,
    StagingDiffRead,
)

__all__ = [
    # P2 Allocations
    "P2AllocationBase",
    "P2AllocationCreate",
    "P2AllocationUpdate",
    "P2AllocationRead",
    # P3 Game Allocations
    "P3GameAllocationBase",
    "P3GameAllocationCreate",
    "P3GameAllocationUpdate",
    "P3GameAllocationRead",
    # P3 Bye Allocations
    "P3ByeAllocationBase",
    "P3ByeAllocationCreate",
    "P3ByeAllocationUpdate",
    "P3ByeAllocationRead",
    # Staging Diffs
    "StagingDiffBase",
    "StagingDiffCreate",
    "StagingDiffUpdate",
    "StagingDiffRead",
]
