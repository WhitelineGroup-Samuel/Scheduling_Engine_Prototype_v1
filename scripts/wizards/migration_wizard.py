#!/usr/bin/env python3
"""
scripts/wizards/migration_wizard.py — Interactive migration creator/applier

Flow:
  1) Prompt for revision message
  2) make migrate-new msg="..."
  3) Detect the new file in migrations/versions and print a clickable path
  4) Ask for approval:
      - If NO: delete the new file and exit
      - If YES: ask where to apply (1=dev, 2=test, 3=all) and run the Make target(s)
  5) Show current heads (make migrate-head)
  6) Prompt to quit

Notes:
  - Expects to be run from repo root (or we cd into repo root).
  - Uses your Makefile targets so behaviour stays consistent.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from subprocess import CompletedProcess


def find_repo_root(start: Path) -> Path:
    """Walk upward until we find a Makefile; fallback to two levels up."""
    p = start
    for _ in range(5):  # don't walk forever
        if (p / "Makefile").exists():
            return p
        p = p.parent
    # Fallback: assume two levels up from scripts/wizards/
    return start.parents[2]


REPO_ROOT = find_repo_root(Path(__file__).resolve())
VERSIONS_DIR = REPO_ROOT / "migrations" / "versions"

print(f"[wizard] repo root: {REPO_ROOT}")


def run(label: str, cmd: list[str] | str, check: bool = True, capture: bool = False) -> CompletedProcess[str]:
    print(f"\n\033[1m{label}\033[0m")
    cp: CompletedProcess[str]
    if isinstance(cmd, list):
        print("$", " ".join(shlex.quote(p) for p in cmd))
        cp = subprocess.run(cmd, cwd=REPO_ROOT, check=False, capture_output=capture, text=True)
        return cp
    else:
        print("$", cmd)
        cp = subprocess.run(cmd, cwd=REPO_ROOT, shell=True, check=False, capture_output=capture, text=True)  # noqa S602
        return cp


def prompt_non_empty(prompt: str) -> str:
    while True:
        try:
            msg = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline
            sys.exit(1)
        if msg:
            return msg
        print("Please enter a non-empty message.")


def prompt_yes_no(prompt: str) -> bool:
    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in {"y", "yes"}


def before_file_set() -> set[Path]:
    if not VERSIONS_DIR.exists():
        VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return set(p for p in VERSIONS_DIR.glob("*.py"))


def newest(paths: Iterable[Path]) -> Path | None:
    paths = list(paths)
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


def choose_apply_target() -> str | None:
    print("\nWhere do you want to apply this migration?")
    print("  1 = Dev")
    print("  2 = Test")
    print("  3 = All")
    print("  Q = Quit without applying")
    while True:
        try:
            ans = input("Choice [1/2/3/Q]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if ans in {"1", "2", "3", "q", ""}:
            if ans in {"", "q"}:
                return None
            return {"1": "migrate-dev", "2": "migrate-test", "3": "migrate-all"}[ans]
        print("Please enter 1, 2, 3, or Q.")


def main() -> int:
    print("=== Migration Wizard ===")

    # 1) Ask for the message
    msg = prompt_non_empty("Enter migration message: ")

    # Snapshot files before
    before = before_file_set()

    # 2) Create revision via Make target
    cp = run("Create revision (autogenerate)", ["make", "migrate-new", f"msg={msg!s}"], check=False)
    if cp.returncode != 0:
        print("\n\033[31mAlembic revision failed.\033[0m")
        return cp.returncode

    # 3) Detect the new file
    after = set(p for p in VERSIONS_DIR.glob("*.py"))
    created = list(after - before)
    mig_file: Path | None
    if len(created) == 1:
        mig_file = created[0]
    else:
        # Fallback: pick newest file
        mig_file = newest(after)

    if not mig_file:
        print("\n\033[31mCould not find a generated migration file in migrations/versions.\033[0m")
        return 1

    print("\nGenerated migration:")
    print(str(mig_file.resolve()))  # VS Code will make this clickable

    # 4) Approval prompt
    if not prompt_yes_no("\nOpen and review the file. Are you happy with it? [Y/N]: "):
        try:
            mig_file.unlink()
            print(f"Deleted: {mig_file}")
        except Exception as e:
            print(f"Warning: failed to delete {mig_file}: {e}")
        print("Cancelled. Exiting.")
        return 0

    # 5) Choose where to apply
    target = choose_apply_target()
    if target is None:
        print("Not applying. Exiting.")
        return 0

    # 6) Apply
    rc = run(f"Apply: make {target}", ["make", target], check=False).returncode
    if rc != 0:
        print("\n\033[31mApply failed.\033[0m")
        return rc

    # 7) Show heads
    run("Current heads (dev & test)", ["make", "migrate-head"], check=False)

    # 8) Quit prompt
    try:
        input("\nPress ENTER (or Q) to quit: ")
    except (EOFError, KeyboardInterrupt):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
