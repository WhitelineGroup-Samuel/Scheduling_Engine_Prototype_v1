"""
===============================================================================
File: app/repositories/base_repository.py
Purpose:
  Generic CRUD convenience around a SQLAlchemy session.

Responsibilities:
  - __init__(session)
  - add(entity), get_by_id(Model, id), list(Model, filters), delete(entity)
  - commit(), rollback() (explicit control)

Collaborators:
  - app.db.session.get_session()
  - app.errors.exceptions.DbError

Notes:
  - Keep thin; heavy queries belong in specific repositories.
===============================================================================
"""