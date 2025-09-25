"""
===============================================================================
File: app/db/base.py
Purpose:
  Expose the canonical SQLAlchemy declarative base (`Base`) and metadata for the app.
  All models must inherit from this Base. Alembic uses `target_metadata = Base.metadata`.

Outcomes Codex must deliver
---------------------------
1) Define a declarative Base with a **stable naming convention** so Alembic
   autogenerate produces consistent constraint/index names.
2) Expose `Base` and `Base.metadata` (the latter is Alembic's `target_metadata`).
3) Provide a no-op function `import_all_models()` that, when called, imports
   all ORM model modules (e.g., app.models.*) exactly once so that
   `Base.metadata` is fully populated before Alembic autogenerate runs.
4) Keep this module side-effect free (do NOT import models at import time).
   Alembic env will call `import_all_models()` explicitly.

Required implementation details
-------------------------------
- Use SQLAlchemy **2.x** APIs.
- __tablename__ explicitly set for each model
- id columns: UUID or BIGSERIAL (project decision); organisations.id = UUID v4 (recommended)
- timestamps: created_at, updated_at in UTC (DB default or app-managed)
- Construct `Base` via `declarative_base()` using a `MetaData` object with the
  following naming convention:
    pk: pk_%(table_name)s
    fk: fk_%(table_name)s_%(referred_table_name)s_%(column_0_name)s
    ix: ix_%(table_name)s_%(column_0_name)s
    uq: uq_%(table_name)s_%(column_0_name)s
    ck: ck_%(table_name)s_%(constraint_name)s
- Export:
    Base                # the declarative base class
    metadata            # alias to Base.metadata
    import_all_models   # function to import app models

Guidance for future models (context for Codex)
----------------------------------------------
- We’ll initially mirror the ERD for `organisations` exactly (INTEGER/SERIAL PK).
  Later entities may move to UUID v4 PKs with `gen_random_uuid()` (pgcrypto).
- Store timestamps in UTC (`timezone=True`); convert to Australia/Melbourne in app.

Visibility to Alembic
---------------------
- app/db/alembic_env.py must import `from app.db.base import Base` and set:
    target_metadata = Base.metadata
- Ensure models are imported somewhere under app/models/__init__.py so Alembic
  autogenerate can discover them (import side-effects ONLY in alembic env).

Collaborators
-------------
- app/models/* : concrete ORM models; keep imports centralized via
  the `import_all_models()` function to avoid circular imports.
- app/db/alembic_env.py : calls `import_all_models()` before autogenerate.

Non-goals
---------
- Do NOT emit any DDL or connect to the database here.
- Do NOT auto-import model modules at import time.

Testing
-------
- Smoke: target_metadata is a sqlalchemy MetaData instance.
- Migration diff: running `alembic revision --autogenerate` sees model tables.

Notes
-----
- Keep this module side-effect free (no Engine creation, no Session).
===============================================================================
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Final

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# Stable naming convention for Alembic/autogenerate
NAMING_CONVENTION: Final = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(referred_table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


def import_all_models() -> None:
    """
    Import all ORM models to ensure Base.metadata is fully populated.
    Call this before Alembic autogenerate or any metadata-based operations.

    Implementation notes:
    - Dynamically import all submodules under `app.models`.
    - Keep this a no-op if called multiple times (Python import system ensures that).
    """
    import app.models as models_pkg  # local import to avoid cycles

    for _, modname, _ in pkgutil.iter_modules(
        models_pkg.__path__, models_pkg.__name__ + "."
    ):
        importlib.import_module(modname)
