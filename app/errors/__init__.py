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

# Codex should implement the re-exports AFTER implementing codes/exceptions/handlers.
# from .codes import ErrorCode
# from .exceptions import (
#     AppError,
#     ConfigError, DBConnectionError, DBMigrationError, DBOperationError,
#     ValidationError, NotFoundError, ConflictError,
#     ExternalServiceError, TimeoutError, IOErrorApp, UnknownError,
# )
# from .handlers import map_exception, handle_cli_error, wrap_cli_main
