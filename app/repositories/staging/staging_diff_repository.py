from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class StagingDiffRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for StagingDiff rows (staging/staging_diffs.py).

    When implementing:
    - Replace `model` with StagingDiff.
    - Add list_for_run(run_id), list_by_entity(entity_type, entity_id).
    - Order by created_at ascending for review UX.
    """

    model: type[Any] = object  # TODO: set to StagingDiff model class
