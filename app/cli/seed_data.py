"""
===============================================================================
File: app/cli/seed_data.py
Purpose
-------
Populate minimal, idempotent development/test data (e.g., a sample organisation).
Default is **dry-run** for safety.

Command
-------
manage.py seed-data [--org-name TEXT] [--apply/--dry-run] [--verbose/-v]

Flags & behavior
----------------
--org-name TEXT : Optional override for the default organisation name.
--apply         : Perform upserts inside a transaction (default is --dry-run).
--dry-run       : Print what would be inserted/updated (default).
--verbose/-v    : DEBUG logging for this run.

Responsibilities
----------------
1) Load settings; configure logging; start new trace.
2) Open a SQLAlchemy session (scoped or context-managed).
3) Compute intended changes (deterministic & idempotent).
4) If --dry-run: print counts; DO NOT write; exit 0.
5) If --apply: upsert rows (e.g., Organisation by unique name/slug); commit.
6) Return a summary: {"inserted": n, "updated": m, "skipped": k}.

Exit codes
----------
- DBOperationError (failed SQL)        → 65
- ConflictError (unexpected uniqueness)→ 69
- Success                               → 0

Integration & dependencies
--------------------------
- app.db.session.get_session() or SessionLocal
- app.db.seed.seed_minimal(session, org_name)  # idempotent helper
- app.repositories.organisation_repository
- app.errors.handlers (@wrap_cli_main)
- app.config.logging_config

Logging contract
----------------
- INFO summary on success with counts and duration_ms.
- On failure: single structured error line (no secrets).

Examples
--------
  manage.py seed-data
  manage.py seed-data --org-name "Demo Org"
  manage.py seed-data --apply -v

Notes
-----
- No destructive operations; only upserts for dev/test convenience.
===============================================================================


ADDENDUM — Seed expectations
===============================================================================
Command flow (authoritative)
----------------------------
1) Parse flags:
   --org-name TEXT      : optional name; default "Whiteline Demo"
   --apply / --dry-run  : default --dry-run
   -v / --verbose       : bump log level for this run

2) Boot:
   - settings = get_settings()
   - configure_logging(settings)
   - start a new trace context (with_trace_id(new_trace_id()))

3) Open session (via SessionLocal from app.db.session):
   - If --dry-run:
       * Compute intended changes WITHOUT writing:
           - Look up organisation by name via OrganisationRepository.get_by_name()
           - If missing: would insert (derive/normalize slug if absent)
           - If exists but slug/name normalization differs: would update
       * Print a human summary (counts and actions) and exit 0.
       * (JSON output is optional in v1; human output is sufficient.)
   - If --apply:
       * Wrap in one transaction:
           result = seed_minimal(session, org_name=...)
           commit
           print one INFO summary line with counts and key identifiers
           (e.g., organisation name, slug, id)
       * Exit 0

4) Errors:
   - Let SQLAlchemy errors bubble to handlers:
       * IntegrityError -> ConflictError (exit 69)
       * OperationalError -> DBConnectionError (exit 65)
       * ProgrammingError -> DBOperationError (exit 65)
   - Unknown -> UnknownError (exit 1)

Input validation
----------------
- Reject empty org name (after stripping) early with ValueError BEFORE DB work.
  The CLI may either:
    a) raise and rely on handlers to map ValueError → ValidationError (exit 64), or
    b) explicitly map to ValidationError itself and call handle_cli_error.
  (Choose one consistent approach; (a) is simpler.)

Determinism & idempotence
-------------------------
- Re-running --apply with the same inputs must not create duplicates.
- --dry-run and --apply must agree on the proposed actions.

Output examples (human)
-----------------------
- Dry run:
    "seed-data: would insert organisation 'Whiteline Demo' (slug=whiteline-demo)"
    "seed-data: would update organisation 'Whiteline Demo' (slug: old->new)"
    "seed-data: no changes (skipped=1)"
- Apply:
    "seed-data: inserted=1 updated=0 skipped=0 organisation='Whiteline Demo' id=<uuid> slug=whiteline-demo"

Dependencies (explicit)
-----------------------
- app.config.settings.get_settings
- app.config.logging_config.configure_logging
- app.utils.logging_tools.{new_trace_id, with_trace_id}
- app.db.session.{SessionLocal or get_session}
- app.db.seed.seed_minimal
- app.repositories.organisation_repository.OrganisationRepository
- app.schemas.organisation.OrganisationInDTO / slug normalizer (for dry-run preview)
- app.errors.handlers.{wrap_cli_main, handle_cli_error}

Testing notes
-------------
- Dry-run prints expected action with no DB writes.
- Apply path is idempotent: first run inserts, second run skips.
- IntegrityError surfaces on duplicate unique keys when inputs conflict.
- Duration_ms can be included in the INFO summary if trivially measurable.

Non-goals (v1)
--------------
- No JSON output flag; human-readable is enough (structured logs already exist).
- No multi-entity seed plans from the CLI (single org is sufficient in v1).
===============================================================================
"""
