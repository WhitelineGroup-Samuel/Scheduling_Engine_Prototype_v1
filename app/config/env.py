"""
===============================================================================
File: app/config/env.py
Purpose:
  Load .env and provide helpers to parse environment variables consistently.

Responsibilities:
  - Load .env with python-dotenv if present.
  - Expose helpers: env_str, env_int, env_bool, env_list (with defaults & casting).
  - Validate presence of required keys early (raise ConfigError).

Collaborators:
  - app.errors.exceptions.ConfigError
  - app.config.constants for well-known keys.

Testing:
  - Unit tests for parsing/validation edge cases.
===============================================================================
"""
