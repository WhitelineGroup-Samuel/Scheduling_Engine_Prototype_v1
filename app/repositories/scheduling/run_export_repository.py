from __future__ import annotations

from typing import Any

from app.repositories.base import BaseRepository


class RunExportRepository(BaseRepository[Any]):
    """
    PLACEHOLDER

    Repository for RunExport rows (scheduling/run_exports.py).

    When implementing:
    - Replace `model` with RunExport.
    - Add create_export(run_id, export_type, path/uri, metadata).
    - Add list_for_run(run_id), latest_for_run(run_id).
    """

    model: type[Any] = object  # TODO: set to RunExport model class
