"""
Centralised enums that mirror ERD CHECK constraints.

Keep these values exactly in sync with the database-level constraints
so validation and OpenAPI remain consistent with the schema.
"""

from __future__ import annotations

from enum import Enum

# ---- Rounds ----


class RoundType(str, Enum):
    GRADING = "GRADING"
    REGULAR = "REGULAR"
    FINALS = "FINALS"


class RoundStatus(str, Enum):
    PLANNED = "PLANNED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ---- Scheduling Runs ----


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    ABANDONED = "ABANDONED"


class ProcessType(str, Enum):
    INITIAL = "INITIAL"
    MID = "MID"


class RunType(str, Enum):
    I_RUN_1 = "I_RUN_1"
    I_RUN_2 = "I_RUN_2"
    M_RUN_1 = "M_RUN_1"
    M_RUN_2 = "M_RUN_2"
    M_RUN_3 = "M_RUN_3"


class ResumeCheckpoint(str, Enum):
    BEFORE_P2 = "BEFORE_P2"
    AFTER_P2_BEFORE_P3 = "AFTER_P2_BEFORE_P3"
    AFTER_P3_BEFORE_FINALISE = "AFTER_P3_BEFORE_FINALISE"
    FINALISED = "FINALISED"


# ---- Scheduling Run Events ----


class RunEventStage(str, Enum):
    STEP1 = "STEP1"
    STEP2 = "STEP2"
    STEP3 = "STEP3"
    STEP4 = "STEP4"
    STEP5 = "STEP5"
    FINALISE = "FINALISE"


class RunEventSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


# ---- Venues / Court Times ----


class AvailabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BLOCKED = "BLOCKED"
    MAINTENANCE = "MAINTENANCE"
    EVENT = "EVENT"


class LockState(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"


# ---- Constraints ----


class AllocationRestrictionType(str, Enum):
    NONE = "NONE"
    AGE = "AGE"
    GRADE = "GRADE"
    DUAL = "DUAL"


class GradeCourtRestrictionType(str, Enum):
    GRADE = "GRADE"
    DUAL = "DUAL"


# ---- Byes / Game status (staging & final) ----


class ByeReason(str, Enum):
    ODD_TEAMS = "ODD_TEAMS"
    ERROR_LOOP = "ERROR_LOOP"
    CONSTRAINT = "CONSTRAINT"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"


class SavedGameStatus(str, Enum):
    AFTER_P2_BEFORE_P3 = "AFTER_P2_BEFORE_P3"
    AFTER_P3_BEFORE_FINALISE = "AFTER_P3_BEFORE_FINALISE"
    FINALISED = "FINALISED"


class FinalGameStatus(str, Enum):
    FINALISED = "FINALISED"
    CANCELLED = "CANCELLED"
    FORFEITED = "FORFEITED"
    COMPLETED = "COMPLETED"


class SeasonVisibility(str, Enum):
    PRIVATE = "PRIVATE"
    INTERNAL = "INTERNAL"
    PUBLIC = "PUBLIC"
