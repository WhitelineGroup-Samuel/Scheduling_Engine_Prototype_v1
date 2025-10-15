from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class SavedGameRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for SavedGame rows (allocations/saved_games.py).

    When implementing:
    - Replace `model` with SavedGame.
    - Add list_for_run(run_id), list_for_round(round_id), etc.
    - Consider helpers to filter by game_status.
    """

    model: type[Any] = object  # TODO: set to SavedGame model class
