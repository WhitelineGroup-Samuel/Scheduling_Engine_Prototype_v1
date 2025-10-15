from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.schemas._base import ORMBase

# Keep export types local here; if reused elsewhere, move to enums.py
ExportType = Literal["CSV", "PDF", "ZIP", "XLSX"]


class RunExportBase(ORMBase):
    """
    Client-editable/business fields for a run export record.
    """

    run_id: int
    export_type: ExportType
    file_path: str
    created_at: datetime | None = None  # server default if omitted


class RunExportCreate(RunExportBase):
    """
    Create payload for RunExport.
    """

    pass


class RunExportUpdate(ORMBase):
    """
    Partial update for RunExport — all fields optional.
    """

    run_id: int | None = None
    export_type: ExportType | None = None
    file_path: str | None = None
    created_at: datetime | None = None


class RunExportRead(RunExportBase):
    """
    Read payload for RunExport (includes identifier).
    """

    export_id: int
