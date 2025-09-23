"""
===============================================================================
File: app/cli/main.py
Purpose:
  Define the Typer/Click application and register subcommands.

Responsibilities:
  - app = Typer()
  - app.add_typer(check_env.app, name="check-env") etc.
  - Provide global options (e.g., --config, --verbose)

Collaborators:
  - app.config.settings, app.errors.handlers
===============================================================================
"""
