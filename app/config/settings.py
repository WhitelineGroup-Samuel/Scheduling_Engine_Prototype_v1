"""
===============================================================================
File: app/config/settings.py
Purpose:
  Canonical pydantic BaseSettings model. Defines all tunable configuration,
  reads from env, and provides computed properties (e.g., SQLAlchemy URL opts).

Key Fields (examples):
  - APP_NAME, APP_ENV (dev/test/prod), DEBUG
  - LOG_LEVEL, LOG_JSON, LOG_DIR
  - DATABASE_URL (PostgreSQL), DB_ECHO, DB_POOL_SIZE, DB_SSL_MODE
  - TIMEZONE (e.g., Australia/Melbourne)

Responsibilities:
  - Validation: ensure DATABASE_URL shape, allowed APP_ENV, etc.
  - Provide @cached_property for derived paths (uses app.config.paths).

Collaborators:
  - app.config.env for env loading
  - app.errors.exceptions.ConfigError on invalid config

Testing:
  - Verify defaults, overrides, and .env precedence.
===============================================================================
"""
