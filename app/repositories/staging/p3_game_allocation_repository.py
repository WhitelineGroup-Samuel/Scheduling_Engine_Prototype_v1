from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class P3GameAllocationRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for P3GameAllocation rows (staging/p3_game_allocations.py).

    When implementing:
    - Replace `model` with P3GameAllocation.
    - Add list_for_run(run_id), list_for_round(round_id).
    - Provide helpers to find allocations by team/court_time.
    """

    model: type[Any] = object  # TODO: set to P3GameAllocation model class
