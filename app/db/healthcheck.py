"""
===============================================================================
File: app/db/healthcheck.py
Purpose
-------
Provide a fast, read-only Postgres healthcheck helper.
===============================================================================
"""

from __future__ import annotations

import re
import time
from collections.abc import Mapping
from typing import Any, Final

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.errors.exceptions import DBConnectionError

__all__ = ["ping"]

_VERSION_REGEX: Final[re.Pattern[str]] = re.compile(r"(\d+(?:\.\d+)*)")

try:  # pragma: no cover - defensive import for SQLAlchemy errors
    from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
except Exception:  # pragma: no cover - fallback when SQLAlchemy internals change
    SQLAlchemyOperationalError = None  # type: ignore[assignment]

try:  # pragma: no cover - psycopg may be absent in pure unit tests
    from psycopg import errors as psycopg_errors
except Exception:  # pragma: no cover - fallback when psycopg isn't installed
    InvalidCatalogName = None  # type: ignore[assignment]
    PsycopgOperationalError = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    InvalidCatalogName = psycopg_errors.InvalidCatalogName
    PsycopgOperationalError = psycopg_errors.OperationalError

_OPERATIONAL_ERRORS = tuple(
    error
    for error in (
        SQLAlchemyOperationalError,
        PsycopgOperationalError,
        InvalidCatalogName,
    )
    if error is not None
)


def _elapsed_ms(start: float) -> float:
    """Return elapsed milliseconds since ``start`` (monotonic timestamp)."""

    return (time.monotonic() - start) * 1000.0


def _assert_within_timeout(
    start: float, timeout_seconds: float, context: Mapping[str, Any]
) -> None:
    """Raise :class:`DBConnectionError` if the allotted timeout has elapsed."""

    if (time.monotonic() - start) > timeout_seconds:
        raise DBConnectionError(
            message="Database healthcheck failed",
            context={**context, "timeout_s": timeout_seconds},
        )


def _build_context(
    database: str | None, timeout_seconds: float, driver: str | None
) -> dict[str, Any]:
    context: dict[str, Any] = {
        "database": database,
        "timeout_s": timeout_seconds,
        "op": "healthcheck.ping",
    }
    if driver:
        context["driver"] = driver
    return context


def ping(
    engine_or_session: Engine | Session, *, timeout_seconds: float = 5.0
) -> dict[str, Any]:
    """Perform a read-only healthcheck against Postgres.

    Parameters
    ----------
    engine_or_session:
        Either a SQLAlchemy ``Engine`` or an active ``Session``. When an
        engine is provided a new connection is opened and explicitly closed at
        the end of the check. Sessions reuse their existing connection.
    timeout_seconds:
        Overall time budget for the healthcheck. Exceeding the limit raises a
        :class:`DBConnectionError`.

    Returns
    -------
    dict[str, Any]
        Structured payload describing the target database, server version, and
        the elapsed time in milliseconds.

    Raises
    ------
    DBConnectionError
        When any of the read-only statements fail or the timeout is exceeded.
    """

    start = time.monotonic()
    database_name: str | None = None
    driver_name: str | None = None

    if isinstance(engine_or_session, Engine):
        connection = engine_or_session.connect()
        should_close = True
        driver_name = engine_or_session.dialect.driver
    else:
        connection = engine_or_session.connection()
        should_close = False
        bind = engine_or_session.get_bind()
        if bind is not None:
            driver_name = bind.dialect.driver

    context = _build_context(database_name, timeout_seconds, driver_name)
    server_version_full: str | None = None

    try:
        _assert_within_timeout(start, timeout_seconds, context)
        connection.execute(text("SELECT 1"))
        _assert_within_timeout(start, timeout_seconds, context)

        try:
            server_version_full_result = connection.execute(text("SHOW server_version"))
            server_version_full = str(server_version_full_result.scalar_one())
            server_version = server_version_full
        except _OPERATIONAL_ERRORS:
            version_row = connection.execute(text("SELECT version()"))
            server_version_full = str(version_row.scalar_one())
            match = _VERSION_REGEX.search(server_version_full)
            if not match:
                raise DBConnectionError(
                    message="Database healthcheck failed",
                    context=context,
                )
            server_version = match.group(1)

        _assert_within_timeout(start, timeout_seconds, context)

        database_result = connection.execute(text("SELECT current_database()"))
        database_name = str(database_result.scalar_one())
        context = _build_context(database_name, timeout_seconds, driver_name)
        _assert_within_timeout(start, timeout_seconds, context)

        result: dict[str, Any] = {
            "ok": True,
            "database": database_name,
            "server_version": server_version,
            "duration_ms": _elapsed_ms(start),
        }
        if server_version_full is not None:
            result["server_version_full"] = server_version_full
        return result
    except _OPERATIONAL_ERRORS as exc:
        raise DBConnectionError(
            message="Database healthcheck failed",
            context=_build_context(database_name, timeout_seconds, driver_name),
        ) from exc
    except Exception as exc:
        raise DBConnectionError(
            message="Database healthcheck failed",
            context=_build_context(database_name, timeout_seconds, driver_name),
        ) from exc
    finally:
        if should_close:
            connection.close()
