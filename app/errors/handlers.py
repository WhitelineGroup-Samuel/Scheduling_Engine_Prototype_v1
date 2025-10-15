"""
===============================================================================
File: app/errors/handlers.py
Purpose
-------
Normalize arbitrary exceptions to our `AppError` types, log them with structured
context (trace_id, code, severity), and return deterministic CLI/process exit
codes. Used by both CLI commands and the top-level `run.py` entrypoint.

Public API (Codex must implement)
---------------------------------
- def map_exception(err: BaseException) -> "AppError":
    - Map vendor exceptions to domain errors (see Phase F Step 14 table). Default:
      wrap in UnknownError(message=str(err), context={"type": err.__class__.__name__}).
    - Prefer direct type checks against SQLAlchemy exceptions if available:
      OperationalError -> DBConnectionError
      ProgrammingError -> DBOperationError
      IntegrityError   -> ConflictError
    - Import defensively:
        try:
            from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError
        except Exception:
            OperationalError = ProgrammingError = IntegrityError = ()  # fallback no-ops

- def handle_cli_error(err: BaseException, logger) -> int:
    Normalize (via map_exception unless err is already AppError),
    log exactly ONE structured line at appropriate level, then
    return `app_err.exit_code`. Use exc_info=True for CRITICAL/Unknown only.

- def wrap_cli_main(func):
    - Decorator for Typer/Click command entrypoints:
      try: return func(...)
      except BaseException as err:
          code = handle_cli_error(err, logger)
          raise SystemExit(code)
    - Use `functools.wraps(func)` when implementing the decorator to preserve CLI help/metadata.

- def level_for(severity: str) -> int
- def exc_info_for(app_err: "AppError") -> bool

Logging levels mapping
----------------------
- Map severity to stdlib logging levels (note: Python uses WARNING not WARN):
  "INFO" -> logging.INFO
  "WARN" -> logging.WARNING
  "ERROR" -> logging.ERROR
  "CRITICAL" -> logging.CRITICAL

Logging contract
----------------
- One line per handled exception; JSON vs human selected by logging config.
- Include extras: code, exit_code, severity, and safe `context` keys.
- `trace_id` is injected by logging filters (Step 13).
- Emit exactly ONE log record per handled error with:
  logger.log(level_for(severity), message,
             extra={"code": app_err.code,
                    "exit_code": app_err.exit_code,
                    "severity": app_err.severity,
                    "context": (app_err.context or {})})
- For CRITICAL/Unknown only: pass `exc_info=True`; otherwise `exc_info=False`.
- Do not duplicate logs across wrappers; `handle_cli_error` is the single place that logs.

Integration with run.py (Phase H Step 16)
-----------------------------------------
- `run.py` wraps its `main()` with a try/except and calls `handle_cli_error(...)`
  on failure, then exits with the returned code.
- Exit codes align with ErrorCode catalog (config=78, db=65, timeout=75, unknown=1).

Safety
------
- Never include secrets in messages or context (DB passwords, tokens).
- Prefer `exc_info=False` for expected errors (Validation/Conflict/NotFound).
- Do not intercept `SystemExit` or `KeyboardInterrupt` in `map_exception` or
  `handle_cli_error`; re-raise them immediately.
- `repr(AppError)` and messages must not include secrets (DB URLs, tokens). If needed, redact with "***".
===============================================================================
"""

from __future__ import annotations

import importlib
import json
import logging
from collections.abc import Callable, Mapping
from functools import wraps
from types import ModuleType
from typing import TYPE_CHECKING, Any

from .exceptions import (
    AppError,
    ConflictError,
    DBConnectionError,
    DBMigrationError,
    DBOperationError,
    ExternalServiceError,
    IOErrorApp,
    UnknownError,
    ValidationError,
)
from .exceptions import TimeoutError as DomainTimeoutError

# --- Pydantic (v2) ---
PydanticCoreValidationError: type[BaseException] | None = None
try:
    from pydantic_core import ValidationError as _PydanticCoreValidationError

    PydanticCoreValidationError = _PydanticCoreValidationError
except Exception:
    pass

# --- Pydantic (v1) ---
PydanticV1ValidationError: type[BaseException] | None = None
try:
    from pydantic import ValidationError as _PydanticV1ValidationError

    PydanticV1ValidationError = _PydanticV1ValidationError
except Exception:
    pass

# --- psycopg module (v3) ---
psycopg: ModuleType | None = None
try:
    import psycopg as _psycopg

    psycopg = _psycopg
except Exception:
    pass

# --- Alembic exceptions ---
AlembicCommandError: type[BaseException] | None = None
try:
    from alembic.util import CommandError as _AlembicCommandError

    AlembicCommandError = _AlembicCommandError
except Exception:
    pass

AlembicRevisionError: type[BaseException] | None = None
try:
    from alembic.script.revision import RevisionError as _AlembicRevisionError

    AlembicRevisionError = _AlembicRevisionError
except Exception:
    pass


if TYPE_CHECKING:  # pragma: no cover - optional dependency guard
    from sqlalchemy.exc import IntegrityError as SAIntegrityError
    from sqlalchemy.exc import OperationalError as SAOperationalError
    from sqlalchemy.exc import ProgrammingError as SAProgrammingError
