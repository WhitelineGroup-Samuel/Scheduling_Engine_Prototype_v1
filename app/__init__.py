"""
===============================================================================
Package: app
File: app/__init__.py
Purpose:
  Root package initializer for the Scheduling Engine back-end. Provides a clean,
  import-safe entry surface (version metadata, lazy settings accessor, and
  optional convenience exports) without performing heavy side effects at import
  time.

Responsibilities:
  - Define package metadata (e.g., __version__, __description__).
  - Expose convenience accessors (e.g., get_settings) via lazy imports to avoid
    import cycles and unnecessary startup work.
  - Optionally define __all__ to present a stable, minimal API to callers.
  - Guarantee *no* network/filesystem side effects during import (logging,
    DB connections, dotenv loading, etc. should occur in run.py / manage.py).

Must Include:
  - __version__: str — semantic version for the package skeleton (e.g., "0.1.0").
  - __description__: short human-readable description.
  - def get_settings():
      Lazy import `from app.config.settings import get_settings` INSIDE the function
      and return the result. This avoids cycles and heavy imports at package import.
  - Optional short-hands to frequently used items that are side-effect free
    (e.g., error classes). Keep this list intentionally small.

Import/Export Contracts:
  - External modules may safely do:
      from app import get_settings, __version__
    without triggering logging/DB configuration.
  - DO NOT: initialize logging, parse .env, create engines/sessions here.
    Those happen in:
      - app.config.env / app.config.settings (loaded explicitly by callers)
      - app.config.logging_config.configure_logging(...)
      - app.db.engine.get_engine(...)

Collaborators:
  - app.config.settings (for get_settings())
  - app.errors.exceptions (optional re-exports)
  - app.errors.codes (optional re-exports)

Used by
-------
  - Banners/diagnostics in run.py and CLI.
  - Tests may import `app` to assert metadata and lazy behavior.

Side-Effects Policy:
  - This file must remain side-effect free:
      * No reading environment variables at import time
      * No file system creation (logs/, migrations/)
      * No logging configuration
      * No database connections

Testing:
  - tests/test_smoke.py should import `app` and verify:
      * __version__ is a non-empty string
      * get_settings() returns a settings object and is memoized by the config
  - Ensure importing `app` alone neither configures logging nor opens DB
    connections (can be asserted by monkeypatching and import timing).

Notes:
  - If you need a global "package-level" constant later, prefer to colocate it
    with its domain module and re-export here (sparingly) to keep `app/__init__`
    stable and cycle-free.
===============================================================================
"""
