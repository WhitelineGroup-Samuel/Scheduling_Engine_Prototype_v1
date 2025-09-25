"""
===============================================================================
File: app/config/constants.py
Purpose:
  Central definitions for common constants/enums to avoid magic strings.
===============================================================================
"""

from __future__ import annotations

ENV_DEV: str = "dev"
ENV_TEST: str = "test"
ENV_PROD: str = "prod"

DEFAULT_TZ: str = "Australia/Melbourne"
DB_SCHEME: str = "postgresql+psycopg"

__all__ = ["ENV_DEV", "ENV_TEST", "ENV_PROD", "DEFAULT_TZ", "DB_SCHEME"]
