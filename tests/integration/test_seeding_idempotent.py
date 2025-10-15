# tests/integration/test_seeding_idempotent.py
from __future__ import annotations

import os
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, text

# Always force TEST env for this module
os.environ.setdefault("APP_ENV", "test")

SEED_CMD = [sys.executable, "-m", "app.cli", "seed-data"]
ALEMBIC_CMD = [sys.executable, "-m", "alembic", "-x", "env=test"]


def _truncate_all(conn) -> None:
    # Truncate all seeded tables, restart identity, cascade to dependents.
    conn.execute(
        text(
            """
        TRUNCATE
          users,
          organisations,
          user_permissions,
          competitions,
          seasons,
          season_days,
          venues,
          courts,
          ages,
          grades,
          teams,
          rounds,
          round_settings
        RESTART IDENTITY CASCADE
        """
        )
    )


@pytest.fixture(scope="module", autouse=True)
def ensure_head():
    """Upgrade TEST DB to head once for this module."""
    proc = subprocess.run(
        ALEMBIC_CMD + ["upgrade", "head"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "APP_ENV": "test"},
    )
    assert proc.returncode == 0, f"Alembic upgrade failed\n{proc.stdout}\n{proc.stderr}"


def _run_seed(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        SEED_CMD + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "APP_ENV": "test"},
    )


def _engine():
    # Pull URL from your Settings module (preferred), otherwise fall back to env.
    try:
        from app.config.settings import get_settings

        s = get_settings()
        url = getattr(s, "effective_database_url", None) or os.environ["DATABASE_URL"]
    except Exception:
        url = os.environ["DATABASE_URL"]
    return create_engine(url)


def _table_exists(conn, table_name: str) -> bool:
    q = text(
        """
        select exists (
            select 1
              from information_schema.tables
             where table_schema = 'public'
               and table_name = :t
        )
    """
    )
    return conn.execute(q, {"t": table_name}).scalar_one()


def _counts(conn, tables: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for t in tables:
        if _table_exists(conn, t):
            out[t] = conn.execute(text(f"select count(*) from {t}")).scalar_one()
        else:
            # Missing is okay; treat as 0 so assertions can still compare.
            out[t] = 0
    return out


@pytest.mark.integration
def test_seed_apply_is_idempotent():
    """
    1) Apply seed → capture counts
    2) Apply seed again → counts unchanged
    3) Known unique row (seeded user) keeps the same PK
    """
    engine = _engine()
    with engine.begin() as conn:
        # Before anything, capture a reference PK for the known seeded user (should exist after first apply)
        # We'll obtain it after first apply; initial value might be None.
        _truncate_all(conn)

    # First apply
    first = _run_seed([])
    assert first.returncode == 0, f"seed apply failed\n{first.stdout}\n{first.stderr}"
    assert "Seed completed. Changes committed." in first.stdout

    # Snapshot counts after first apply
    with engine.begin() as conn:
        tables = [
            "users",
            "organisations",
            "user_permissions",
            "competitions",
            "seasons",
            "season_days",
            "venues",
            "courts",
            "ages",
            "grades",
            "teams",
            "rounds",
            "round_settings",
            # "time_slots",  # Uncomment if/when your seed creates these
        ]
        first_counts = _counts(conn, tables)

        # Spot-check a stable row: the seeded user
        user_id_1 = conn.execute(text("select user_account_id from users where email = 'samuel@whitelinegroup.com.au'")).scalar_one_or_none()
        assert user_id_1 is not None, "Expected seeded user to exist after first apply"

    # Second apply
    second = _run_seed([])
    assert second.returncode == 0, f"second seed apply failed\n{second.stdout}\n{second.stderr}"
    assert "Seed Summary" in second.stdout  # You print a summary even on apply

    # Snapshot counts after second apply
    with engine.begin() as conn:
        second_counts = _counts(conn, tables)
        assert second_counts == first_counts, f"Counts changed across idempotent seed\nfirst={first_counts}\nsecond={second_counts}"

        user_id_2 = conn.execute(text("select user_account_id from users where email = 'samuel@whitelinegroup.com.au'")).scalar_one_or_none()
        assert user_id_2 == user_id_1, "Seed must not duplicate/replace the seeded user"

    with engine.begin() as conn:
        _truncate_all(conn)


@pytest.mark.integration
def test_seed_plan_does_not_mutate_counts():
    """
    --plan (your 'preview' mode) must not change counts.
    """
    engine = _engine()
    with engine.begin() as conn:
        _truncate_all(conn)
        tables = [
            "users",
            "organisations",
            "user_permissions",
            "competitions",
            "seasons",
            "season_days",
            "venues",
            "courts",
            "ages",
            "grades",
            "teams",
            "rounds",
            "round_settings",
        ]
        before = _counts(conn, tables)

    plan = _run_seed(["--plan"])
    assert plan.returncode == 0, f"seed --plan failed\n{plan.stdout}\n{plan.stderr}"
    assert "Dry run completed. No changes were written." in plan.stdout

    with engine.begin() as conn:
        after = _counts(conn, tables)

    assert after == before, "Preview/plan must not change persisted data"
