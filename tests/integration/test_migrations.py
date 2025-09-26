"""Integration tests verifying Alembic migrations apply cleanly."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_alembic_upgrade_head_subprocess(engine: Engine) -> None:
    """Run ``alembic upgrade head`` and confirm the version table is populated."""

    pytest.importorskip("alembic", reason="alembic not installed")
    command = [sys.executable, "-m", "alembic", "upgrade", "head"]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        pytest.fail(
            "alembic upgrade head failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    inspector = inspect(engine)
    assert inspector.has_table("alembic_version"), "alembic_version table missing"
    with engine.connect() as connection:
        version = connection.execute(text("select version_num from alembic_version"))
        version_num = version.scalar_one()
    assert isinstance(version_num, str)
    assert version_num.strip()
