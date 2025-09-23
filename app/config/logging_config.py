"""
===============================================================================
File: app/config/logging_config.py
Purpose:
  Configure Python logging via dictConfig (console + rotating file handler).
  Support JSON logs optionally; include trace/request IDs hooks.

Responsibilities:
  - build_logging_dict(settings) -> dict
  - configure_logging(settings) -> None

Collaborators:
  - app.utils.logging_tools (context vars/formatters)
  - app.config.paths.LOG_DIR for file outputs

Notes:
  - Ensure idempotency: safe to call multiple times.
===============================================================================
"""
