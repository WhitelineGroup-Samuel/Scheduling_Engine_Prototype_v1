"""
TEST DESCRIPTION BLOCK — tests/integration/test_seed_data.py

Purpose
-------
Verify that the seed routines are deterministic, idempotent, and safe. Ensures
the CLI wrapper (--dry-run / --apply) behaves per contract.

What to include
---------------
- Fixtures: test engine + SessionLocal (transaction-per-test)
- Test: first apply inserts; second apply skips
- Test: dry-run predicts actions (mock or call seed_minimal in read-only mode)
- Test: unique constraint behavior (two inserts with same name -> IntegrityError)

Dependencies
------------
- app/db/seed.py
- app/repositories/organisation_repository.py
- app/db/session.py
- tests/fixtures/db.py
"""
