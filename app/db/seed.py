"""
===============================================================================
File: app/db/seed.py
Purpose:
  Minimal seeding utilities to insert placeholder rows (e.g., organisation, user)
  so the environment is operable for early dev/testing.

Responsibilities:
  - seed_minimal(session) -> None
  - Idempotent: safe to run multiple times.

Collaborators:
  - app.models (when added), app.schemas.common for DTOs (optional)

Testing:
  - Ensure seeders are transactional and rollback-safe in tests.
===============================================================================
"""
