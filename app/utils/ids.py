"""
===============================================================================
File: app/utils/ids.py
Purpose:
  Generate stable identifiers (UUID4/ULID) and validate them.

Responsibilities:
  - new_uuid(), new_ulid()
  - is_uuid(value) -> bool

Notes:
  - Keep no DB coupling here.
===============================================================================
"""
