from __future__ import annotations

from typing import Any, Literal

from app.schemas._base import CreatedStampedReadMixin, ORMBase

EntityType = Literal["P2_ALLOCATION", "P3_ALLOCATION", "COMPOSITE_ALLOCATION"]
ChangeType = Literal["ADD", "CHANGE", "REMOVE"]


class StagingDiffBase(ORMBase):
    """
    Client-editable/business fields for a staging diff entry.
    """

    run_id: int
    entity_type: EntityType
    entity_id: str
    change_type: ChangeType
    before_json: dict[str, Any] | None = None
    after_json: dict[str, Any] | None = None


class StagingDiffCreate(StagingDiffBase):
    """
    Create payload for StagingDiff.
    """

    pass


class StagingDiffUpdate(ORMBase):
    """
    Partial update for StagingDiff — all fields optional.
    """

    run_id: int | None = None
    entity_type: EntityType | None = None
    entity_id: str | None = None
    change_type: ChangeType | None = None
    before_json: dict[str, Any] | None = None
    after_json: dict[str, Any] | None = None


class StagingDiffRead(StagingDiffBase, CreatedStampedReadMixin):
    """
    Read payload for StagingDiff (includes identifier and audit fields).
    """

    diff_id: int