else:  # pragma: no cover - guard optional dependency import failures
    try:
        from sqlalchemy.exc import IntegrityError as SAIntegrityError
        from sqlalchemy.exc import OperationalError as SAOperationalError
        from sqlalchemy.exc import ProgrammingError as SAProgrammingError
    except Exception:  # noqa: BLE001 - optional dependency missing
        SAIntegrityError = SAOperationalError = SAProgrammingError = BaseException  # type: ignore[assignment]


LoggerLike = logging.Logger


def level_for(severity: str) -> int:
    """Return the stdlib logging level for a given severity string."""

    mapping: Mapping[str, int] = {
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return mapping.get(severity.upper(), logging.ERROR)


def exc_info_for(app_err: AppError) -> bool:
    """Determine whether traceback details should be logged for the error."""

    return app_err.severity == "CRITICAL"


def map_exception(err: BaseException) -> AppError:
    """Translate any exception into a structured :class:`AppError`."""

    if isinstance(err, SystemExit | KeyboardInterrupt):
        raise err

    if isinstance(err, AppError):
        return err

    if isinstance(err, SAOperationalError):
        return DBConnectionError(context={"type": err.__class__.__name__})

    if isinstance(err, SAProgrammingError):
        return DBOperationError(context={"type": err.__class__.__name__})

    if isinstance(err, SAIntegrityError):
        return ConflictError(context={"type": err.__class__.__name__})

    # --- psycopg v3 mapping: InvalidCatalogName => DB connection error ---
    try:  # optional dependency; avoid hard import if missing
        pg_errors = importlib.import_module("psycopg.errors")
        InvalidCatalogName = getattr(pg_errors, "InvalidCatalogName", None)
    except Exception:  # psycopg not installed or import error
        InvalidCatalogName = None

    if InvalidCatalogName is not None and isinstance(err, InvalidCatalogName):
        return DBConnectionError(context={"type": err.__class__.__name__})

    # --- Pydantic validation (v2 and v1) ---
    if PydanticCoreValidationError is not None and isinstance(err, PydanticCoreValidationError):
        return ValidationError(message="Invalid data.", context={"type": err.__class__.__name__})
    if PydanticV1ValidationError is not None and isinstance(err, PydanticV1ValidationError):
        return ValidationError(message="Invalid data.", context={"type": err.__class__.__name__})

    # --- JSON decode errors (JSONB payloads, config files, etc.) ---
    if isinstance(err, json.JSONDecodeError):
        return ValidationError(
            message="Invalid JSON payload.",
            context={
                "type": err.__class__.__name__,
                "pos": err.pos,
                "lineno": err.lineno,
                "colno": err.colno,
            },
        )

    # --- psycopg v3 operational classes (transport/auth/socket) ---
    if psycopg is not None and isinstance(err, psycopg.OperationalError | psycopg.InterfaceError):
        return DBConnectionError(context={"type": err.__class__.__name__})

    # --- Alembic migration errors ---
    if (AlembicCommandError is not None and isinstance(err, AlembicCommandError)) or (
        AlembicRevisionError is not None and isinstance(err, AlembicRevisionError)
    ):
        return DBMigrationError(context={"type": err.__class__.__name__})

    if isinstance(err, ValueError):
        message = str(err) or None
        context = {"type": err.__class__.__name__}
        if message:
            context["detail"] = message
        return ValidationError(message=message, context=context)

    if isinstance(err, TimeoutError):
        message = str(err) or None
        return DomainTimeoutError(message=message, context={"type": err.__class__.__name__})

    if isinstance(err, ConnectionError):
        message = str(err) or None
        return ExternalServiceError(message=message, context={"type": err.__class__.__name__})

    if isinstance(err, OSError):
        message = str(err) or None
        return IOErrorApp(message=message, context={"type": err.__class__.__name__})

    if isinstance(err, RuntimeError):
        message = str(err) or None
        return DBMigrationError(message=message, context={"type": err.__class__.__name__})

    return UnknownError(
        message=str(err),
        context={"type": err.__class__.__name__},
    )


def handle_cli_error(err: BaseException, logger: LoggerLike) -> int:
    """Normalize, log, and return the exit code for a CLI error."""

    if isinstance(err, SystemExit | KeyboardInterrupt):
        raise err

    app_err = map_exception(err)
    logger.log(
        level_for(app_err.severity),
        app_err.message,
        extra={
            "code": app_err.code,
            "exit_code": app_err.exit_code,
            "severity": app_err.severity,
            "context": app_err.context or {},
        },
        exc_info=exc_info_for(app_err),
    )
    return app_err.exit_code


def wrap_cli_main[T](func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that standardizes CLI error handling for entrypoints."""

    logger = logging.getLogger(func.__module__)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as err:  # noqa: BLE001 - must capture all exceptions
            code = handle_cli_error(err, logger)
            raise SystemExit(code) from err

    return wrapper


__all__ = [
    "map_exception",
    "handle_cli_error",
    "wrap_cli_main",
    "level_for",
    "exc_info_for",
]
