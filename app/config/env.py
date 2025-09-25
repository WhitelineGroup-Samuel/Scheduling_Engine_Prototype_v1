"""
===============================================================================
File: app/config/env.py
Purpose
-------
Consistently load environment variables from `.env` files in development/test
only, keeping production dependent on the process environment.
===============================================================================
"""

from __future__ import annotations

import os

from .constants import ENV_DEV, ENV_PROD, ENV_TEST
from .paths import REPO_ROOT

_TRUTHY_VALUES: set[str] = {"1", "true", "yes", "on"}
_FALSY_VALUES: set[str] = {"0", "false", "no", "off"}


def load_dotenv_for_env(app_env: str, *, test_mode: bool = False) -> None:
    """Load environment variables from a `.env` file when appropriate."""

    if app_env == ENV_PROD:
        return
    if app_env not in {ENV_DEV, ENV_TEST}:
        return

    dotenv_name = ".env.test" if test_mode else ".env"
    dotenv_path = REPO_ROOT / dotenv_name
    if not dotenv_path.exists():
        return

    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv(dotenv_path, override=False)


def _get_env(key: str) -> str | None:
    """Helper to fetch an environment variable."""

    value = os.getenv(key)
    if value is None:
        return None
    return value.strip()


def env_bool(key: str, default: bool = False) -> bool:
    """Return a boolean environment variable using relaxed parsing."""

    value = _get_env(key)
    if value is None:
        return default
    lowered = value.lower()
    if lowered in _TRUTHY_VALUES:
        return True
    if lowered in _FALSY_VALUES:
        return False
    return default


def env_int(key: str, default: int | None = None) -> int | None:
    """Return an integer environment variable if possible."""

    value = _get_env(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def env_str(key: str, default: str | None = None) -> str | None:
    """Return a string environment variable or the default."""

    value = _get_env(key)
    if value is None:
        return default
    return value


__all__ = ["load_dotenv_for_env", "env_bool", "env_int", "env_str"]
