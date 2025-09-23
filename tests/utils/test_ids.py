"""
TEST DESCRIPTION BLOCK — tests/utils/test_ids.py

Purpose
-------
Verify ID helpers behave deterministically and safely (format, uniqueness).

What to include
---------------
1) Imports:
   - stdlib: re
   - third-party: pytest
   - local: app.utils.ids (e.g., new_uuid_str(), maybe ULID helpers later)

2) Tests:
   - test_new_uuid_str_format():
       * Act: s = new_uuid_str()
       * Assert: matches canonical UUID v4 pattern (hex + hyphens), len == 36.
   - test_new_uuid_str_uniqueness():
       * Generate e.g., 1000 IDs; assert len(set(ids)) == len(ids)

3) Edge cases:
   - If you add a ULID helper later, add tests for sortability/monotonicity.

Dependencies on other scripts
-----------------------------
- app/utils/ids.py

Notes
-----
- Keep tests fast; no I/O or DB.
"""
