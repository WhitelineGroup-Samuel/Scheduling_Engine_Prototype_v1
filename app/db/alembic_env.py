"""
===============================================================================
File: app/db/alembic_env.py
Purpose:
  Alembic environment script (project-specific). It wires Alembic to our
  SQLAlchemy metadata and runtime settings so `alembic upgrade head`
  operates on the correct database and sees all models.

Outcomes Codex must deliver
---------------------------
1) **Online mode only** (we do not generate offline SQL files yet).
2) Load settings from our app config (Pydantic Settings), resolving DB URL as:
     - If `DATABASE_URL` is set: use it.
     - Else compose from parts: DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME.
3) Import `Base` metadata from `app.db.base` and set:
     target_metadata = Base.metadata
   Ensure models are imported first by calling `import_all_models()`.
4) Create an Engine with:
     future=True, pool_pre_ping=True
   and pass it to Alembic's migration context for online migrations.
5) Set safe Postgres session guards prior to running migrations:
     SET lock_timeout = '5s';
     SET statement_timeout = '60s';
   (Execute via connection before `context.run_migrations()`.)
6) Support both CLI invocation (`alembic upgrade head`) and programmatic use.
7) Avoid importing the entire app graph; only import minimal settings + base.
8) Ensure that the first entity `organisations` (Organisation model in
   app.models.core) is visible after calling `import_all_models()` so
   autogenerate can create the table per ERD.

Required functions / structure
------------------------------
- Provide `run_migrations_online()` which:
    * loads settings
    * builds SQLAlchemy Engine
    * configures Alembic context with `target_metadata`
    * executes the timeout `SET` statements
    * runs migrations inside a transaction block

- Provide a no-op `run_migrations_offline()` that raises NotImplementedError
  (document that we only support online mode for now).

Pathing & imports
-----------------
- Ensure sys.path includes the repository root so `import app...` works when
  Alembic invokes this script from the repo root.
- Alembic `script_location` is `migrations/` (set in alembic.ini). If an
  Alembic-generated `migrations/env.py` exists, it should simply import and
  delegate to `run_migrations_online()` from this module.

Postgres specifics & notes
--------------------------
- For large indexes, prefer CREATE INDEX CONCURRENTLY (separate transaction).
- Search path: start with `public` schema only.

Collaborators
-------------
- app.config.settings : Pydantic Settings factory (get_settings()).
- app.db.base         : Base/metadata and `import_all_models()`.
- alembic.ini         : provides script location & logging config.

===============================================================================
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Import Base/metadata for target_metadata (imports must be at top for Ruff E402)
from app.db.base import Base, import_all_models

# Ensure sys.path includes repo root for `import app...`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Alembic Config object, for logging etc.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure models are imported so Alembic autogenerate can see them
import_all_models()
target_metadata = Base.metadata


def _get_database_url() -> str:
    """
    Resolve the database URL from environment or app settings.
    Precedence:
      1) OS env DATABASE_URL
      2) Compose from DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME via settings
    """
    # 1) Try direct env
    direct = os.getenv("DATABASE_URL")
    if direct:
        return direct

    # 2) Use app settings (preferred path in dev/test)
    from importlib import import_module

    s = getattr(import_module("app.config.settings"), "get_settings")()
    # If settings object already exposes DATABASE_URL, prefer it
    url = getattr(s, "DATABASE_URL", None)
    if isinstance(url, str) and url:
        return url

    user = getattr(s, "DB_USER", None)
    pw = getattr(s, "DB_PASSWORD", None)
    host = getattr(s, "DB_HOST", None)
    port = getattr(s, "DB_PORT", None)
    name = getattr(s, "DB_NAME", None)
    if all([user, pw, host, port, name]):
        return f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{name}"

    raise RuntimeError("Could not resolve database URL from environment or settings")


def run_migrations_online() -> None:
    """
    Run Alembic migrations in 'online' mode.
    """
    connectable = create_engine(
        _get_database_url(),
        poolclass=pool.NullPool,
        future=True,
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        # Set Postgres session timeouts for safe migrations
        connection.exec_driver_sql("SET lock_timeout = '5s'")
        connection.exec_driver_sql("SET statement_timeout = '60s'")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_offline() -> None:
    """
    Offline mode is not supported. Use online migrations only.
    """
    raise NotImplementedError(
        "Offline migrations are not supported. Run in online mode."
    )
