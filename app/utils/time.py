"""Datetime helpers with UTC conversions and lightweight timing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from time import monotonic
from types import TracebackType
from typing import Callable, Literal, TypeVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def now_utc() -> datetime:
    """Return the current UTC time as an aware :class:`datetime` instance."""

    return datetime.now(timezone.utc)


def now_tz(tz_name: str) -> datetime:
    """Return the current time in the supplied IANA zone as an aware datetime.

    Args:
        tz_name: Name of the timezone as defined in the IANA database.

    Returns:
        datetime: The timezone-aware datetime representing ``tz_name`` now.

    Raises:
        ValueError: If ``tz_name`` is not a recognised timezone identifier.
    """

    try:
        zone = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown time zone: {tz_name}") from exc
    return datetime.now(zone)


def to_utc(dt: datetime) -> datetime:
    """Convert ``dt`` to an aware UTC :class:`datetime`.

    Naive datetimes are assumed to be expressed in UTC already.

    Args:
        dt: The datetime to convert.

    Returns:
        datetime: An aware UTC datetime instance.
    """

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_dt(dt: datetime) -> str:
    """Format ``dt`` as an ISO 8601 string normalised to UTC with ``Z`` suffix.

    Args:
        dt: The datetime to format.

    Returns:
        str: An ISO formatted representation that ends in ``Z``.
    """

    utc_dt = to_utc(dt)
    iso = utc_dt.isoformat().replace("+00:00", "Z")
    if not iso.endswith("Z"):
        iso += "Z"
    return iso


def format_duration_ms(start: float, end: float) -> float:
    """Return ``(end - start)`` in milliseconds, rounded to three decimals.

    Args:
        start: Start timestamp from :func:`time.monotonic`.
        end: End timestamp from :func:`time.monotonic`.

    Returns:
        float: The elapsed duration in milliseconds.
    """

    return round((end - start) * 1000.0, 3)


@dataclass
class Timer:
    """Measure elapsed time using :func:`time.monotonic` within a context block."""

    _start: float | None = None
    _end: float | None = None

    def __enter__(self) -> "Timer":
        """Start timing and return ``self`` for use inside the ``with`` statement."""

        self._start = monotonic()
        self._end = None
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        """Stop timing. Exceptions are not suppressed."""

        self._end = monotonic()
        return False

    @property
    def duration_ms(self) -> float:
        """Return the measured duration in milliseconds, or ``0.0`` if pending."""

        if self._start is None or self._end is None:
            return 0.0
        return format_duration_ms(self._start, self._end)


T = TypeVar("T")


def measure(func: Callable[[], T]) -> tuple[T, float]:
    """Execute ``func`` and return its result alongside the execution time in ms.

    Args:
        func: A callable executed without arguments.

    Returns:
        tuple[T, float]: A tuple of the callable's return value and the elapsed milliseconds.
    """

    start = monotonic()
    result = func()
    end = monotonic()
    return result, format_duration_ms(start, end)


__all__ = [
    "now_utc",
    "now_tz",
    "to_utc",
    "format_dt",
    "format_duration_ms",
    "Timer",
    "measure",
]
