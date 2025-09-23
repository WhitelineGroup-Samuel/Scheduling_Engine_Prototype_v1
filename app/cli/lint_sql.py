"""
===============================================================================
File: app/cli/lint_sql.py
Purpose:
  Run sqlfluff (or similar) on /sql directory and report violations.

Responsibilities:
  - Shell out to sqlfluff or invoke programmatically.
  - Return non-zero exit on lint failures.

Collaborators:
  - app.config.paths.SQL_DIR
===============================================================================
"""