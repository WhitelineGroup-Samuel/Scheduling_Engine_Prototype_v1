"""
===============================================================================
File: app/db/engine.py
Purpose:
  Construct the SQLAlchemy Engine using validated settings.

Responsibilities:
  - get_engine(settings) -> Engine (pool sizing, echo, SSL, future=True)
  - Optionally register connection event listeners (e.g., set timezone).

Collaborators:
  - app.config.settings
  - app.errors.exceptions.DbError on connection failures

Notes:
  - Keep engine a singleton per-process where possible.
===============================================================================
"""
