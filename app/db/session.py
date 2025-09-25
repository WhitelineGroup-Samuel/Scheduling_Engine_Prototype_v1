"""
===============================================================================
File: app/db/session.py
Purpose
-------
Provide a robust **Session** factory and utilities for transactional work.
===============================================================================
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Optional

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker

__all__ = [
    "SessionLocal",
    "create_session_factory",
    "get_session",
    "session_scope",
    "begin_nested_for_tests",
]

SessionLocal: Optional[sessionmaker[Session]] = None


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a configured ``sessionmaker`` bound to ``engine``.

    Parameters
    ----------
    engine:
        SQLAlchemy engine that will supply connections for new sessions.

    Returns
    -------
    sessionmaker[Session]
        Factory that creates ``Session`` instances with safe defaults
        (no autoflush, objects remain usable post-commit).
    """

    factory = sessionmaker[Session](
        bind=engine, expire_on_commit=False, autoflush=False
    )
    return factory


@contextmanager
def get_session(
    session_factory: Optional[sessionmaker[Session]] = None,
) -> Iterator[Session]:
    """Yield a session scoped to the context, committing or rolling back.

    Parameters
    ----------
    session_factory:
        Optional factory override. When omitted the module-level
        ``SessionLocal`` must be initialised by the application bootstrapper.

    Yields
    ------
    Session
        Managed session that commits on success, rolls back on errors, and is
        always closed at the end of the ``with`` block.
    """

    factory = session_factory or SessionLocal
    if factory is None:
        raise RuntimeError("Session factory is not configured")

    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    finally:
        session.close()


session_scope = get_session


def begin_nested_for_tests(session: Session) -> SessionTransaction:
    """Start and return a nested transaction for use in tests.

    Parameters
    ----------
    session:
        Session under which the nested transaction (SAVEPOINT) should start.

    Returns
    -------
    SessionTransaction
        Handle to the SAVEPOINT transaction that tests can roll back between
        assertions.
    """

    return session.begin_nested()
