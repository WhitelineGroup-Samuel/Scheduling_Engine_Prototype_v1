"""
===============================================================================
File: app/db/healthcheck.py
Purpose:
  Lightweight DB connectivity verification.

Responsibilities:
  - ping(session_or_engine) -> Dict[str, Any] with duration and server version.
  - Raise DbError on failure.

Collaborators:
  - app.errors.exceptions.DbError

Used by:
  - run.py, app/cli/diag.py
===============================================================================
"""