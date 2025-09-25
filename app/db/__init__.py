"""
===============================================================================
Package: app.db
Purpose:
  Database access layer integration point. Exports get_engine() and SessionLocal,
  and central metadata for Alembic usage.

Exports:
  - get_engine(), SessionLocal, get_session()

Collaborators:
  - .engine, .session, .base (metadata), .healthcheck, .seed
===============================================================================
"""
