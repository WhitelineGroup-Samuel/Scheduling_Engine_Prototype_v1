"""
TEST DESCRIPTION BLOCK — tests/utils/test_validators.py

Purpose
-------
Prove that validator helpers return True/False for clear tables of inputs (no I/O, fast).

What to include
---------------
1) Imports:
   - third-party: pytest
   - local: app.utils.validators (e.g., is_non_empty_str, is_valid_email, is_valid_url, etc.)

2) Tests:
   - test_is_non_empty_str_table():
       * Table of inputs -> expected True/False (e.g., "", " ", "abc", None, 123 -> False/True etc.)
   - test_is_valid_email_table():
       * Valid examples: "a@b.com", "first.last+tag@domain.co.uk"
       * Invalid examples: "a@", "@b.com", "a@b", "a b@c.com", ""
   - test_is_valid_url_table():
       * Valid: http(s) URLs, with/without ports, query strings
       * Invalid: bare domains without scheme, spaces, malformed schemes

3) Style:
   - Use @pytest.mark.parametrize to keep tests short and readable.

Dependencies on other scripts
-----------------------------
- app/utils/validators.py

Notes
-----
- Provide clear assertion error messages including the input value when a case fails.
- Keep logic pure; avoid network calls or filesystem.
"""
