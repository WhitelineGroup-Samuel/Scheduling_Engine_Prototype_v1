"""Tests for UUID helpers ensuring deterministic formatting and uniqueness."""

from __future__ import annotations

import re

import pytest

from app.utils.ids import new_uuid_str

pytestmark = pytest.mark.unit

_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def test_new_uuid_str_format() -> None:
    """Generated UUID strings should match the canonical UUID4 format."""

    value = new_uuid_str()

    assert len(value) == 36
    assert _UUID_PATTERN.match(value), f"Unexpected UUID4 format: {value}"


def test_new_uuid_str_uniqueness() -> None:
    """A batch of generated UUID strings should be globally unique."""

    batch = [new_uuid_str() for _ in range(1000)]

    assert len(batch) == len(set(batch)), "Duplicate UUIDs detected in generated batch"
