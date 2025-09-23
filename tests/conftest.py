"""
Test bootstrap:
- Always load .env.test for pytest runs (if present).
- Force APP_ENV=test so the app selects the test DB and test-safe settings.
- This happens before any test imports user code, so config is consistent.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def pytest_configure(config: Any) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    env_test = repo_root / ".env.test"

    # Load .env.test if it exists (devs keep it locally; secrets stay out of git)
    if env_test.exists():
        # override=True so tests don't accidentally inherit values from your dev .env
        load_dotenv(env_test, override=True)

    # Ensure the app knows we're in test mode even if .env.test omitted APP_ENV
    os.environ.setdefault("APP_ENV", "test")
