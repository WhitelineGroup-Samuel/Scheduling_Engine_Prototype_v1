"""Tests for mapping low-level exceptions to :class:`AppError` subclasses."""

from __future__ import annotations

import asyncio
import importlib

import pytest
from pydantic import BaseModel, ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

from app.errors.codes import ErrorCode
from app.errors.exceptions import (
    AppError,
    ConflictError,
    DBConnectionError,
    DBOperationError,
    IOErrorApp,
    TimeoutError,
    UnknownError,
    ValidationError,
)
from app.errors.handlers import map_exception

pytestmark = pytest.mark.unit


def _assert_error(
    mapped: AppError, expected_type: type[AppError], code: ErrorCode
) -> None:
    """Assert core attributes shared by :class:`AppError` instances."""

    assert isinstance(mapped, expected_type)
    assert mapped.code == code.code
    assert mapped.exit_code == code.exit_code
    assert mapped.severity == code.severity
    assert mapped.message
    if mapped.context is not None:
        assert mapped.context.get("type")


def test_map_operational_error_to_db_connection_error() -> None:
    """Operational errors from SQLAlchemy map to database connection issues."""

    err = OperationalError("SELECT 1", {}, Exception("db down"))

    mapped = map_exception(err)

    _assert_error(mapped, DBConnectionError, ErrorCode.DB_CONNECTION_ERROR)
    assert mapped.context == {"type": "OperationalError"}


def test_map_integrity_error_to_conflict_error() -> None:
    """Integrity errors should surface as conflict errors."""

    err = IntegrityError("INSERT", {}, Exception("duplicate key value"))

    mapped = map_exception(err)

    _assert_error(mapped, ConflictError, ErrorCode.CONFLICT_ERROR)
    assert mapped.context == {"type": "IntegrityError"}


def test_map_programming_error_to_db_operation_error() -> None:
    """Programming errors translate to database operation failures."""

    err = ProgrammingError("UPDATE", {}, Exception("syntax error"))

    mapped = map_exception(err)

    _assert_error(mapped, DBOperationError, ErrorCode.DB_OPERATION_ERROR)
    assert mapped.context == {"type": "ProgrammingError"}


def test_map_psycopg_invalid_catalog_to_db_connection_error() -> None:
    """psycopg invalid catalog errors should map to connection failures."""

    pytest.importorskip("psycopg", reason="psycopg not installed")
    errors_module = importlib.import_module("psycopg.errors")
    invalid_catalog = getattr(errors_module, "InvalidCatalogName")
    err = invalid_catalog("database does not exist")

    mapped = map_exception(err)

    _assert_error(mapped, DBConnectionError, ErrorCode.DB_CONNECTION_ERROR)
    assert mapped.context == {"type": "InvalidCatalogName"}


def test_map_pydantic_validation_error_to_validation_error() -> None:
    """Pydantic validation errors become domain validation errors."""

    class DemoModel(BaseModel):
        value: int

    with pytest.raises(PydanticValidationError) as excinfo:
        DemoModel(value="not-an-int")

    mapped = map_exception(excinfo.value)

    _assert_error(mapped, ValidationError, ErrorCode.VALIDATION_ERROR)
    assert mapped.context and mapped.context.get("type") == "ValidationError"


@pytest.mark.parametrize(
    "os_error", [FileNotFoundError("missing"), PermissionError("denied")]
)
def test_map_os_errors_to_io_error(os_error: OSError) -> None:
    """Filesystem related errors are normalised to :class:`IOErrorApp`."""

    mapped = map_exception(os_error)

    _assert_error(mapped, IOErrorApp, ErrorCode.IO_ERROR)
    assert mapped.context == {"type": os_error.__class__.__name__}


def test_map_timeout_to_timeout_error() -> None:
    """Timeouts should map directly to the domain timeout error."""

    mapped = map_exception(asyncio.TimeoutError())

    _assert_error(mapped, TimeoutError, ErrorCode.TIMEOUT_ERROR)
    assert mapped.context == {"type": "TimeoutError"}


def test_map_unknown_to_unknown_error() -> None:
    """Fallback to :class:`UnknownError` with safe context for unexpected errors."""

    mapped = map_exception(Exception("boom"))

    _assert_error(mapped, UnknownError, ErrorCode.UNKNOWN_ERROR)
    assert mapped.context == {"type": "Exception"}
