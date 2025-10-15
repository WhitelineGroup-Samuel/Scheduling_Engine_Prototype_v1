from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from app.schemas._base import ORMBase

PhaseLiteral = Literal["P2", "P3", "COMPOSITE"]


class RunConstraintsSnapshotBase(ORMBase):
    """
    Client-editable/business fields for a constraints snapshot row.
    """

    run_id: int
    phase: PhaseLiteral
    constraints_json: dict[str, Any]
    created_at: datetime | None = None  # server default if omitted


class RunConstraintsSnapshotCreate(RunConstraintsSnapshotBase):
    """
    Create payload for RunConstraintsSnapshot.
    """

    pass


class RunConstraintsSnapshotUpdate(ORMBase):
    """
    Partial update for RunConstraintsSnapshot — all fields optional.
    """

    run_id: int | None = None
    phase: PhaseLiteral | None = None
    constraints_json: dict[str, Any] | None = None
    created_at: datetime | None = None


class RunConstraintsSnapshotRead(RunConstraintsSnapshotBase):
    """
    Read payload for RunConstraintsSnapshot (includes identifier).
    """

    snapshot_id: int
