"""
===============================================================================
File: app/db/alembic_env.py
Purpose:
  Alembic environment script. Wires Alembic to SQLAlchemy metadata and app
  settings so `alembic upgrade head` uses our config paths and DB URL.

Responsibilities:
  - Provide run_migrations_offline/online() implementations.
  - Load settings via app.config.settings.get_settings().
  - Target_metadata = app.db.base.Base.metadata

Collaborators:
  - Alembic (alembic.ini), app.db.base, app.config.paths

Notes:
  - Ensure script works both for CLI and programmatic invocations.
===============================================================================
"""