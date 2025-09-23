"""
===============================================================================
File: app/db/base.py
Purpose:
  Declarative Base and metadata registration point for models.

Responsibilities:
  - Base = declarative_base()
  - Import app.models.* to populate Base.metadata for Alembic.

Collaborators:
  - app.models (ensure imports happen exactly once)
===============================================================================
"""
