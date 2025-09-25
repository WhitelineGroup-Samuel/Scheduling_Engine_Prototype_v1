"""
===============================================================================
Package: app.db
Purpose:
  Database access layer integration point. Re-exports engine/session helpers.
===============================================================================
"""

from __future__ import annotations

from .base import Base, import_all_models, metadata
from .engine import create_engine_from_settings, sanitize_url_for_log
from .session import create_session_factory, get_session, session_scope

__all__ = [
    "create_engine_from_settings",
    "sanitize_url_for_log",
    "create_session_factory",
    "get_session",
    "session_scope",
    "Base",
    "metadata",
    "import_all_models",
]
