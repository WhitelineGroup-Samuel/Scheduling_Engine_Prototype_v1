"""
TEST DESCRIPTION BLOCK — tests/integration/test_db_connect.py

Purpose
-------
Validate that the test database is reachable via SQLAlchemy and responds to **read-only** queries.

What to include
---------------
1) Imports:
   - stdlib: os
   - third-party: pytest, sqlalchemy (text)
   - local: fixtures from tests/fixtures/db.py (engine or db_connection)

2) Marker:
   - Use @pytest.mark.integration for the test module or individual tests.

3) Tests:
   - test_engine_can_connect(engine):
       * Act: with engine.connect() as conn: SELECT current_database(), version()
       * Assert: DB name == "scheduling_test"; version string non-empty.
   - test_readonly_query_succeeds(db_connection):
       * Act: SELECT NOW()
       * Assert: single row returned; value is non-null.

Constraints
-----------
- No writes (no INSERT/UPDATE/CREATE/DROP).
- Keep runtime < 0.2s ideally.

Dependencies on other scripts
-----------------------------
- tests/fixtures/db.py : engine, db_connection
- app/config/settings.py : for connection URL under the hood

Notes
-----
- This test gives a clear, early signal if the DB service isn't available locally or in CI.
"""
