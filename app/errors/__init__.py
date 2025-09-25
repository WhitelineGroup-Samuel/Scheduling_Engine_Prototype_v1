"""
===============================================================================
Package: app.errors
Purpose
-------
Centralize the Scheduling Engine's error taxonomy and handling utilities.

What Codex must expose from this package
----------------------------------------
- Re-export core symbols so callers can do:
    from app.errors import (
        AppError,
        ConfigError, DBConnectionError, DBMigrationError, DBOperationError,
        ValidationError, NotFoundError, ConflictError,
        ExternalServiceError, TimeoutError, IOErrorApp, UnknownError,
        ErrorCode,
        map_exception, handle_cli_error, wrap_cli_main,
    )

Implementation guidance
-----------------------
- Import order must avoid import cycles:
    * .codes defines ErrorCode catalog (no imports from .exceptions/.handlers).
    * .exceptions defines AppError + subclasses (import ErrorCode only).
    * .handlers defines mapping + CLI handlers (import both codes and exceptions).
- Keep package import side-effect free (no logging, no I/O).

Non-goals
---------
- No HTTP layer here; error→HTTP mapping may live in a future API package.
===============================================================================
"""

from .codes import ErrorCode
from .exceptions import (
    AppError,
    ConfigError,
    ConflictError,
    DBConnectionError,
    DBMigrationError,
    DBOperationError,
    ExternalServiceError,
    IOErrorApp,
    NotFoundError,
    TimeoutError,
    UnknownError,
    ValidationError,
)
from .handlers import handle_cli_error, map_exception, wrap_cli_main

__all__: list[str] = [
    "ErrorCode",
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
    "map_exception",
    "handle_cli_error",
    "wrap_cli_main",
]
