"""Time control helpers to make integration tests deterministic."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

import pytest

try:  # pragma: no cover - optional dependency
    from freezegun import freeze_time as _freezegun_freeze_time
except ImportError:  # pragma: no cover - executed when freezegun missing
    _freezegun_freeze_time = None

from app.utils import time as time_utils

_FROZEN_INSTANT = datetime(2024, 1, 1, tzinfo=timezone.utc)


@contextmanager
def fixed_utc(dt: datetime) -> Iterator[None]:
    """Temporarily freeze :func:`app.utils.time.now_utc` at ``dt``."""

    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError("Frozen datetime must be timezone-aware (UTC).")

    if _freezegun_freeze_time is not None:
        with _freezegun_freeze_time(dt):
            yield
        return

    original_now_utc = time_utils.now_utc

    def _patched_now_utc() -> datetime:
        """Return the frozen UTC instant."""

        return dt

    setattr(time_utils, "now_utc", _patched_now_utc)
    try:
        yield
    finally:
        setattr(time_utils, "now_utc", original_now_utc)


@pytest.fixture(scope="function")
def freeze_time() -> Iterator[datetime]:
    """Freeze application time to ``2024-01-01T00:00:00Z`` for the duration of a test."""

    with fixed_utc(_FROZEN_INSTANT):
        yield _FROZEN_INSTANT
