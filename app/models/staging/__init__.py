# flake8: noqa
"""
Public imports for Staging models so Alembic sees all mappings
and Base.metadata is fully populated.
"""

from app.models.staging.p2_allocations import P2Allocation
from app.models.staging.p3_game_allocations import P3GameAllocation
from app.models.staging.p3_bye_allocations import P3ByeAllocation
from app.models.staging.staging_diffs import StagingDiff

__all__ = ["P2Allocation", "P3GameAllocation", "P3ByeAllocation", "StagingDiff"]
