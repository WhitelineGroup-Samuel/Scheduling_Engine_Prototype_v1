"""
TEST DESCRIPTION BLOCK — tests/fixtures/db.py

Purpose
-------
Provide **database fixtures** for integration tests:
- Engine creation tied to the test environment.
- Transactional Session per test with automatic ROLLBACK (no persistent writes).
- Optional Alembic migration application fixture (enabled once Alembic wiring exists).

What to include
---------------
1) Imports:
   - stdlib: os
   - third-party: pytest, sqlalchemy (create_engine, Engine, text), sqlalchemy.orm (sessionmaker, Session)
   - local: app.config.settings (for DB settings and URL), app.db.engine (if you expose factory),
            alembic (optional) for migration fixture when enabled.

2) Fixture: engine() -> sqlalchemy.Engine  [scope="session"]
   - Build a SQLAlchemy Engine using DATABASE_URL (constructed from parts if necessary).
   - echo=False, future=True, pool_pre_ping=True.
   - yield the engine, then dispose after session ends.

3) Fixture: db_connection(engine) -> Connection  [scope="function"]
   - engine.connect()
   - yield connection
   - finally: connection.close()

4) Fixture: session_factory(engine) -> sessionmaker  [scope="session"]
   - sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

5) Fixture: db_session(session_factory, engine) -> Session  [scope="function"]
   - Begin a transaction on connection.
   - Bind Session to connection using session_factory.
   - yield Session to test.
   - After test: rollback transaction, close session.

6) (Enable later) Fixture: migrated_db(engine) -> None  [scope="session"]
   - Use Alembic programmatic API or subprocess call "alembic upgrade head".
   - Ensure it only runs once per test session.
   - Intended for tests that require schema to be at head.

Expectations
------------
- Fixtures must NOT create or drop databases.
- All writes during tests are rolled back per test function (db_session).
- All tests should default to read-only unless explicitly marked otherwise.
- Engine and sessions must be created with SQLAlchemy 2.x style.

Dependencies on other scripts
-----------------------------
- app/config/settings.py : DB URL construction and validation
- app/db/engine.py : (optional) helper to create engine using uniform options
- Alembic config: app/db/alembic_env.py and alembic.ini (for migrated_db)

Notes
-----
- Keep fixtures small and explicit; avoid session/engine global state.
- Use @pytest.mark.integration on tests that rely on these fixtures.
"""
