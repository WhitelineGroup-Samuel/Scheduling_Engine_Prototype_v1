from __future__ import annotations

from app.schemas._base import CreatedStampedReadMixin, ORMBase
from app.schemas.enums import SavedGameStatus


class SavedGameBase(ORMBase):
    """
    Client-editable/business fields for a saved game (checkpoint).
    """

    run_id: int
    round_id: int
    age_id: int
    grade_id: int
    team_a_id: int
    team_b_id: int
    court_time_id: int
    game_status: SavedGameStatus


class SavedGameCreate(SavedGameBase):
    """
    Create payload for SavedGame.
    Service injects created_by_user_id from auth context.
    """

    pass


class SavedGameUpdate(ORMBase):
    """
    Partial update for SavedGame — all fields optional.
    """

    run_id: int | None = None
    round_id: int | None = None
    age_id: int | None = None
    grade_id: int | None = None
    team_a_id: int | None = None
    team_b_id: int | None = None
    court_time_id: int | None = None
    game_status: SavedGameStatus | None = None


class SavedGameRead(SavedGameBase, CreatedStampedReadMixin):
    """
    Read payload for SavedGame (includes identifier and audit fields).
    """

    saved_game_id: int
