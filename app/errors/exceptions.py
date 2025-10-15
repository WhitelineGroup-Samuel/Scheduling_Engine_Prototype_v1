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

  Use subclass name `IOErrorApp` deliberately to avoid clashing with built-in `IOError` alias of `OSError`.

  Each subclass:
    - Sets default `code`, `exit_code`, `severity` from ErrorCode catalog.
    - Accepts `message: str | None` (fallback to a sensible default).
    - Accepts `context: dict | None` (safe extras; never secrets).

- Helper:
    def from_exception(exc: BaseException) -> AppError
      (optional—can live in handlers instead)

- Export `__all__ = ["AppError","ConfigError","DBConnectionError","DBMigrationError",
                     "DBOperationError","ValidationError","NotFoundError","ConflictError",
                     "ExternalServiceError","TimeoutError","IOErrorApp","UnknownError"]`

- `message` must default to a sensible constant per subclass if not provided.
- `context` type: `Mapping[str, object] | None` for read-only safety; store internally as `dict[str, object]`.
- `__str__` returns `"<code> <message>"`; avoid leaking context in `str()`; leave it to logs.

Notes
-----
- Keep messages succinct and actionable.
- Do not embed secrets in messages or context.
- `repr(AppError)` and messages must not include secrets (DB URLs, tokens). If needed, redact with "***".
===============================================================================
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from .codes import ErrorCode, SeverityLiteral


class AppError(Exception):
    """Base class for all Scheduling Engine application errors."""

    code: str
    message: str
    context: MutableMapping[str, object] | None
    exit_code: int
    severity: SeverityLiteral

    def __init__(
        self,
        *,
        code: str,
        message: str,
        exit_code: int,
        severity: SeverityLiteral,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize the application error with structured metadata."""

        super().__init__(f"{code} {message}")
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.severity = severity
        self.context = dict(context) if context else None

    def __str__(self) -> str:
        """Return a concise representation used for CLI and logs."""

        return f"{self.code} {self.message}"


class ConfigError(AppError):
    """Raised when configuration files or environment values are invalid."""

    DEFAULT_MESSAGE = "Invalid configuration detected."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.CONFIG_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class DBConnectionError(AppError):
    """Raised when the application cannot reach the database server."""

    DEFAULT_MESSAGE = "Unable to connect to the database."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.DB_CONNECTION_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class DBMigrationError(AppError):
    """Raised when database migrations fail to complete successfully."""

    DEFAULT_MESSAGE = "Database migration failed."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.DB_MIGRATION_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class DBOperationError(AppError):
    """Raised when a database operation encounters an error."""

    DEFAULT_MESSAGE = "Database operation failed."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.DB_OPERATION_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class ValidationError(AppError):
    """Raised when user input or state validation fails."""

    DEFAULT_MESSAGE = "Validation failed."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.VALIDATION_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class NotFoundError(AppError):
    """Raised when the requested resource does not exist."""

    DEFAULT_MESSAGE = "Requested resource was not found."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.NOT_FOUND_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class ConflictError(AppError):
    """Raised when a domain conflict prevents the requested action."""

    DEFAULT_MESSAGE = "Resource conflict detected."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.CONFLICT_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class ExternalServiceError(AppError):
    """Raised when a downstream service returns an error."""

    DEFAULT_MESSAGE = "External service returned an error."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.EXTERNAL_SERVICE_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class TimeoutError(AppError):
    """Raised when an operation exceeds the allotted time budget."""

    DEFAULT_MESSAGE = "Operation timed out."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.TIMEOUT_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class IOErrorApp(AppError):
    """Raised when file system or IO interactions fail."""

    DEFAULT_MESSAGE = "Input/output operation failed."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.IO_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


class UnknownError(AppError):
    """Raised when an unexpected or unmapped error occurs."""

    DEFAULT_MESSAGE = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        code = ErrorCode.UNKNOWN_ERROR
        super().__init__(
            code=code.code,
            message=message or self.DEFAULT_MESSAGE,
            exit_code=code.exit_code,
            severity=code.severity,
            context=context,
        )


__all__ = [
    "AppError",
    "ConfigError",
    "DBConnectionError",
    "DBMigrationError",
    "DBOperationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "ExternalServiceError",
    "TimeoutError",
    "IOErrorApp",
    "UnknownError",
]
