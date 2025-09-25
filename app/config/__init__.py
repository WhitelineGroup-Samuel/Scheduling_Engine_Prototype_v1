"""
===============================================================================
Package: app.config
Purpose:
  Centralized configuration access. Exposes get_settings() as the canonical
  way to retrieve app settings across the codebase.
===============================================================================
"""

from __future__ import annotations

from .settings import get_settings

__all__ = ["get_settings"]
