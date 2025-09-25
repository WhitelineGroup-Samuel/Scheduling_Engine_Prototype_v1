"""
TEST DESCRIPTION BLOCK — tests/unit/test_errors_mapping.py

Purpose
-------
Ensure low-level/library exceptions are mapped to our domain exceptions (`AppError`
subclasses) with the correct error codes, severities, and exit codes as defined in:
- app/errors/codes.py
- app/errors/exceptions.py
- app/errors/handlers.py  (map_exception)

Scope
-----
Unit tests only. No real DB, no network, no filesystem. Use fakes/mocks to simulate
exceptions from SQLAlchemy, psycopg, Alembic, Pydantic, OS, and generic Python.

What to include
---------------
1) Imports:
   - stdlib: asyncio
   - third-party: pytest
   - local: app.errors.handlers (map_exception), app.errors.exceptions (AppError subclasses),
            app.errors.codes (ErrorCode catalog)
   - vendor exceptions to simulate:
       * sqlalchemy.exc: OperationalError, ProgrammingError, IntegrityError
       * psycopg.errors: InvalidCatalogName (skip if psycopg not installed)
       * pydantic: ValidationError (build a tiny model to raise it)
       * alembic.util: CommandError (skip if alembic not installed)
       * builtin: FileNotFoundError, PermissionError, asyncio.TimeoutError

2) Tests (table-driven where possible):
   - test_map_operational_error_to_db_connection_error():
       * Make a sqlalchemy.exc.OperationalError instance (can pass None-like params).
       * Assert mapped is DBConnectionError; code "SENG-DB-001"; exit 65; severity "CRITICAL".
   - test_map_integrity_error_to_conflict_error():
       * Use IntegrityError with UNIQUE violation-like message.
       * Expect ConflictError; code "SENG-DOMAIN-002"; exit 69.
   - test_map_programming_error_to_db_operation_error():
       * Expect DBOperationError; code "SENG-DB-003"; exit 65.
   - test_map_psycopg_invalid_catalog_to_db_connection_error():
       * psycopg.errors.InvalidCatalogName → DBConnectionError.
   - test_map_pydantic_validation_error_to_validation_error():
       * Trigger Pydantic ValidationError; expect code "SENG-VALIDATION-001"; exit 64.
   - test_map_os_errors_to_io_error():
       * FileNotFoundError & PermissionError → IOErrorApp; exit 74.
   - test_map_timeout_to_timeout_error():
       * asyncio.TimeoutError → TimeoutError; exit 75.
   - test_map_unknown_to_unknown_error():
       * Exception("boom") → UnknownError; code "SENG-UNKNOWN-000"; exit 1; context["type"] == "Exception".

3) Assertions:
   - Always assert instance type of AppError subclass.
   - Assert error.code, error.exit_code, error.severity match the catalog.
   - Optionally assert `context` contains safe fields (e.g., {"type": "..."}).

Markers & Performance
---------------------
- No @pytest.mark.integration.
- Keep tests fast (< 50ms ideally).
- If optional libs are missing, skip those specific tests with clear reasons.

Dependencies on other scripts
-----------------------------
- app/errors/codes.py
- app/errors/exceptions.py
- app/errors/handlers.py

Notes
-----
- If importing vendor exceptions is cumbersome, create minimal stand-ins or
  skip with a clear message using pytest.skip.
"""

import pytest

# TEMP: Remove this global skip once error mapping is implemented.
pytestmark = pytest.mark.skip(
    reason="Error mapping not implemented yet; remove when ready."
)
