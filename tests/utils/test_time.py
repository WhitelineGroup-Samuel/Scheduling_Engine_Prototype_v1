"""
TEST DESCRIPTION BLOCK — tests/utils/test_time.py

Purpose
-------
Validate time utilities with timezone-awareness and predictable conversion between UTC and local (Australia/Melbourne).

What to include
---------------
1) Imports:
   - stdlib: datetime (timezone, timedelta)
   - third-party: pytest
   - local: app.utils.time (now_utc(), to_local(), parse_iso8601()), tests/fixtures/time (freeze_time)

2) Tests:
   - test_now_utc_is_aware():
       * Act: dt = now_utc()
       * Assert: dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) == timedelta(0)
   - test_to_local_converts_correctly(freeze_time):
       * Arrange: fix time to known UTC point (e.g., 2024-01-01T00:00:00Z)
       * Act: local = to_local(fixed_utc_dt, tz="Australia/Melbourne")
       * Assert: local.tzinfo is aware; offset matches expected for that date (AEST/AEDT)
   - test_parse_iso8601_strict():
       * Act/Assert: valid strings parse to aware datetimes in UTC (or documented behavior),
                    invalid strings raise a ValueError (or custom error type).

3) Edge cases:
   - Daylight saving boundaries: ensure to_local() handles offset changes correctly.

Dependencies on other scripts
-----------------------------
- app/utils/time.py
- tests/fixtures/time.py

Notes
-----
- Avoid relying on system timezone; explicitly set or pass tz names.
- Freeze time where applicable for deterministic outputs.
"""
