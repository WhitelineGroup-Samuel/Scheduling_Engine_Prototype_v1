"""
===============================================================================
File: app/db/seed.py
Purpose
-------
Provide **deterministic, idempotent** seed routines for development & test
databases. Seeding must be safe to run multiple times and should never duplicate
rows. All writes occur inside a single transaction that either fully commits or
rolls back.

Scope (v1)
----------
- Minimal dataset to validate the pipeline end-to-end using the **organisations**
  table as the first entity scope.
- Additional seeders may be added later as separate functions.

Public API (Codex must implement)
---------------------------------
def seed_minimal(session, *, org_name: str | None = None) -> dict:
    Idempotently ensure the presence of a single 'organisation' record, plus
    any trivial referential prerequisites (none in v1).
    - session: SQLAlchemy Session (already opened by caller).
    - org_name: Optional explicit organisation name. Defaults to "Whiteline Demo".
    Returns:
      {
        "inserted": int,   # rows inserted
        "updated": int,    # rows updated in-place
        "skipped": int,    # rows already present & unchanged
        "items": [         # optional details (may be omitted for perf)
          {"id": "<uuid>", "name": "...", "slug": "..."}
        ],
      }
    Contract:
      - Must be **idempotent**: running repeatedly yields "skipped" after first run.
      - Must be **deterministic**: same inputs -> same outputs.
      - Must perform only necessary writes (no churn on timestamps unless changed).
    Error policy:
      - Do not swallow DB exceptions. Let IntegrityError/OperationalError bubble.
      - Higher layers (CLI) map exceptions to AppError via handlers.

def seed_from_plan(session, plan: "SeedPlan") -> dict:
    General-purpose entry that executes a declarative plan object (see SeedPlan
    below). Enables composing multiple seed operations while preserving
    idempotence, single-transaction semantics, and a unified summary.

# Optional type to make plans explicit (simple dataclass / NamedTuple)
class SeedPlan:
    Represents a declarative, ordered set of seed tasks.
    Fields:
      organisations: list[OrganisationSeed]
      # Future: teams, venues, seasons, fixtures...

class OrganisationSeed:
    DTO describing an organisation to ensure exists.
    Fields:
      name: str             # business key (unique)
      slug: str | None      # optional; when absent, derive from name

Implementation notes
--------------------
- Use OrganisationRepository for all DB access.
- Generate/normalize slug using the same rules as our DTOs (schemas/organisation.py).
- Upsert strategy (portable v1):
    * get_by_name() -> if found and fields differ, update (only changed fields)
    * else create()
- Ensure you **refresh()** after create/update to return current row state.

Transaction model
-----------------
- Caller opens a Session (context-managed). This module does not manage commits.
- The CLI (`seed-data --apply`) wraps seed_minimal() within one transaction.
- On any exception, callers must rollback and map errors at the boundary.

Safety & side effects
---------------------
- No destructive operations (no truncates / deletes) in v1 seeders.
- No logging here; the CLI prints a single structured summary line.
- No secret values anywhere.

Validation
----------
- Reject empty `org_name` after stripping; raise ValueError prior to DB work.
- Ensure slug normalization yields a valid slug; if impossible, raise ValueError.

Performance
-----------
- Seed should complete in < 100 ms for a warm connection.
- Avoid N+1; one lookup + create/update per entity is sufficient.

Testing expectations
--------------------
- First run: returns {"inserted": 1, "updated": 0, "skipped": 0}
- Second run (same inputs): {"inserted": 0, "updated": 0, "skipped": 1}
- Change org_name to an existing record name → conflict surfaces as IntegrityError
  (when slug collides); the CLI maps this to ConflictError (exit 69).
- With explicit slug: upsert respects provided slug (normalized).

Dependencies
------------
- app.repositories.organisation_repository.OrganisationRepository
- app.schemas.organisation.OrganisationInDTO / normalizers (for slug derivation)
- app.db.session.get_session (used by the CLI, not here)

Extensibility (future)
----------------------
- Add additional seeders: teams, venues, seasons...
- Introduce reproducible **fixture sets** keyed by environment (dev/test/demo).
===============================================================================
"""
