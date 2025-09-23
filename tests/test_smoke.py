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
   - local: app.config.settings (get_settings or Settings factory), app.config.logging_config
            app.db.healthcheck, app.db.alembic_env (for target_metadata)

2) Tests (all MUST be fast and side-effect free):
   - test_settings_loads_and_validates():
       * Arrange: load settings using the canonical factory (e.g., get_settings()).
       * Assert: settings.app_env == "test"
                settings.timezone == "Australia/Melbourne"
                settings.log_level is parsed to expected numeric level (INFO)
                database_url is either provided OR constructed correctly from parts
                boolean parsing for LOG_JSON behaves (e.g., "false" -> False)
   - test_timezone_available():
       * Assert that zoneinfo.ZoneInfo(settings.timezone) is loadable and tz-aware.
   - test_logging_config_builds_and_emits(caplog):
       * Arrange: call logging_config.configure_logging(settings).
       * Act: log a test message via a named logger.
       * Assert: caplog captured at least one record with expected fields:
                record.levelname, record.name, record.message (or getMessage())
                and a trace_id field present (either attached via extra or LogRecord adapter).
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
   - Avoid writing to DB or filesystem (use tmp_path for any transient files, then clean up).

4) Failure messages:
   - Provide clear asserts with helpful messages so misconfigurations are obvious.

Dependencies on other scripts
-----------------------------
- app/config/settings.py : settings factory / Pydantic Settings model
- app/config/logging_config.py : dictConfig builder (console + optional JSON + trace_id)
- app/db/healthcheck.py : read-only ping implementation
- app/db/alembic_env.py : target_metadata wiring

Notes
-----
- Tests assume `.env.test` is auto-loaded by tests/conftest.py.
- DB used here is "scheduling_test"; do not mutate schema or data.
"""
