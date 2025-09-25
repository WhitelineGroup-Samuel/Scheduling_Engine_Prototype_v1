"""
===============================================================================
File: app/errors/exceptions.py
Purpose
-------
Define the base application exception (`AppError`) and concrete subclasses.
Each subclass binds to an ErrorCode and carries a safe message and optional
context dict that will be emitted as structured log extras.

What Codex must implement
-------------------------
- class AppError(Exception):
    - code: str
    - message: str
    - context: dict[str, Any] | None
    - exit_code: int
    - severity: Literal["INFO","WARN","ERROR","CRITICAL"]
    - __str__ returns "<code> <message>"

- Concrete subclasses (minimum):
    ConfigError, DBConnectionError, DBMigrationError, DBOperationError,
    ValidationError, NotFoundError, ConflictError, ExternalServiceError,
    TimeoutError, IOErrorApp, UnknownError

  Each subclass:
    - Sets default `code`, `exit_code`, `severity` from ErrorCode catalog.
    - Accepts `message: str | None` (fallback to a sensible default).
    - Accepts `context: dict | None` (safe extras; never secrets).

- Helper:
    def from_exception(exc: BaseException) -> AppError
      (optional—can live in handlers instead)

Notes
-----
- Keep messages succinct and actionable.
- Do not embed secrets in messages or context.
===============================================================================
"""
