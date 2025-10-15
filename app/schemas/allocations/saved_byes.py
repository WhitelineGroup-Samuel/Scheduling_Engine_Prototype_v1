from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import ByeReason, SavedGameStatus


class SavedByeBase(ORMBase):
    """
    Client-editable/business fields for a saved bye (checkpoint).
    """

    run_id: int
    round_id: int
    age_id: int
    grade_id: int
    team_id: int
    bye_reason: ByeReason | None = None
    game_status: SavedGameStatus


class SavedByeCreate(SavedByeBase):
    """
    Create payload for SavedBye.
    Service injects created_by_user_id from auth context.
    """

    pass


class SavedByeUpdate(ORMBase):
    """
    Partial update for SavedBye — all fields optional.
    """

    run_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    team_id: int | None = None
    bye_reason: ByeReason | None = None
    game_status: SavedGameStatus | None = None


class SavedByeRead(SavedByeBase, CreatedStampedReadMixin):
    """
    Read payload for SavedBye (includes identifier and audit fields).
    """

    saved_bye_id: int
