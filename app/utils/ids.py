"""Identifier generation and validation utilities for UUID and ULID values."""

from __future__ import annotations

import secrets
import time
import uuid
from typing import Final

_ULID_ALPHABET: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_uuid() -> uuid.UUID:
    """Return a freshly generated UUID4 instance.

    Returns:
        uuid.UUID: A random UUID version 4 value.
    """

    return uuid.uuid4()


def new_uuid_str() -> str:
    """Return the string representation of a newly generated UUID4.

    Returns:
        str: The canonical string form of :func:`new_uuid`.
    """

    return str(new_uuid())


def is_uuid(value: str | uuid.UUID | None) -> bool:
    """Determine whether ``value`` represents a valid UUID.

    Args:
        value: The candidate value, provided as a string or :class:`uuid.UUID`.

    Returns:
        bool: ``True`` when ``value`` can be parsed into a UUID.
    """

    if isinstance(value, uuid.UUID):
        return True
    if not value:
        return False
    try:
        uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return False
    return True


def _encode_ulid(value: int) -> str:
    """Encode a 128-bit integer into the canonical 26 character ULID form.

    Args:
        value: The 128-bit integer to encode.

    Returns:
        str: The encoded ULID string.
    """

    chars = ["0"] * 26
    for index in range(26):
        shift = (25 - index) * 5
        chars[index] = _ULID_ALPHABET[(value >> shift) & 0x1F]
    return "".join(chars)


def new_ulid() -> str:
    """Return a lexicographically sortable ULID string.

    Returns:
        str: A 26-character ULID encoded using the Crockford base32 alphabet.
    """

    timestamp_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    randomness = secrets.randbits(80)
    combined = (timestamp_ms << 80) | randomness
    return _encode_ulid(combined)


__all__ = [
    "new_uuid",
    "new_uuid_str",
    "is_uuid",
    "new_ulid",
]
