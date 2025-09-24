"""
===============================================================================
File: app/errors/handlers.py
Purpose
-------
Normalize arbitrary exceptions to our `AppError` types, log them with structured
context (trace_id, code, severity), and return deterministic CLI/process exit
codes. Used by both CLI commands and the top-level `run.py` entrypoint.

Public API (Codex must implement)
---------------------------------
- def map_exception(err: BaseException) -> "AppError":
    Map vendor exceptions to domain errors (see Phase F Step 14 table). Default:
    wrap in UnknownError(message=str(err), context={"type": err.__class__.__name__}).

- def handle_cli_error(err: BaseException, logger) -> int:
    Normalize (via map_exception unless err is already AppError),
    log exactly ONE structured line at appropriate level, then
    return `app_err.exit_code`. Use exc_info=True for CRITICAL/Unknown only.

- def wrap_cli_main(func):
    Decorator for Typer/Click command entrypoints:
      try: return func(...)
      except BaseException as err:
          code = handle_cli_error(err, logger)
          raise SystemExit(code)

- def level_for(severity: str) -> int
- def exc_info_for(app_err: "AppError") -> bool

Logging contract
----------------
- One line per handled exception; JSON vs human selected by logging config.
- Include extras: code, exit_code, severity, and safe `context` keys.
- `trace_id` is injected by logging filters (Step 13).

Integration with run.py (Phase H Step 16)
-----------------------------------------
- `run.py` wraps its `main()` with a try/except and calls `handle_cli_error(...)`
  on failure, then exits with the returned code.
- Exit codes align with ErrorCode catalog (config=78, db=65, timeout=75, unknown=1).

Safety
------
- Never include secrets in messages or context (DB passwords, tokens).
- Prefer `exc_info=False` for expected errors (Validation/Conflict/NotFound).
===============================================================================
"""
