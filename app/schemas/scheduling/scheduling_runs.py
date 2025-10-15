from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import (
    ProcessType,
    ResumeCheckpoint,
    RunStatus,
    RunType,
)


def _empty_int_list() -> list[int]:
    return []


class SchedulingRunBase(ORMBase):
    """
    Client-editable/business fields for a scheduling run.
    """

    season_id: int
    season_day_id: int
    run_status: RunStatus
    process_type: ProcessType
    run_type: RunType | None = None
    s1_check_results: str
    round_ids: list[int] = Field(default_factory=_empty_int_list)
    seed_master: str
    resume_checkpoint: ResumeCheckpoint
    config_hash: str | None = None
    metrics: dict[str, Any] | None = None
    error_code: str | None = None
    error_details: dict[str, Any] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    idempotency_key: str


class SchedulingRunCreate(SchedulingRunBase):
    """
    Create payload for SchedulingRun.
    `created_by_user_id` is set by the service layer from the current user.
    """

    pass


class SchedulingRunUpdate(ORMBase):
    """
    Partial update for SchedulingRun — all fields optional.
    Apply with exclude_unset=True.
    """

    run_status: RunStatus | None = None
    process_type: ProcessType | None = None
    run_type: RunType | None = None
    s1_check_results: str | None = None
    round_ids: list[int] | None = None
    seed_master: str | None = None
    resume_checkpoint: ResumeCheckpoint | None = None
    config_hash: str | None = None
    metrics: dict[str, Any] | None = None
    error_code: str | None = None
    error_details: dict[str, Any] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class SchedulingRunRead(SchedulingRunBase, CreatedStampedReadMixin):
    """
    Read payload for SchedulingRun (includes identifiers and audit).
    """

    run_id: int
