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

Notes
-----
- Codes are **stable** once released; new conditions get new codes.
- Exit codes follow sysexits-like semantics where reasonable.
===============================================================================
"""
