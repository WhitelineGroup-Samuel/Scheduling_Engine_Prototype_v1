"""
===============================================================================
File: app/db/session.py
Purpose
-------
Provide a robust **Session** factory and utilities for transactional work.
Target characteristics:
- Deterministic transaction boundaries
- Safe defaults (expire_on_commit=False, autoflush=False)
- Easy use in CLI commands and tests
- Predictable cleanup (commit/rollback/close)

Public API (Codex must implement)
---------------------------------
1) def create_session_factory(engine) -> "sessionmaker":
   - Return a `sessionmaker` configured with:
       class_=sqlalchemy.orm.Session
       bind=engine
       expire_on_commit=False  # objects remain usable after commit (common in services/CLIs)
       autoflush=False
       autocommit=False  # SQLAlchemy 2.x default
   - No implicit connection at factory creation.

2) def get_session(session_factory=None):
   - Context manager (yielding Session) for one-shot operations:
     with get_session(SessionLocal) as session:
         # do work
   - Behavior:
       * If session_factory is None, use a **module-level** default `SessionLocal`
         that callers set once after creating the Engine.
       * On normal exit, commit.
       * On exception, rollback and re-raise.
       * Always close() at the end.
   - MUST avoid swallowing exceptions.

3) def session_scope(session_factory=None):
   - Alias to `get_session` for readability; identical semantics.

4) Optional: def begin_nested_for_tests(session):  # used in pytest fixtures
   - Start a SAVEPOINT and return a handle for rollback between tests.

Module-level state (careful)
----------------------------
- `SessionLocal`: optional module-level variable to store a sessionmaker.
  *CLI bootstrap may set:*
      engine = create_engine_from_settings(settings)
      SessionLocal = create_session_factory(engine)
- Module import MUST NOT create an engine or connect to the DB.

Patterns for callers
--------------------
- CLI (seed-data, diag):
    with get_session(SessionLocal) as session:
        # write or read ops
- Repositories:
    - Accept a Session in constructor or methods; do not create Engines/Sessions themselves.
- Tests:
    - tests/fixtures/db.py should:
        * Create an Engine to the **test DB**
        * Create a dedicated SessionLocal for tests
        * Use transaction-per-test with rollback (nested transaction or SAVEPOINT)
        * Ensure no state leakage across tests

Timeouts & safety
-----------------
- Statement timeouts are enforced at the **connection** level via Engine options
  (see app/db/engine.py). Session layer does not set additional timeouts.
- Do not log sensitive values; let top-level logging filters handle redaction.

Error semantics
---------------
- DB exceptions raised inside the context manager propagate up.
- Handlers at the CLI boundary map SQLAlchemy/psycopg exceptions to AppError types
  (ConflictError, DBOperationError, etc.) as per Phase F Step 14.

Testing
-------
- Unit: context manager commits on success, rollbacks on exception, always closes.
- Integration: with test engine, verify a write within a context is visible only
  until the outer test transaction is rolled back by fixtures.

Non-goals
---------
- No async session in v1.
- No global singleton; keep wiring explicit from CLI/run.py.
===============================================================================
"""
