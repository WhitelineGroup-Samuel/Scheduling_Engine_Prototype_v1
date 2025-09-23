"""
===============================================================================
Package: app.config
Purpose:
  Centralized configuration access. Exposes get_settings() as the canonical
  way to retrieve app settings across the codebase.

Exports:
  - get_settings(): returns a singleton Settings object (pydantic BaseSettings).

Collaborators:
  - .env (loaders), .settings (Settings model), .logging_config, .paths

Testing:
  - Ensure repeated calls return the same memoized Settings instance.
===============================================================================
"""