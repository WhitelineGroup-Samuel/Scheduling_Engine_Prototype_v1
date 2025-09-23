"""
===============================================================================
File: app/cli/check_env.py
Purpose:
  Validate required environment variables and print a status report.

Responsibilities:
  - Verify presence & types; print missing keys.
  - Exit non-zero on failure.

Collaborators:
  - app.config.env, app.config.settings, app.errors.exceptions.ConfigError
===============================================================================
"""
