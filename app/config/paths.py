"""
===============================================================================
File: app/config/paths.py
Purpose:
  Resolve project-relative paths (repo root, logs, migrations, sql, etc.)
  in a single place to avoid ad-hoc path joins.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
LOG_DIR: Path = REPO_ROOT / "logs"
MIGRATIONS_DIR: Path = REPO_ROOT / "migrations"
SQL_DIR: Path = REPO_ROOT / "scripts"


def ensure_dirs() -> None:
    """Ensure key configuration directories exist."""

    for directory in (LOG_DIR, MIGRATIONS_DIR, SQL_DIR):
        directory.mkdir(parents=True, exist_ok=True)


__all__ = ["REPO_ROOT", "LOG_DIR", "MIGRATIONS_DIR", "SQL_DIR", "ensure_dirs"]
