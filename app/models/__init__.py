# app/models/__init__.py
# pyright: reportUnusedImport=false
# flake8: noqa
"""
app.models package

Explicit, eager imports of ORM models so Base.metadata is fully populated
for Alembic autogenerate and tests.
"""

from __future__ import annotations

# ----- System -----
from app.models.system.users import UserAccount
from app.models.system.user_permissions import UserPermission
from app.models.system.organisations import Organisation
from app.models.system.competitions import Competition
from app.models.system.seasons import Season
from app.models.system.season_days import SeasonDay

# ----- Calendar -----
from app.models.calendar.dates import Date
from app.models.calendar.public_holidays import PublicHoliday
from app.models.calendar.default_times import DefaultTime

# ----- Venues -----
from app.models.venues.venues import Venue
from app.models.venues.courts import Court
from app.models.venues.court_rankings import CourtRanking
from app.models.venues.court_times import CourtTime

# ----- Timeplan -----
from app.models.timeplan.rounds import Round
from app.models.timeplan.round_dates import RoundDate
from app.models.timeplan.round_groups import RoundGroup
from app.models.timeplan.round_settings import RoundSetting
from app.models.timeplan.time_slots import TimeSlot

# ----- Taxonomy -----
from app.models.taxonomy.ages import Age
from app.models.taxonomy.grades import Grade
from app.models.taxonomy.teams import Team

# ----- Constraints -----
from app.models.constraints.allocation_settings import AllocationSetting
from app.models.constraints.age_round_constraints import AgeRoundConstraint
from app.models.constraints.grade_round_constraints import GradeRoundConstraint
from app.models.constraints.age_court_restrictions import AgeCourtRestriction
from app.models.constraints.grade_court_restrictions import GradeCourtRestriction

# ----- Scheduling -----
from app.models.scheduling.scheduling_runs import SchedulingRun
from app.models.scheduling.scheduling_run_events import SchedulingRunEvent
from app.models.scheduling.scheduling_locks import SchedulingLock
from app.models.scheduling.run_exports import RunExport
from app.models.scheduling.run_constraints_snapshot import RunConstraintsSnapshot

# ----- Staging -----
from app.models.staging.p2_allocations import P2Allocation
from app.models.staging.p3_game_allocations import P3GameAllocation
from app.models.staging.p3_bye_allocations import P3ByeAllocation
from app.models.staging.staging_diffs import StagingDiff

# ----- Allocations / Outputs -----
from app.models.allocations.saved_games import SavedGame
from app.models.allocations.saved_byes import SavedBye
from app.models.allocations.final_game_schedule import FinalGameSchedule
from app.models.allocations.final_bye_schedule import FinalByeSchedule

__all__ = [
    # System
    "UserAccount",
    "UserPermission",
    "Organisation",
    "Competition",
    "Season",
    "SeasonDay",
    # Calendar
    "Date",
    "PublicHoliday",
    "DefaultTime",
    # Venues
    "Venue",
    "Court",
    "CourtRanking",
    "CourtTime",
    # Timeplan
    "Round",
    "RoundDate",
    "RoundGroup",
    "RoundSetting",
    "TimeSlot",
    # Taxonomy
    "Age",
    "Grade",
    "Team",
    # Constraints
    "AllocationSetting",
    "AgeRoundConstraint",
    "GradeRoundConstraint",
    "AgeCourtRestriction",
    "GradeCourtRestriction",
    # Scheduling
    "SchedulingRun",
    "SchedulingRunEvent",
    "SchedulingLock",
    "RunExport",
    "RunConstraintsSnapshot",
    # Staging
    "P2Allocation",
    "P3GameAllocation",
    "P3ByeAllocation",
    "StagingDiff",
    # Allocations / Outputs
    "SavedGame",
    "SavedBye",
    "FinalGameSchedule",
    "FinalByeSchedule",
]
