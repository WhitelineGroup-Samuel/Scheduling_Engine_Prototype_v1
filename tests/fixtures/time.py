"""Time control helpers to make integration tests deterministic."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any, ContextManager

import pytest

from app.utils import time as time_utils

# Optional dependency: "freezegun" is only needed if installed in the dev env.
_freezegun_freeze_time: Callable[[Any], ContextManager[Any]] | None
try:
    _fz_mod = importlib.import_module("freezegun")
    _freezegun_freeze_time = getattr(_fz_mod, "freeze_time", None)
except Exception:
    _freezegun_freeze_time = None

_FROZEN_INSTANT = datetime(2024, 1, 1, tzinfo=UTC)


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

    time_utils.now_utc = _patched_now_utc
    try:
        yield
    finally:
        time_utils.now_utc = original_now_utc


@pytest.fixture(scope="function")
def freeze_time() -> Callable[[datetime], ContextManager[datetime]]:
    """Return a factory that yields a context manager to freeze app time at a given aware UTC datetime."""

    @contextmanager
    def _freezer(dt: datetime) -> Iterator[datetime]:
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("Frozen datetime must be timezone-aware (UTC).")
        with fixed_utc(dt):
            yield dt

    return _freezer
