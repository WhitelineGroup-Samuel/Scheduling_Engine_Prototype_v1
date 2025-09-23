"""
===============================================================================
File: app/config/paths.py
Purpose:
  Resolve project-relative paths (repo root, logs, migrations, sql, etc.)
  in a single place to avoid ad-hoc path joins.

Responsibilities:
  - Provide functions/constants like REPO_ROOT, LOG_DIR, MIGRATIONS_DIR, SQL_DIR.
  - Create directories on demand (e.g., LOG_DIR exists).

Collaborators:
  - app.config.settings for overrides (optional).

Notes:
  - Use pathlib.Path; avoid os.path.
===============================================================================
"""