# flake8: noqa
"""
Top-level repositories public exports.

This module re-exports:
- Base primitives (BaseRepository, common mixins)
- All concrete repository classes from each domain package
"""

# Base primitives
from app.repositories.base import BaseRepository
from app.repositories.mixins import (
    OrgScopedMixin,
    CompetitionScopedMixin,
    SeasonScopedMixin,
    SeasonDayScopedMixin,
    OrderingMixin,
)

# ---- Domain repositories (imported from their package __init__.py) ----

# System
from app.repositories.system import (
    OrganisationRepository,
    CompetitionRepository,
    SeasonRepository,
    SeasonDayRepository,
    UserPermissionRepository,
    UserAccountRepository,
)

# Venues
from app.repositories.venues import (
    VenueRepository,
    CourtRepository,
    CourtRankingRepository,
    CourtTimeRepository,
)

# Calendar
from app.repositories.calendar import (
    DateRepository,
    DefaultTimeRepository,
    PublicHolidayRepository,
)

# Taxonomy
from app.repositories.taxonomy import (
    AgeRepository,
    GradeRepository,
    TeamRepository,
)

# Timeplan
from app.repositories.timeplan import (
    RoundRepository,
    RoundSettingRepository,
    TimeSlotRepository,
    RoundDateRepository,
    RoundGroupRepository,
)

# Constraints
from app.repositories.constraints import (
    AllocationSettingRepository,
    AgeRoundConstraintRepository,
    GradeRoundConstraintRepository,
    AgeCourtRestrictionRepository,
    GradeCourtRestrictionRepository,
)

# Scheduling
from app.repositories.scheduling import (
    SchedulingRunRepository,
    SchedulingRunEventRepository,
    SchedulingLockRepository,
    RunConstraintsSnapshotRepository,
    RunExportRepository,
)

# Staging
from app.repositories.staging import (
    P2AllocationRepository,
    P3GameAllocationRepository,
    P3ByeAllocationRepository,
    StagingDiffRepository,
)

# Allocations
from app.repositories.allocations import (
    SavedGameRepository,
    SavedByeRepository,
    FinalGameScheduleRepository,
    FinalByeScheduleRepository,
)

__all__ = [
    # Base primitives
    "BaseRepository",
    "OrgScopedMixin",
    "CompetitionScopedMixin",
    "SeasonScopedMixin",
    "SeasonDayScopedMixin",
    "OrderingMixin",
    # System
    "OrganisationRepository",
    "CompetitionRepository",
    "SeasonRepository",
    "SeasonDayRepository",
    "UserPermissionRepository",
    "UserAccountRepository",
    # Venues
    "VenueRepository",
    "CourtRepository",
    "CourtRankingRepository",
    "CourtTimeRepository",
    # System
    "DateRepository",
    "DefaultTimeRepository",
    "PublicHolidayRepository",
    # Taxonomy
    "AgeRepository",
    "GradeRepository",
    "TeamRepository",
    # Timeplan
    "RoundRepository",
    "RoundSettingRepository",
    "TimeSlotRepository",
    "RoundDateRepository",
    "RoundGroupRepository",
    # Constraints
    "AllocationSettingRepository",
    "AgeRoundConstraintRepository",
    "GradeRoundConstraintRepository",
    "AgeCourtRestrictionRepository",
    "GradeCourtRestrictionRepository",
    # Scheduling
    "SchedulingRunRepository",
    "SchedulingRunEventRepository",
    "SchedulingLockRepository",
    "RunConstraintsSnapshotRepository",
    "RunExportRepository",
    # Staging
    "P2AllocationRepository",
    "P3GameAllocationRepository",
    "P3ByeAllocationRepository",
    "StagingDiffRepository",
    # Allocations
    "SavedGameRepository",
    "SavedByeRepository",
    "FinalGameScheduleRepository",
    "FinalByeScheduleRepository",
]
