from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas._base import ORMBase
from app.schemas.enums import RunEventSeverity, RunEventStage


class SchedulingRunEventBase(ORMBase):
    """
    Client-editable/business fields for a scheduling run event.
    """

    run_id: int
    stage: RunEventStage
    severity: RunEventSeverity
    event_message: str = Field(min_length=1)
    context: dict[str, Any] | None = None
    event_time: datetime | None = None  # server default if omitted


class SchedulingRunEventCreate(SchedulingRunEventBase):
    """
    Create payload for SchedulingRunEvent.
    """

    pass


class SchedulingRunEventUpdate(ORMBase):
    """
    Partial update for SchedulingRunEvent — all fields optional.
    """

    run_id: int | None = None
    stage: RunEventStage | None = None
    severity: RunEventSeverity | None = None
    event_message: str | None = None
    context: dict[str, Any] | None = None
    event_time: datetime | None = None


class SchedulingRunEventRead(SchedulingRunEventBase):
    """
    Read payload for SchedulingRunEvent (includes identifier).
    """

    event_id: int
