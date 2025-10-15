from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class P2AllocationRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for P2Allocation rows (staging/p2_allocations.py).

    When implementing:
    - Replace `model` with P2Allocation.
    - Add list_for_run(run_id) and list_for_round(round_id).
    - Provide upsert/replace patterns for re-runs if required.
    """

    model: type[Any] = object  # TODO: set to P2Allocation model class
