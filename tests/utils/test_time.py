"""Tests covering time utility helpers for timezone awareness and parsing."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from types import ModuleType
from typing import ContextManager

import pytest

from app.utils import time as time_utils

pytestmark = pytest.mark.unit

TO_LOCAL = getattr(time_utils, "to_local", None)
PARSE_ISO8601 = getattr(time_utils, "parse_iso8601", None)

_time_fixture_module: ModuleType | None
try:
    _time_fixture_module = importlib.import_module("tests.fixtures.time")
except ModuleNotFoundError:
    _time_fixture_module = None

if _time_fixture_module and hasattr(_time_fixture_module, "freeze_time"):
    freeze_time = _time_fixture_module.freeze_time
else:

    @pytest.fixture(name="freeze_time")
    def freeze_time_fixture() -> Callable[[datetime], ContextManager[datetime]]:
        """Provide a minimal freezer context manager for deterministic tests."""

        @contextmanager
        def _freezer(target: datetime) -> Iterator[datetime]:
            yield target

        return _freezer


def test_now_utc_is_aware() -> None:
    """The now_utc helper should return a timezone-aware UTC datetime."""

    value = time_utils.now_utc()

    assert value.tzinfo is not None
    assert value.tzinfo.utcoffset(value) == timedelta(0)


@pytest.mark.skipif(TO_LOCAL is None, reason="to_local helper not implemented")
def test_to_local_converts_correctly(
    freeze_time: Callable[[datetime], ContextManager[datetime]],
) -> None:
    """Converting UTC timestamps to the Melbourne timezone preserves awareness."""

    assert TO_LOCAL is not None
    fixed_utc = datetime(2024, 1, 1, tzinfo=UTC)
    with freeze_time(fixed_utc):
        local = TO_LOCAL(fixed_utc, tz="Australia/Melbourne")
    assert local.tzinfo is not None
    offset = local.utcoffset() or timedelta(0)
    assert offset in {timedelta(hours=10), timedelta(hours=11)}


@pytest.mark.skipif(PARSE_ISO8601 is None, reason="parse_iso8601 helper not implemented")
def test_parse_iso8601_strict() -> None:
    """ISO8601 parsing should yield aware UTC datetimes and reject invalid strings."""

    assert PARSE_ISO8601 is not None
    parsed = PARSE_ISO8601("2024-01-01T00:00:00Z")
    assert parsed.tzinfo is not None
    assert parsed.tzinfo.utcoffset(parsed) == timedelta(0)

    with pytest.raises(ValueError):
        PARSE_ISO8601("not-a-timestamp")
