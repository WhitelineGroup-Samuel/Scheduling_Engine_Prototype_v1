"""Pytest configuration ensuring deterministic test environment setup."""

from __future__ import annotations

import os
from collections.abc import Iterable

import pytest
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)
os.environ.setdefault("APP_ENV", "test")

# Hard safety: ensure we only ever run against the test database
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL is not set. tests/conftest.py expects .env.test to define it.")
if "scheduling_test" not in DB_URL:
    raise RuntimeError(f"Refusing to run tests on non-test DB URL: {DB_URL}")

pytest_plugins = [
    "tests.fixtures.db",
    "tests.fixtures.time",
    "tests.fixtures.calendar",
]


def _should_skip_all() -> bool:
    """Return ``True`` when the environment requests skipping all tests."""

    flag = os.getenv("SKIP_ALL_TESTS")
    if flag is None:
        return False
    return flag.lower() in {"1", "true", "yes"}


def pytest_configure(config: pytest.Config) -> None:
    """Register project markers and optionally skip the entire test run."""

    config.addinivalue_line("markers", "unit: marks tests that exercise isolated units")
    config.addinivalue_line("markers", "smoke: marks lightweight smoke tests verifying bootstrapping")
    config.addinivalue_line("markers", "integration: marks tests that rely on external systems")

    if _should_skip_all():
        pytest.skip("SKIP_ALL_TESTS is set; skipping entire test run", allow_module_level=True)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Label collected tests with unit/smoke/integration markers based on path."""

    for item in items:
        path = str(item.path)
        markers: Iterable[pytest.MarkDecorator]
        if "/tests/unit/" in path or "/tests/utils/" in path:
            markers = (pytest.mark.unit,)
        elif "/tests/integration/" in path:
            markers = (pytest.mark.integration,)
        elif path.endswith("tests/test_smoke.py"):
            markers = (pytest.mark.smoke,)
        else:
            markers = ()
        for marker in markers:
            item.add_marker(marker)
