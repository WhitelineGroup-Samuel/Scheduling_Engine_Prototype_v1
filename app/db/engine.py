"""
===============================================================================
File: app/db/engine.py
Purpose
-------
Create and manage the canonical SQLAlchemy **Engine** for Postgres.
Enforce safe defaults (timeouts, pooling, pre-ping, redaction) and provide
helpers for building sanitized URLs for logs.
===============================================================================
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url

__all__ = [
    "create_engine_from_settings",
    "sanitize_url_for_log",
    "engine_diagnostics",
]


def sanitize_url_for_log(url: str) -> str:
    """Return a redacted representation of a Postgres connection URL.

    Parameters
    ----------
    url:
        Raw connection string that may include credentials.

    Returns
    -------
    str
        A safe URL representation where the username and password (if
        present) are replaced with ``***`` so secrets never appear in logs.
    """

    try:
        sa_url = make_url(url)
    except Exception:
        return "***"
    username = "***" if sa_url.username else None
    password = "***" if sa_url.password else None
    redacted = sa_url.set(username=username, password=password)
    return str(redacted)


def _build_connect_args(
    *,
    settings: Any,
    role: str,
    statement_timeout_ms: int | None,
    idle_in_tx_timeout_ms: int | None,
    connect_timeout_s: int | None,
) -> dict[str, Any]:
    """Construct psycopg (v3) / SQLAlchemy ``connect_args`` with safe timeouts for every connection."""
    connect_args: dict[str, Any] = {
        "application_name": f"{settings.APP_NAME}:{role}",
    }
    if connect_timeout_s is not None:
        connect_args["connect_timeout"] = connect_timeout_s

    option_parts: list[str] = []
    if statement_timeout_ms is not None:
        option_parts.append(f"-c statement_timeout={statement_timeout_ms}")
    if idle_in_tx_timeout_ms is not None:
        option_parts.append(f"-c idle_in_transaction_session_timeout={idle_in_tx_timeout_ms}")
    if option_parts:
        connect_args["options"] = " ".join(option_parts)
    return connect_args


def create_engine_from_settings(
    settings: Any,
    *,
    echo_sql: bool | None = None,
    role: str = "app",
    statement_timeout_ms: int | None = 5000,
    idle_in_tx_timeout_ms: int | None = 120000,
    connect_timeout_s: int | None = 5,
) -> Engine:
    """Build and return a configured SQLAlchemy engine for Postgres.

    Parameters
    ----------
    settings:
        Pydantic settings instance exposing ``effective_database_url``,
        environment flags, and app metadata.
    echo_sql:
        Optional override for SQLAlchemy's ``echo`` flag. When ``None`` the
        value is derived from ``APP_ENV`` and ``LOG_LEVEL``.
    role:
        Identifier appended to ``application_name`` for easier attribution in
        Postgres activity views.
    statement_timeout_ms / idle_in_tx_timeout_ms / connect_timeout_s:
        Driver-level guards applied to every connection to prevent runaway
        queries and stalled transactions.

    Returns
    -------
    Engine
        A fully configured SQLAlchemy engine that has not established any
        connections yet.
    """

    effective_url = settings.effective_database_url
    echo = echo_sql if echo_sql is not None else settings.APP_ENV == "dev" and settings.LOG_LEVEL == "DEBUG"

    engine = create_engine(
        effective_url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=10,
        pool_recycle=1800,
        connect_args=_build_connect_args(
            settings=settings,
            role=role,
            statement_timeout_ms=statement_timeout_ms,
            idle_in_tx_timeout_ms=idle_in_tx_timeout_ms,
            connect_timeout_s=connect_timeout_s,
        ),
    )
    return engine


def engine_diagnostics(engine: Engine) -> dict[str, Any]:
    """Return non-connecting diagnostic information about an engine.

    Parameters
    ----------
    engine:
        Engine instance to introspect.

    Returns
    -------
    dict[str, Any]
        Lightweight metadata describing pool sizing, echo flag, and dialect
        without requiring an actual database connection.
    """

    pool = engine.pool
    pool_size_value: Any
    size_attr = getattr(pool, "size", None)
    if callable(size_attr):
        try:
            pool_size_value = size_attr()
        except TypeError:
            pool_size_value = None
    else:
        pool_size_value = size_attr
    max_overflow_value = getattr(pool, "max_overflow", None)
    if callable(max_overflow_value):
        try:
            max_overflow_value = max_overflow_value()
        except TypeError:
            max_overflow_value = None
    if max_overflow_value is None:
        max_overflow_value = getattr(pool, "_max_overflow", None)

    return {
        "pool_size": pool_size_value,
        "max_overflow": max_overflow_value,
        "echo": bool(engine.echo),
        "dialect": f"{engine.dialect.name}+{engine.dialect.driver}",
    }
