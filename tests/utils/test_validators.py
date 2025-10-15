"""Tests ensuring validator helpers return expected boolean outcomes."""

from __future__ import annotations

import pytest

from app.utils import validators as validators_module

pytestmark = pytest.mark.unit

IS_NON_EMPTY_STR = getattr(validators_module, "is_non_empty_str", None)
IS_VALID_EMAIL = getattr(validators_module, "is_valid_email", None)
IS_VALID_URL = getattr(validators_module, "is_valid_url", None)


@pytest.mark.skipif(IS_NON_EMPTY_STR is None, reason="is_non_empty_str helper not implemented")
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", False),
        (" ", False),
        ("abc", True),
        (None, False),
        (123, False),
    ],
)
def test_is_non_empty_str_table(value: object, expected: bool) -> None:
    """Non-empty string validation should distinguish truthy and falsey inputs."""

    assert IS_NON_EMPTY_STR is not None
    result = bool(IS_NON_EMPTY_STR(value))
    assert result is expected, f"Expected {expected} for input {value!r}, received {result}"


@pytest.mark.skipif(IS_VALID_EMAIL is None, reason="is_valid_email helper not implemented")
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a@b.com", True),
        ("first.last+tag@domain.co.uk", True),
        ("a@", False),
        ("@b.com", False),
        ("a@b", False),
        ("a b@c.com", False),
        ("", False),
    ],
)
def test_is_valid_email_table(value: str, expected: bool) -> None:
    """Email validation should accept common valid forms and reject malformed ones."""

    assert IS_VALID_EMAIL is not None
    result = bool(IS_VALID_EMAIL(value))
    assert result is expected, f"Expected {expected} for email {value!r}, received {result}"


@pytest.mark.skipif(IS_VALID_URL is None, reason="is_valid_url helper not implemented")
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("http://example.com", True),
        ("https://example.com/path?query=1", True),
        ("https://example.com:8443/api", True),
        ("ftp://example.com", False),
        ("example.com", False),
        ("http://", False),
        ("http://exa mple.com", False),
    ],
)
def test_is_valid_url_table(value: str, expected: bool) -> None:
    """URL validation should limit accepted schemes and reject malformed inputs."""

    assert IS_VALID_URL is not None
    result = bool(IS_VALID_URL(value))
    assert result is expected, f"Expected {expected} for URL {value!r}, received {result}"
