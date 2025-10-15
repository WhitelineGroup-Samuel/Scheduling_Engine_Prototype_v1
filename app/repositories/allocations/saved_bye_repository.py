from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class SavedByeRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for SavedBye rows (allocations/saved_byes.py).

    When implementing:
    - Replace `model` with SavedBye.
    - Add list_for_run(run_id), list_for_round(round_id).
    - Provide helpers to filter by bye_reason or status.
    """

    model: type[Any] = object  # TODO: set to SavedBye model class
