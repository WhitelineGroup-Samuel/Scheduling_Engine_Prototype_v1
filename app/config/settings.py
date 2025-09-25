"""
===============================================================================
File: app/config/settings.py
Purpose
-------
Single source of truth for configuration (Pydantic BaseSettings). Consumed by
logging, DB engine/session creation, CLI, and run.py.

What Codex must implement
-------------------------
Model
- class Settings(BaseSettings)
    Fields (non-exhaustive; include at least these):
      APP_NAME: str = "scheduling-engine"
      APP_VERSION: str = "0.1.0"         # may be overridden from package metadata
      APP_ENV: Literal["dev","test","prod"]  # required; validate enum
      LOG_LEVEL: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"] = "INFO"
      LOG_JSON: bool = False
      TIMEZONE: str = "Australia/Melbourne"

      # Database (compose if DATABASE_URL missing)
      DATABASE_URL: str | None = None
      DB_HOST: str | None = "localhost"
      DB_PORT: int | None = 5432
      DB_NAME: str | None = None
      DB_USER: str | None = None
      DB_PASSWORD: str | None = None

      # Derived / convenience
      @property
      def effective_database_url(self) -> str:  # prefer DATABASE_URL else compose
          ...

Validation rules
----------------
- If DATABASE_URL provided → prefer it (must be non-empty).
- Else, require all parts (USER/PASSWORD/HOST/PORT/NAME) to compose URL.
- Validate enums for APP_ENV/LOG_LEVEL; coerce LOG_JSON from common truthy/falsey.
- No secrets included in __repr__/__str__.

Load order & precedence
- Defaults < .env (dev/test only) < OS environment variables (always highest).
- In prod, the app should not load `.env` (handled in env loader module).

Used by logging (Phase F Step 13)
- LOG_JSON selects JSON vs human formatter.
- LOG_LEVEL sets root level.
- APP_ENV/APP_NAME/APP_VERSION used by StaticFieldsFilter injection.

Top-level run behavior specifics
-------------------------
- `run.py` calls a canonical `get_settings()` factory (Codex to provide) ONCE.
- `run.py` may override log format/level per flags; settings remain read-only.

Testing
- Unit tests assert default values, overrides via env, and URL composition.
- Smoke test asserts `settings.APP_ENV == "test"` in test runs and that booleans parse.

Collaborators
-------------
- app.config.env: optional dotenv loader for dev/test.
- app.config.logging_config: consumes LOG_* and APP_* fields.

Non-goals
---------
- No secret manager client here; in prod, rely on OS env or the platform to inject secrets.

===============================================================================
"""
