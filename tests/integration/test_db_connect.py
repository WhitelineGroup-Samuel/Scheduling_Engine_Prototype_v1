"""Connectivity smoke tests for the integration database."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

pytestmark = pytest.mark.integration


def test_engine_can_connect(engine: Engine) -> None:
    """Ensure the SQLAlchemy engine can reach the ``scheduling_test`` database."""

    assert os.getenv("APP_ENV") == "test"
    with engine.connect() as connection:
        database_name = connection.execute(text("select current_database()"))
        version_info = connection.execute(text("select version()"))
        db_name = database_name.scalar_one()
        version = version_info.scalar_one()
    assert db_name == "scheduling_test"
    assert isinstance(version, str)
    assert version.strip()


def test_readonly_query_succeeds(db_connection: Connection) -> None:
    """Execute a read-only query to confirm the connection is usable."""

    current_time = db_connection.execute(text("select now() at time zone 'utc'"))
    value = current_time.scalar_one()
    assert value is not None
