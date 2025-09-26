"""
===============================================================================
File: app/db/base.py
Purpose:
  Expose the canonical SQLAlchemy declarative base (`Base`) and metadata for the app.
===============================================================================
"""

from __future__ import annotations

import importlib
from typing import Final

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase

__all__ = ["Base", "metadata", "import_all_models"]

_NAMING_CONVENTION: Final[dict[str, str]] = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(referred_table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}

_metadata = sa.MetaData(naming_convention=_NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative base class that all ORM models must inherit from."""

    metadata = _metadata


metadata = Base.metadata

_models_imported: bool = False


def import_all_models() -> None:
    """Import all ORM model modules so ``Base.metadata`` is populated."""

    global _models_imported
    if _models_imported:
        return

    importlib.import_module("app.models.core")

    _models_imported = True
