from __future__ import annotations

import importlib
from collections.abc import Callable
from datetime import UTC, datetime

import pytest


def _get_parse_iso8601() -> Callable[[str], datetime]:
    """
    Locate a parse_iso8601 function. Prefer app.utils.time.parse_iso8601,
    else try app.schemas._base.parse_iso8601. If not found, skip.
    """
    try:
        mod = importlib.import_module("app.utils.time")
        func = getattr(mod, "parse_iso8601", None)
        if callable(func):
            return func  # type: ignore[return-value]
    except Exception:
        pass

    try:
        mod = importlib.import_module("app.schemas._base")
        func = getattr(mod, "parse_iso8601", None)
        if callable(func):
            return func  # type: ignore[return-value]
    except Exception:
        pass

    pytest.skip("parse_iso8601 helper not available.")
    raise AssertionError("unreachable")


def test_parse_iso8601_z_suffix() -> None:
    parse_iso8601 = _get_parse_iso8601()
    dt = parse_iso8601("2025-01-01T12:00:00Z")
    assert isinstance(dt, datetime)
    assert dt.tzinfo is UTC
    assert dt.hour == 12 and dt.minute == 0 and dt.second == 0


def test_parse_iso8601_positive_offset_normalizes_to_utc() -> None:
    parse_iso8601 = _get_parse_iso8601()
    dt = parse_iso8601("2025-01-01T12:00:00+10:00")
    # Local 12:00 at +10 → 02:00 UTC
    assert dt.tzinfo is UTC
    assert dt.hour == 2 and dt.minute == 0


def test_parse_iso8601_negative_offset_with_minutes() -> None:
    parse_iso8601 = _get_parse_iso8601()
    dt = parse_iso8601("2025-01-01T12:00:00-04:30")
    # Local 12:00 at -04:30 → 16:30 UTC
    assert dt.tzinfo is UTC
    assert dt.hour == 16 and dt.minute == 30


@pytest.mark.parametrize(
    "bad",
    [
        "2025-01-01T12:00:00Zjunk",  # trailing garbage
        "2025-13-01T00:00:00Z",  # bad month
        "not-a-date",  # totally invalid
        "2025-01-01 12:00:00+10:00x",  # invalid tail
    ],
)
def test_parse_iso8601_invalid_inputs_raise(bad: str) -> None:
    parse_iso8601 = _get_parse_iso8601()
    with pytest.raises(Exception):
        _ = parse_iso8601(bad)
