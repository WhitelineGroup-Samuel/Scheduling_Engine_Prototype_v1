"""
TEST DESCRIPTION BLOCK — tests/integration/test_migrations.py

Purpose
-------
When Alembic is wired, prove that migrations can be discovered and applied to the test DB.

What to include
---------------
1) Imports:
   - stdlib: subprocess, sys, pathlib
   - third-party: pytest, sqlalchemy (inspect), sqlalchemy.text
   - local: tests/fixtures/db.py (engine), alembic configuration helpers (if any)

2) Marker:
   - @pytest.mark.integration

3) Pre-conditions:
   - alembic.ini must be configured.
   - app/db/alembic_env.py must set target_metadata.

4) Tests:
   - test_alembic_upgrade_head_subprocess(engine):
       * Act: run "alembic upgrade head" via subprocess (cwd=repo root).
       * Assert: exit code 0; afterward, "alembic_version" table exists and version != None.
   - test_alembic_stamp_head_no_apply(engine): (optional)
       * For scenarios where we only stamp, not apply; assert success and version table present.

5) Cleanup:
   - Not required if using a separate test DB and rollback per test; however,
     if applying DDL changes, scope this test carefully since DDL isn't rolled back.
     Consider running once per session or using a dedicated DB schema.

Dependencies on other scripts
-----------------------------
- alembic.ini, app/db/alembic_env.py
- tests/fixtures/db.py

Notes
-----
- If migrations are not ready yet, mark these tests with @pytest.mark.skip(reason="...") or conditionally skip.
- Once models exist, add explicit assertions that expected tables/columns/indexes exist after upgrade.
"""

import pytest

pytestmark = pytest.mark.skip(reason="Migrations not wired yet")
