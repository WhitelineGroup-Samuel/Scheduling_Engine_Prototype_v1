"""
TEST DESCRIPTION BLOCK — tests/fixtures/time.py

Purpose
-------
Provide **time-related** test utilities/fixtures to make time-dependent tests deterministic.

What to include
---------------
1) Imports:
   - stdlib: datetime, contextlib
   - third-party: pytest, freezegun (optional) OR implement a minimal freezer using monkeypatch
   - local: app.utils.time (if helpers exist like now_utc(), to_local(), etc.)

2) Fixture: freeze_time()  [scope="function"]
   - Either:
     a) Use freezegun.freeze_time("2024-01-01T00:00:00Z") as a context manager and yield.
     b) Or monkeypatch datetime in app.utils.time to return a fixed aware UTC datetime.
   - After test: automatically restore real time.

3) Helper contextmanager (optional): fixed_utc(dt: datetime)
   - Generic way to freeze time inside a "with" block for ad-hoc tests.

Expectations
------------
- All frozen datetimes must be timezone-aware (UTC) to avoid naive/aware mixing.
- Tests consuming this fixture should not rely on system clock.

Dependencies on other scripts
-----------------------------
- app/utils/time.py : now_utc(), to_local(), parse_iso8601()

Notes
-----
- If you prefer not to add freezegun dependency now, provide a monkeypatch-based approach.
- Keep the API tiny to minimize maintenance overhead.
"""
