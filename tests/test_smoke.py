"""
TEST DESCRIPTION BLOCK — tests/test_smoke.py

Purpose
-------
Fast, read-only **smoke tests** that prove the skeleton boots:
- Settings load & validate correctly from environment variables (.env.test).
- Logging configuration builds without error and emits expected fields (incl. trace_id).
- DB healthcheck can execute *read-only* queries against the test database.
- Alembic wiring (env script + target_metadata) is discoverable.
- CLI entrypoints are discoverable and show help.

What to include
---------------
1) Imports:
   - stdlib: os, json, subprocess, sys, pathlib
   - third-party: pytest
   - local: app.config.settings (get_settings/Settings),
            app.config.logging_config (configure_logging),
            app.db.healthcheck (ping),
            app.db.alembic_env (target_metadata)

2) Tests (all MUST be fast and side-effect free):
   - test_settings_loads_and_validates():
       * Arrange: load settings using the canonical factory (e.g., get_settings()).
       * Assert: settings.APP_ENV == "test"
                settings.TIMEZONE == "Australia/Melbourne"
                settings.LOG_LEVEL == "INFO" (or maps to logging.INFO)
                effective database_url is either provided OR constructed correctly from parts
                boolean parsing for LOG_JSON behaves (e.g., "false" -> False)
   - test_timezone_available():
       * Assert that zoneinfo.ZoneInfo(settings.TIMEZONE) is loadable and tz-aware.
   - test_logging_config_builds_and_emits(caplog):
       * Arrange: call logging_config.configure_logging(settings).
       * Act: log a test message via a named logger.
       * Assert (human mode): first record has `trace_id` attribute populated.
       * Assert (json mode): temporarily set LOG_JSON=true, reconfigure, emit one line,
         json.loads(line) contains keys: ts, level, logger, trace_id, msg, env, app, version.
   - test_db_healthcheck_readonly():
       * Arrange: build a SQLAlchemy Engine from settings (do NOT create/drop anything).
       * Act: call healthcheck.ping(engine) which should execute SELECT-only statements.
       * Assert: result.ok is True, result.database == "scheduling_test",
                server_version is non-empty, duration_ms > 0.
   - test_alembic_wiring_discoverable():
       * Assert: app.db.alembic_env exposes target_metadata (Base.metadata)
                and that it is a sqlalchemy MetaData instance (no migration apply here).
   - test_cli_help_succeeds(tmp_path):
       * Act: run "python manage.py --help" via subprocess.
       * Assert: return code == 0 and some known commands are mentioned (e.g., "check-env").

3) Markers & Performance:
   - No @pytest.mark.integration here; keep these tests < 1s cumulative where possible.
   - Avoid writing to DB or filesystem (use tmp_path for any transient files).

4) Failure messages:
   - Provide clear asserts with helpful messages so misconfigurations are obvious.

Dependencies on other scripts
-----------------------------
- app/config/settings.py : Pydantic Settings model and/or factory
- app/config/logging_config.py : dictConfig builder (console + JSON + trace_id)
- app/utils/logging_tools.py : trace id context access (implicitly via filter)
- app/db/healthcheck.py : read-only ping implementation
- app/db/alembic_env.py : target_metadata wiring
- app/errors/handlers.py : map_exception/handle_cli_error used by CLI smoke if needed

Notes
-----
- Tests assume `.env.test` is auto-loaded by tests/conftest.py.
- DB used here is "scheduling_test"; do not mutate schema or data.
"""

import pytest

# TEMP: Keep the global skip while migrations/logging are still being wired.
pytestmark = pytest.mark.skip(
    reason="Migrations/logging not wired yet; remove when ready."
)
