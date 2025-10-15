#!/usr/bin/env python3
"""
scripts/wizards/db_wizard.py — Interactive DB startup wizard (Python version of `make db-begin`)

What it does:
  1) docker compose up -d ; docker compose ps
  2) psql smoke tests against dev & test
  3) show Alembic head for dev/test using your venv's interpreter
  4) prompt to open Postgres logs (opens macOS Terminal window if available)

Requirements:
  - docker + docker compose
  - psql client
  - Your .venv is active when you run this (so alembic resolves correctly)
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# --- Config (kept consistent with your Makefile) ---
DB_SERVICE = "db"
CONTAINER = "scheduling_postgres"
COMPOSE = ["docker", "compose"]
PSQL_DEV = "postgresql://scheduler_user:myschedulerpass@127.0.0.1:5432/scheduling_dev"
PSQL_TEST = "postgresql://scheduler_user:myschedulerpass@127.0.0.1:5432/scheduling_test"

REPO_ROOT = Path(__file__).resolve().parents[1]  # repo root (../.. from scripts/)
PYTHON = sys.executable or "python3"  # use current venv interpreter


def run(label: str, cmd: list[str] | str, check: bool = True, env: dict[str, str] | None = None) -> int:
    """Run a command, streaming output. Accepts list or shell string."""
    print(f"\n\033[1m{label}\033[0m")
    if isinstance(cmd, list):
        print("$", " ".join(shlex.quote(p) for p in cmd))
        proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    else:
        print("$", cmd)
        proc = subprocess.run(cmd, cwd=REPO_ROOT, shell=True, env=env)  # noqa: S602
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def compose(*args: str) -> int:
    return run("docker compose " + " ".join(args), [*COMPOSE, *args])


def psql(url: str, sql: str) -> int:
    return run(f"psql -> {url}", ["psql", url, "-c", sql])


def alembic_current(app_env: str) -> int:
    # Use venv python so Alembic resolves in the same environment
    env = os.environ.copy()
    env["APP_ENV"] = app_env
    return run(f"Alembic current ({app_env})", [PYTHON, "-m", "alembic", "-x", f"env={app_env}", "current"], env=env)


def has_osascript() -> bool:
    return shutil.which("osascript") is not None


def open_logs_in_new_terminal() -> None:
    """
    macOS: open a NEW Terminal window that tails docker logs for the DB service.
    Falls back to tail logs in current terminal if AppleScript isn't available.
    """
    if not has_osascript():
        print("osascript not found; following logs here.")
        compose("logs", "-f", DB_SERVICE)
        return

    # Build an AppleScript that cd's into the repo and tails logs
    repo = str(REPO_ROOT)
    # Use single quotes around repo and escape any single quotes
    safe_repo = repo.replace("'", "'\\''")
    script = f"""
        tell application "Terminal"
            do script "cd '{safe_repo}' && docker compose logs -f {shlex.quote(DB_SERVICE)}"
            activate
        end tell
    """
    run("Open logs in new macOS Terminal window", ["osascript", "-e", script], check=False)


def prompt_yes_no(prompt: str) -> bool:
    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()  # newline
        return False
    return ans in {"y", "yes"}


def main() -> int:
    print("=== Starting Postgres stack (Python wizard) ===")

    # 1) Up + ps
    compose("up", "-d")
    compose("ps")

    # 2) Status: psql smoke tests
    psql(PSQL_DEV, "select current_database(), current_user;")
    psql(PSQL_TEST, "select current_database(), current_user;")

    # 3) Alembic heads
    alembic_current("dev")
    alembic_current("test")

    # 4) Prompt for logs
    if prompt_yes_no("\nShow Postgres logs now? [Y/N]: "):
        open_logs_in_new_terminal()
    else:
        print("OK, not showing logs. Done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
