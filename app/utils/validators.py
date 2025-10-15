"""Reusable validation helpers for configuration, CLI, and schema inputs."""

from __future__ import annotations

import re
from typing import Any, Final
from urllib.parse import SplitResult, urlsplit, urlunsplit

_DEFAULT_LOG_LEVELS: Final[set[str]] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_DEFAULT_ENVS: Final[set[str]] = {"dev", "test", "prod"}
_TRUTHY_STRINGS: Final[set[str]] = {"1", "true", "t", "yes", "y", "on"}
_FALSEY_STRINGS: Final[set[str]] = {"0", "false", "f", "no", "n", "off"}
_NON_EMPTY = re.compile(r"\S")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URL = re.compile(r"^https?://[^\s/:]+(?::\d+)?(?:/[^\s]*)?$", re.IGNORECASE)


def validate_url(
    url: str,
    *,
    schemes: tuple[str, ...] = (
        "postgresql",
        "postgresql+psycopg",
        "postgresql+psycopg2",
    ),
) -> str:
    """Validate a database connection URL and normalize supported schemes.

    Args:
        url: The URL string to validate.
        schemes: Allowed URL schemes, compared case-insensitively.

    Returns:
        str: The validated (and possibly normalized) URL string.

    Raises:
        ValueError: If the scheme or network location is invalid.
    """

    parsed = urlsplit(url)
    # Normalize legacy driver tag *before* validation so old URLs still pass
    scheme_in = parsed.scheme
    scheme_lower = scheme_in.lower()
    mapped_scheme = "postgresql+psycopg" if scheme_lower == "postgresql+psycopg2" else scheme_in

    if not parsed.netloc:
        raise ValueError("URL must include network location")

    allowed_schemes = {item.lower() for item in schemes}
    if mapped_scheme.lower() not in allowed_schemes:
        raise ValueError(f"Unsupported URL scheme: {scheme_in}")

    # If normalization changed the scheme, rebuild the URL; otherwise return input
    if mapped_scheme != scheme_in:
        normalized = parsed._replace(scheme=mapped_scheme)
        return urlunsplit(normalized)
    return url


def validate_log_level(value: str) -> str:
    """Validate logging level names and return the canonical uppercase form.

    Args:
        value: The candidate logging level string.

    Returns:
        str: The validated uppercase logging level.

    Raises:
        ValueError: If ``value`` is not a supported level.
    """

    upper_value = value.strip().upper()
    if upper_value not in _DEFAULT_LOG_LEVELS:
        raise ValueError(f"Unsupported log level: {value}")
    return upper_value


def validate_env(value: str) -> str:
    """Validate environment designators (dev/test/prod) and return lowercase.

    Args:
        value: The environment name to validate.

    Returns:
        str: The normalized lower-case environment string.

    Raises:
        ValueError: If ``value`` does not match an accepted environment.
    """

    lowered = value.strip().lower()
    if lowered not in _DEFAULT_ENVS:
        raise ValueError(f"Unsupported environment: {value}")
    return lowered


def coerce_bool(value: Any) -> bool:
    """Coerce common representations of truthy/falsey values into a boolean.

    Args:
        value: The incoming value, potentially a string, int, or bool.

    Returns:
        bool: ``True`` or ``False`` depending on ``value``.

    Raises:
        ValueError: If the value cannot be interpreted as a boolean.
    """

    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUTHY_STRINGS:
            return True
        if normalized in _FALSEY_STRINGS:
            return False
    raise ValueError(f"Cannot coerce value to bool: {value!r}")


def redact_url_credentials(url: str) -> str:
    """Redact credentials from a connection URL while preserving other parts.

    Args:
        url: The potentially credentialed URL.

    Returns:
        str: A sanitized URL with any username/password removed.
    """

    parsed = urlsplit(url)
    hostname = parsed.hostname
    if hostname is None:
        # Remove potential credentials when hostname is missing entirely.
        netloc = parsed.netloc.rsplit("@", maxsplit=1)[-1]
    else:
        host = hostname
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        netloc = host
        if parsed.port is not None:
            netloc = f"{netloc}:{parsed.port}"
    sanitized = SplitResult(
        scheme=parsed.scheme,
        netloc=netloc,
        path=parsed.path,
        query=parsed.query,
        fragment=parsed.fragment,
    )
    return urlunsplit(sanitized)


def is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(_NON_EMPTY.search(value))


def is_valid_email(value: str) -> bool:
    return bool(_EMAIL.match(value))


def is_valid_url(value: str) -> bool:
    return bool(_URL.match(value))


__all__ = [
    "validate_url",
    "validate_log_level",
    "validate_env",
    "coerce_bool",
    "redact_url_credentials",
    "is_non_empty_str",
    "is_valid_email",
    "is_valid_url",
]
