"""
===============================================================================
File: app/errors/handlers.py
Purpose:
  Map exceptions to exit codes and structured log messages.

Responsibilities:
  - handle_exception(exc: Exception) -> exit_code:int
  - log_and_format(exc) utilities

Collaborators:
  - app.errors.codes

Used by:
  - run.py, manage.py/CLI commands
===============================================================================
"""