"""Database fixtures providing transactional isolation for integration tests."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker

from app.config.constants import DB_SCHEME
from app.config.settings import get_settings
from app.db.engine import create_engine_from_settings


def _normalise_drivername(url: str) -> str:
    """Return a connection URL that explicitly uses the psycopg driver."""

    parsed = make_url(url)
    if parsed.drivername == DB_SCHEME:
        return url
    normalised = parsed.set(drivername=DB_SCHEME)
    return str(normalised)


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """Return a SQLAlchemy engine bound to the test database."""

    settings = get_settings()
    app_env = os.getenv("APP_ENV") or settings.APP_ENV
    if app_env != "test":
        raise RuntimeError("Integration tests must run with APP_ENV=test")

    effective_url = _normalise_drivername(settings.effective_database_url)
    if effective_url == settings.effective_database_url:
        sa_engine = create_engine_from_settings(settings, echo_sql=False, role="pytest")
    else:
        sa_engine = create_engine(
            effective_url,
            echo=False,
            pool_pre_ping=True,
        )
    try:
        yield sa_engine
    finally:
        sa_engine.dispose()


@pytest.fixture(scope="function")
def db_connection(engine: Engine) -> Iterator[Connection]:
    """Yield a raw SQLAlchemy connection for read-only queries."""

    connection = engine.connect()
    try:
        connection.execute(text("select 1"))
        yield connection
    finally:
        connection.close()


@pytest.fixture(scope="session")
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a configured session factory bound to the shared engine."""

    factory = sessionmaker[Session](
        bind=engine, expire_on_commit=False, autoflush=False
    )
    return factory


@pytest.fixture(scope="function")
def db_session(
    session_factory: sessionmaker[Session],
    engine: Engine,
) -> Iterator[Session]:
    """Provide a transactional session that rolls back after each test."""

    connection = engine.connect()
    transaction = connection.begin()
    session = session_factory(bind=connection)
    session.execute(text("SET LOCAL TIME ZONE 'UTC'"))
    session.begin_nested()

    def _restart_savepoint(sess: Session, transaction_: SessionTransaction) -> None:
        """Re-establish nested SAVEPOINTs after commits within tests."""

        parent = getattr(transaction_, "parent", None) or getattr(
            transaction_, "_parent", None
        )
        if (
            transaction_.nested
            and parent is not None
            and not getattr(parent, "nested", False)
        ):
            sess.begin_nested()

    event.listen(session, "after_transaction_end", _restart_savepoint)

    try:
        yield session
    finally:
        event.remove(session, "after_transaction_end", _restart_savepoint)
        try:
            session.close()
        finally:
            if transaction.is_active:
                transaction.rollback()
            connection.close()


@pytest.fixture(scope="session")
def migrated_db(engine: Engine) -> Iterator[None]:
    """Apply Alembic migrations to the test database once per test session."""

    pytest.importorskip("alembic", reason="alembic not installed")
    import subprocess
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    command = [sys.executable, "-m", "alembic", "upgrade", "head"]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "alembic upgrade head failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    try:
        yield
    finally:
        engine.dispose()
