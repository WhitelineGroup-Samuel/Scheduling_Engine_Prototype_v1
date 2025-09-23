"""
===============================================================================
File: app/db/session.py
Purpose:
  Provide SessionLocal (sessionmaker) and safe context managers for DB sessions.

Responsibilities:
  - SessionLocal = sessionmaker(bind=get_engine(...), expire_on_commit=False)
  - get_session() -> contextmanager yielding Session with auto-commit/rollback.

Collaborators:
  - app.db.engine.get_engine
  - app.errors.exceptions.DbError for transactional errors

Testing:
  - Transaction rollbacks in tests/fixtures/db.py.
===============================================================================
"""