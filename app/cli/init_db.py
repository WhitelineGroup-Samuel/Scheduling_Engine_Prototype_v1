"""
===============================================================================
File: app/cli/init_db.py
Purpose:
  Initialize database schema by running Alembic migrations to head.

Responsibilities:
  - Connect to DATABASE_URL; run upgrade head.
  - Optionally create DB if missing (best-effort).

Collaborators:
  - app.db.alembic_env, alembic.config
  - app.errors.exceptions.DbError

Notes:
  - Idempotent; safe if already at head.
===============================================================================
"""