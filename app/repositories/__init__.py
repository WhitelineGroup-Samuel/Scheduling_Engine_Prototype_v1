"""
===============================================================================
Package: app.repositories
Purpose
-------
Provide a thin, testable data-access layer over SQLAlchemy Sessions/Models.
Repositories must:
- Be **stateless** (no global session); accept a `Session` per-operation or at init.
- Never create Engines/Sessions; callers provide them (see app.db.session).
- Map low-level SQL/driver errors to **AppError** types at the CLI boundary only;
  inside the repo, raise the original SQLAlchemy exceptions (so handlers can map).

Repository design principles
----------------------------
- **Explicit Session**: Each method receives a `Session` (preferred) or the repo
  is constructed with a `Session` to be used for the method lifetime.
- **Idempotent Reads**: Reads never mutate state.
- **Deterministic Writes**: Writes return the created/updated domain row (ORM object).
- **UTC time**: Use app.utils.time helpers for timestamps; DB defaults preferred.
- **No logging inside repositories**: Let callers log; repositories are pure access.

Error policy (alignment with Phase F Step 14)
---------------------------------------------
- Repositories may catch IntegrityError/ProgrammingError to add context and re-raise
  the **same** exception type (do NOT convert to AppError here). Handlers will map:
  - IntegrityError (unique violation) → ConflictError
  - ProgrammingError → DBOperationError
  - OperationalError → DBConnectionError

Testing conventions
-------------------
- Unit (with test DB): Use transaction-per-test fixture; no state leakage.
- Factories/fixtures create rows via repository methods to test constraints.
- Assertions check DB state (counts, unique constraints, updates).

Exports
-------
- BaseRepository
- OrganisationRepository
===============================================================================
"""
