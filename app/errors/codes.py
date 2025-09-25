"""
===============================================================================
File: app/errors/codes.py
Purpose
-------
Define the canonical error code catalog for the Scheduling Engine.
Each code includes a stable string identifier, a default severity, and
a CLI exit code to return when surfaced from the CLI layer.

What Codex must implement
-------------------------
- class ErrorCode(Enum or NamedTuple):
    Fields (minimum):
      - code: str (e.g., "SENG-DB-001")
      - exit_code: int (CLI exit status)
      - severity: Literal["INFO","WARN","ERROR","CRITICAL"]
      - http_status: int | None  (optional; reserved for future HTTP layer)

- Define entries for:
    CONFIG_ERROR         = ("SENG-CONFIG-001", 78, "ERROR", 400)
    DB_CONNECTION_ERROR  = ("SENG-DB-001",    65, "CRITICAL", 503)
    DB_MIGRATION_ERROR   = ("SENG-DB-002",    65, "ERROR",    500)
    DB_OPERATION_ERROR   = ("SENG-DB-003",    65, "ERROR",    500)
    VALIDATION_ERROR     = ("SENG-VALIDATION-001", 64, "ERROR", 422)
    NOT_FOUND_ERROR      = ("SENG-DOMAIN-001", 66, "ERROR", 404)
    CONFLICT_ERROR       = ("SENG-DOMAIN-002", 69, "ERROR", 409)
    EXTERNAL_SERVICE_ERROR = ("SENG-EXT-001", 70, "ERROR", 502)
    TIMEOUT_ERROR        = ("SENG-EXT-002", 75, "ERROR", 504)
    IO_ERROR             = ("SENG-IO-001", 74, "ERROR", 500)
    UNKNOWN_ERROR        = ("SENG-UNKNOWN-000", 1, "CRITICAL", 500)

Implementation pattern (no ambiguity)
------------------------------------
- Implement ErrorCode as an `enum.Enum` where each member value is a 4-tuple
  `(code, exit_code, severity, http_status)`. Provide typed properties so
  usage is ergonomic:

    class ErrorCode(Enum):
        CONFIG_ERROR = ("SENG-CONFIG-001", 78, "ERROR", 400)
        ...

        @property
        def code(self) -> str: ...
        @property
        def exit_code(self) -> int: ...
        @property
        def severity(self) -> Literal["INFO","WARN","ERROR","CRITICAL"]: ...
        @property
        def http_status(self) -> int | None: ...

- Export: `__all__ = ["ErrorCode"]`

Notes
-----
- Codes are **stable** once released; new conditions get new codes.
- Exit codes follow sysexits-like semantics where reasonable.
===============================================================================
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

SeverityLiteral = Literal["INFO", "WARN", "ERROR", "CRITICAL"]


class ErrorCode(Enum):
    """Canonical catalog of Scheduling Engine error codes."""

    CONFIG_ERROR = (
        "SENG-CONFIG-001",
        78,
        "ERROR",
        400,
    )
    DB_CONNECTION_ERROR = (
        "SENG-DB-001",
        65,
        "CRITICAL",
        503,
    )
    DB_MIGRATION_ERROR = (
        "SENG-DB-002",
        65,
        "ERROR",
        500,
    )
    DB_OPERATION_ERROR = (
        "SENG-DB-003",
        65,
        "ERROR",
        500,
    )
    VALIDATION_ERROR = (
        "SENG-VALIDATION-001",
        64,
        "ERROR",
        422,
    )
    NOT_FOUND_ERROR = (
        "SENG-DOMAIN-001",
        66,
        "ERROR",
        404,
    )
    CONFLICT_ERROR = (
        "SENG-DOMAIN-002",
        69,
        "ERROR",
        409,
    )
    EXTERNAL_SERVICE_ERROR = (
        "SENG-EXT-001",
        70,
        "ERROR",
        502,
    )
    TIMEOUT_ERROR = (
        "SENG-EXT-002",
        75,
        "ERROR",
        504,
    )
    IO_ERROR = (
        "SENG-IO-001",
        74,
        "ERROR",
        500,
    )
    UNKNOWN_ERROR = (
        "SENG-UNKNOWN-000",
        1,
        "CRITICAL",
        500,
    )

    @property
    def code(self) -> str:
        """Return the stable string identifier for this error code."""

        return self.value[0]

    @property
    def exit_code(self) -> int:
        """Return the CLI exit status associated with this error."""

        return self.value[1]

    @property
    def severity(self) -> SeverityLiteral:
        """Return the default severity for this error type."""

        return self.value[2]

    @property
    def http_status(self) -> int | None:
        """Return the HTTP status mapped to this error, if defined."""

        return self.value[3]


__all__ = ["ErrorCode"]
