from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class RunConstraintsSnapshotRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for RunConstraintsSnapshot rows (scheduling/run_constraints_snapshot.py).

    When implementing:
    - Replace `model` with RunConstraintsSnapshot.
    - Add create_from_current_constraints(run_id, season_day_id).
    - Provide get_for_run(run_id) for audit/debug UIs.
    """

    model: type[Any] = object  # TODO: set to RunConstraintsSnapshot model class
