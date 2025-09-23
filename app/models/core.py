"""
===============================================================================
File: app/models/core.py
Purpose:
  Provide shared ORM mixins (created_at, updated_at, soft_delete, user stamps)
  used across domain models.

Responsibilities:
  - TimestampMixin, SoftDeleteMixin, UserStampMixin
  - __repr__/identity helpers

Collaborators:
  - app.db.base.Base

Testing:
  - Verify default values, onupdate triggers, and serialization helpers.
===============================================================================
"""
