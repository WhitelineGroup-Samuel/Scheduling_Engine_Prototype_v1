"""
===============================================================================
File: app/cli/diag.py
Purpose:
  Print environment diagnostics: Python version, paths, DB ping, settings
  summary (sanitized), and migration head status.

Responsibilities:
  - Compose a table-like output for developer clarity.

Collaborators:
  - app.db.healthcheck, app.config.settings, app.config.paths
===============================================================================
"""
