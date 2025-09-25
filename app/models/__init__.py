"""app.models package
=====================

Container package for SQLAlchemy ORM models. Modules are imported lazily to
avoid side effects during package import while still giving Alembic visibility
via :func:`app.db.base.import_all_models`.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["Organisation"]


def __getattr__(name: str) -> Any:
    """Provide lazy access to ORM classes without eager imports."""

    if name == "Organisation":
        module = import_module("app.models.core")
        return getattr(module, name)
    raise AttributeError(f"module 'app.models' has no attribute {name!r}")
