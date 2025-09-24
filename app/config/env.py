"""
===============================================================================
File: app/config/env.py
Purpose
-------
Consistently load environment variables from `.env` files in **development/test**
ONLY, and provide thin helpers for parsing. Production must rely solely on the
process environment (no .env loading).

Public API (Codex must implement)
---------------------------------
- def load_dotenv_for_env(app_env: str, *, test_mode: bool = False) -> None:
    Behavior:
      - If app_env in {"dev", "test"}:
          * Prefer `.env.test` when test_mode=True (pytest sets), else `.env`.
          * Use python-dotenv if available; if not present, no-op.
      - If app_env == "prod": NO-OP (strict).

- Optional helper parsers (used rarely because Pydantic Settings handles parsing):
    env_bool(key, default=False), env_int(key, default=None), etc.

Error handling
--------------
- Do NOT raise if file missing; this loader is best-effort for convenience.
- Validation of required keys happens in app.config.settings (ConfigError).

Used by
-------
- run.py at startup (Phase H Step 16): load only for dev/test; not for prod.
- pytest bootstrap (if necessary).

Testing
-------
- Unit tests can simulate presence/absence of .env.test and assert that values
  are visible to pydantic settings afterwards.
===============================================================================
"""
