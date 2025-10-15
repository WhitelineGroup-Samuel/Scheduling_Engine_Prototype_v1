from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class P3ByeAllocationRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for P3ByeAllocation rows (staging/p3_bye_allocations.py).

    When implementing:
    - Replace `model` with P3ByeAllocation.
    - Add list_for_run(run_id), list_for_round(round_id).
    - Provide helpers by team/grade/age as needed.
    """

    model: type[Any] = object  # TODO: set to P3ByeAllocation model class
