"""
TEST DESCRIPTION BLOCK — tests/unit/test_handlers_cli.py

Purpose
-------
Verify CLI error handling emits **one structured log line** with the proper
severity and returns the correct exit code, using:
- app/errors/handlers.py: handle_cli_error, wrap_cli_main, level_for, exc_info_for
- app/errors/exceptions.py: AppError subclasses
- app/config/logging_config.py: configured logger (trace_id injected by filters)

Scope
-----
Unit tests (no DB). Use a real logger configured via configure_logging(settings),
but rely on pytest's `caplog` to capture records. Avoid filesystem and network.

What to include
---------------
1) Imports:
   - stdlib: sys, functools
   - third-party: pytest
   - local:
       * app.errors.handlers: handle_cli_error, wrap_cli_main, level_for
       * app.errors.exceptions: ValidationError, DBConnectionError, UnknownError
       * app.errors.codes: ErrorCode (optional for explicit code checks)
       * app.config.logging_config: configure_logging
       * app.config.settings: get_settings or Settings factory

2) Fixture or setup:
   - Build a Settings object with APP_ENV="test", LOG_JSON=false (human) for readability.
     (Optionally run a second test with LOG_JSON=true to ensure JSON output parses.)
   - Call configure_logging(settings) and get a named logger (e.g., "app.tests.handlers").

3) Tests:
   - test_handle_cli_error_validation_returns_64_and_no_exc_info(caplog):
       * err = ValidationError("bad input", context={"field": "name"})
       * rc = handle_cli_error(err, logger)
       * Assert rc == 64
       * caplog captured 1+ record with level ERROR (no traceback)
       * record has attributes: code, exit_code; filter should inject trace_id
   - test_handle_cli_error_db_connection_critical_has_exc_info(caplog):
       * err = DBConnectionError("cannot connect", context={"host":"localhost","port":5432})
       * rc == 65
       * assert CRITICAL level and exc_info was included (caplog.records[0].exc_info not None)
   - test_wrap_cli_main_converts_exception_to_system_exit(monkeypatch, caplog):
       * Define a dummy function that raises Exception("boom")
       * Decorate with @wrap_cli_main
       * Call and assert SystemExit with code 1 (UnknownError default)
       * Assert one log record emitted at CRITICAL with code SENG-UNKNOWN-000
   - (Optional) test_json_mode_emits_parseable_json(caplog):
       * Reconfigure with LOG_JSON=true and re-run one of the above tests, then
         parse the emitted log line as JSON and assert keys:
         ts, level, logger, trace_id, msg, code, exit_code, env, app, version.

Markers & Performance
---------------------
- No @pytest.mark.integration.
- Keep each test < 100ms. Avoid slow stack traces by disabling exc_info for expected errors.

Dependencies on other scripts
-----------------------------
- app/errors/handlers.py
- app/errors/exceptions.py
- app/errors/codes.py
- app/config/logging_config.py
- app/config/settings.py
- app/utils/logging_tools.py (indirectly via logging filters)

Notes
-----
- If log capture shows multiple records, ensure your logger is not propagating to root
  with duplicate handlers (configure_logging should set propagate=False or attach once).
"""

import pytest

# TEMP: Remove this global skip once CLI error handler is implemented.
pytestmark = pytest.mark.skip(
    reason="CLI error handler not implemented yet; remove when ready."
)
