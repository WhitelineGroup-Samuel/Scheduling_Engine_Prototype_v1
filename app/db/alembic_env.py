"""
===============================================================================
File: app/db/alembic_env.py
Purpose:
  Alembic environment script (project-specific) for running migrations online.
===============================================================================
"""

from __future__ import annotations

import pathlib
import sys
from typing import Final

from alembic import context
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

REPO_ROOT: Final[pathlib.Path] = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config.settings import get_settings  # noqa: E402
from app.db.base import Base, import_all_models  # noqa: E402

__all__ = ["run_migrations_online", "run_migrations_offline", "target_metadata"]

target_metadata = Base.metadata


def _configure_engine(url: str) -> Engine:
    """Return a SQLAlchemy engine configured for Alembic migrations."""

    return create_engine(url, pool_pre_ping=True, future=True)


def run_migrations_online() -> None:
    """Run Alembic migrations in online mode against the configured database."""

    settings = get_settings()
    database_url = settings.effective_database_url
    engine = _configure_engine(database_url)

    with engine.connect() as connection:
        import_all_models()
        context.configure(connection=connection, target_metadata=target_metadata)
        connection.execute(text("SET lock_timeout = '5s'"))
        connection.execute(text("SET statement_timeout = '60s'"))
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


def run_migrations_offline() -> None:
    """Offline migrations are not supported for this project."""

    raise NotImplementedError(
        "Offline migrations are not supported; use online mode only."
    )
