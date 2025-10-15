"""
Common reusable types and constraints for DTOs.

Use these to keep your DTOs concise and consistent across modules.
"""

from __future__ import annotations

from typing import Annotated, Any, NotRequired, TypedDict

from pydantic import Field, StringConstraints

# ---- JSON helpers ----
JSONDict = dict[str, Any]
JSONList = list[Any]
JSONValue = str, int, float, bool, None, JSONDict, JSONList  # handy if you need a recursive union


# ---- Constrained strings you can reuse ----
# Pydantic v2 style constraints via Annotated + StringConstraints

# Slugs: lowercase alphanumerics separated by single hyphens, max 64 chars
SlugStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    ),
]

# Short codes (e.g., team_code, grade_code, court_code) – max 20 chars, allow letters/numbers/underscore/hyphen
Code20 = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=20, pattern=r"^[A-Za-z0-9_-]+$"),
]

# Generic non-empty text (trimmed)
NonEmptyStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]

# Optional hex colour like "#A1B2C3" (if you decide to validate display colours in DTOs)
HexColour = Annotated[
    str,
    StringConstraints(pattern=r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})$"),
]

PositiveInt = Annotated[int, Field(ge=1)]
NonNegInt = Annotated[int, Field(ge=0)]
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


# ---- Optional typed JSON shapes you may tighten later ----


class MetricsPayload(TypedDict, total=False):
    """Loosely-typed metrics container used by scheduling_runs.metrics."""

    allocations: NotRequired[int]
    byes: NotRequired[int]
    warnings: NotRequired[list[str]]
    errors: NotRequired[list[str]]
    extra: NotRequired[JSONDict]


class ErrorDetailsPayload(TypedDict, total=False):
    """Optional detailed error payload used by scheduling_runs.error_details."""

    code: NotRequired[str]
    message: NotRequired[str]
    details: NotRequired[JSONDict]


class RoundRulesPayload(TypedDict, total=False):
    """
    Example rules payload for round_settings.rules.
    Keep this flexible at first; tighten as your rule engine stabilises.
    """

    min_gap_minutes: NotRequired[int]
    allow_back_to_back: NotRequired[bool]
    preferred_start_times: NotRequired[list[str]]  # "HH:MM" strings
    court_rank_strategy: NotRequired[str]
    extra: NotRequired[JSONDict]
