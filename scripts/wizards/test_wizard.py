#!/usr/bin/env python3
"""
scripts/wizards/test_wizard.py — Interactive “Quality / Tests / Pre-commit” wizard.

Menu:
  1) QUALITY CHECKS
     - Creates reports/YYYY/MM/DD/<HH-MM-SS>_quality_report.txt
     - Runs ruff (two-pass to detect autofix vs remaining), black --check --diff, mypy, pyright
     - Prints brief status to terminal and writes detailed sections to the report
  2) PYTESTS
     - Submenu: 1=All (make test-report-detailed), 2=Unit (make test-unit), 3=Integration (make test-int)
     - Loop until user quits
  3) PRE-COMMIT CHECKS
     - Runs: make pre-commit-suite

Notes:
  - Runs from repo root (we auto-detect it by locating the Makefile).
  - Assumes your .venv is already active (profile takes care of that).
"""

from __future__ import annotations

import os
import re
import select
import shlex
import shutil
import string
import subprocess
import sys
import threading
import time
from typing import Literal
from collections.abc import Sequence, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# ------------------------------------------------------------------------------
# Repo root detection
# ------------------------------------------------------------------------------


def find_repo_root(start: Path) -> Path:
    p = start
    for _ in range(6):
        if (p / "Makefile").exists():
            return p
        p = p.parent
    # Fallback: two levels up from scripts/wizards/
    return start.parents[2]


REPO_ROOT = find_repo_root(Path(__file__).resolve())
print(f"[wizard] repo root: {REPO_ROOT}")

# ------------------------------------------------------------------------------
# Shell helpers
# ------------------------------------------------------------------------------

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"


def relpath_str(p: str | Path) -> str:
    """Return repo-relative path if possible, else the original string."""
    try:
        pp = Path(p).resolve()
        return str(pp.relative_to(REPO_ROOT))
    except Exception:
        return str(p)


def osc8_link(label: str, p: Path) -> str:
    """Clickable hyperlink for terminals that support OSC 8 (VS Code terminal does)."""
    url = p.resolve().as_uri()  # file:///… path
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


@dataclass
class CmdResult:
    rc: int
    out: str
    err: str


def run_cmd(label: str, cmd: Sequence[str] | str, cwd: Path | None = None, echo: bool = True) -> CmdResult:
    """Run a command; return rc/out/err; never raise. Prints output only when echo=True."""
    if cwd is None:
        cwd = REPO_ROOT
    if echo:
        print(f"\n{BOLD}{label}{RESET}")
        if isinstance(cmd, str):
            print("$", cmd)
        else:
            print("$", " ".join(shlex.quote(s) for s in cmd))
    cp = subprocess.run(
        cmd,
        cwd=cwd,
        shell=isinstance(cmd, str),
        text=True,
        capture_output=True,
        check=False,
    )
    if echo and cp.stdout:
        prev = cp.stdout if len(cp.stdout) < 4000 else (cp.stdout[:3800] + "\n... [truncated]\n")
        if prev.strip():
            print(prev.rstrip())
    if echo and cp.stderr:
        prev_err = cp.stderr if len(cp.stderr) < 2000 else (cp.stderr[:1800] + "\n... [truncated]\n")
        if prev_err.strip():
            print(prev_err.rstrip(), file=sys.stderr)
    return CmdResult(cp.returncode, cp.stdout, cp.stderr)


def have_precommit() -> bool:
    return shutil.which("pre-commit") is not None and (REPO_ROOT / ".pre-commit-config.yaml").exists()


def run_precommit_hook(hook: str, extra_args: list[str] | None = None) -> CmdResult:
    args = ["pre-commit", "run", hook, "--all-files", "-v"]
    if extra_args:
        args.extend(extra_args)
    return run_cmd(f"pre-commit ({hook})", args, echo=False)


def run_precommit_hook_spinner(hook: str, label: str, extra_args: list[str] | None = None) -> CmdResult:
    """Run a single pre-commit hook with the spinner and return captured output."""
    args = ["pre-commit", "run", hook, "--all-files", "-v"]
    if extra_args:
        args.extend(extra_args)
    return run_with_spinner(label, args)


ANSI_RE = re.compile("\x1b\\[[0-9;]*[mK]|\x1b\\]8;;.*?\x1b\\\\|\x1b\\]8;;\x1b\\\\")


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def run_with_spinner(label: str, cmd: Sequence[str] | str, cwd: Path | None = None, env: dict[str, str] | None = None) -> CmdResult:
    """
    Run a command capturing output while showing a single-line spinner that disappears when done.
    Never prints the command output; returns it as CmdResult.
    """
    if cwd is None:
        cwd = REPO_ROOT

    done = threading.Event()
    spinner_frames = ["|", "/", "-", "\\"]
    line_text = f"{label}"

    def spin() -> None:
        i = 0
        while not done.is_set():
            frame = spinner_frames[i % len(spinner_frames)]
            print(f"\r{frame} {line_text}", end="", flush=True)
            i += 1
            time.sleep(0.12)
        # clear the spinner line
        clear = " " * (len(line_text) + 4)
        print(f"\r{clear}\r", end="", flush=True)

    t = threading.Thread(target=spin, daemon=True)
    t.start()
    try:
        cp = subprocess.run(
            cmd,
            cwd=cwd,
            shell=isinstance(cmd, str),
            text=True,
            capture_output=True,
            check=False,
            env=env or os.environ.copy(),
        )
    finally:
        done.set()
        t.join()

    return CmdResult(cp.returncode, cp.stdout, cp.stderr)


@contextmanager
def spinner_line(message: str) -> Iterator[None]:
    """
    Show a single spinner line with `message` until the with-block finishes,
    then erase the line.
    """
    done = threading.Event()
    spinner_frames = ["|", "/", "-", "\\"]
    line_text = message

    def spin() -> None:
        i = 0
        while not done.is_set():
            frame = spinner_frames[i % len(spinner_frames)]
            print(f"\r{frame} {line_text}", end="", flush=True)
            i += 1
            time.sleep(0.12)
        clear = " " * (len(line_text) + 4)
        print(f"\r{clear}\r", end="", flush=True)

    t = threading.Thread(target=spin, daemon=True)
    t.start()
    try:
        yield
    finally:
        done.set()
        t.join()


def drain_stdin(timeout: float = 0.0) -> None:
    """
    Non-blocking drain of any pending input on stdin. This swallows stray
    escape sequences that can appear when VS Code opens/moves the terminal.
    """
    try:
        while True:
            r, _, _ = select.select([sys.stdin], [], [], timeout)
            if not r:
                break
            # Read a line (or whatever is pending) and discard.
            _ = sys.stdin.readline()
            # After the first read, keep draining without waiting.
            timeout = 0.0
    except Exception:
        # Be conservative: if anything goes wrong, just stop draining.
        pass


def sanitize_answer(s: str) -> str:
    """
    Keep only printable ASCII (plus space), lower-case & strip.
    This drops ANSI escape codes and other control chars.
    """
    allowed = set(string.printable)  # includes digits/letters/punct/space
    clean = "".join(ch for ch in s if ch in allowed)
    return clean.strip().lower()


def read_choice(prompt: str, valid: set[str], allow_blank: bool = True) -> str | None:
    """
    Prompt for a choice; ignore junk until a valid entry is provided.
    Returns the (sanitized) choice, or None on EOF/KeyboardInterrupt.
    """
    while True:
        try:
            drain_stdin(0.0)  # swallow any pending noise
            raw = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        ans = sanitize_answer(raw)
        if ans == "" and allow_blank:
            return ""
        if ans in valid:
            return ans
        print(f"Please enter one of: {', '.join(sorted(valid))}" + (", or blank" if allow_blank else ""))


# ------------------------------------------------------------------------------
# Report helpers
# ------------------------------------------------------------------------------


def now_parts() -> tuple[str, str, Path]:
    ts = datetime.now()
    ddir = Path("reports") / f"{ts:%Y}" / f"{ts:%m}" / f"{ts:%d}"
    fname = f"{ts:%H-%M-%S}_quality_report.md"
    return ts.strftime("%d/%m/%Y"), ts.strftime("%H:%M:%S"), (REPO_ROOT / ddir / fname)


def make_report_path(kind: Literal["quality", "pytest", "precommit"]) -> tuple[str, str, Path]:
    """
    Like now_parts() but choose filename per report type.
    """
    ts = datetime.now()
    ddir = Path("reports") / f"{ts:%Y}" / f"{ts:%m}" / f"{ts:%d}"
    suffix = "_quality_report.md" if kind == "quality" else "_test_report.md" if kind == "pytest" else "_pre_commit_report.md"
    fname = f"{ts:%H-%M-%S}{suffix}"
    return ts.strftime("%d/%m/%Y"), ts.strftime("%H:%M:%S"), (REPO_ROOT / ddir / fname)


def write_report_header_generic(path: Path, report_type: str, date_str: str, time_str: str, repo_root: Path, extra_fields: dict[str, str]) -> None:
    """
    Generic header:
      # CODEBASE REPORT
      **REPORT TYPE:** <type>
      **DATE:** <...>
      **TIME:** <...>
      **REPO:** <...>
      **KEY:** value ...
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# CODEBASE REPORT\n")
        f.write(f"**REPORT TYPE:** {report_type}\n\n")
        f.write(f"**DATE:** {date_str}  \n")
        f.write(f"**TIME:** {time_str}  \n")
        f.write(f"**REPO:** {repo_root}  \n")
        for k, v in extra_fields.items():
            f.write(f"**{k}:** {v}\n")
        f.write("\n")


def append_section_md(path: Path, title: str, content: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n")
        if content.strip():
            f.write(content.rstrip() + "\n")
        else:
            f.write("(no output)\n")


def append_h1_md(path: Path, title: str, content: str = "") -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n# {title}\n")
        if content.strip():
            f.write(content.rstrip() + "\n")


def build_quality_summary_compact(ruff_sum: str, black_sum: str, mypy_sum: str) -> str:
    # two spaces at end of first two lines force single line breaks in markdown
    return "\n".join(
        [
            f"**RUFF:** {ruff_sum}  ",
            f"**BLACK:** {black_sum}  ",
            f"**MYPY:** {mypy_sum}",
        ]
    )


def build_pytest_counts_md(passed_n: int, failed_n: int, skipped_n: int) -> str:
    return "\n".join(
        [
            f"**PASSED:** {passed_n}  ",
            f"**FAILED:** {failed_n}  ",
            f"**SKIPPED:** {skipped_n}",
        ]
    )


def summary_count_line(label: str, count: int, width: int = 69) -> str:
    dots = "." * max(1, width - len(label) - len(str(count)))
    return f"{label}{dots}{count}"


def section_status_line(tool: str, status: str) -> None:
    print(f"{tool}: {status}")


def write_summary_md(path: Path, ruff_sum: str, black_sum: str, mypy_sum: str) -> None:
    lines = [
        "## SUMMARY",
        f"ruff.....................................................................{ruff_sum}  ",
        f"black....................................................................{black_sum}  ",
        f"mypy.....................................................................{mypy_sum}  ",
        "",
    ]
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_quality_summary_compact_md(path: Path, ruff_sum: str, black_sum: str, mypy_sum: str) -> None:
    append_section_md(path, "SUMMARY", build_quality_summary_compact(ruff_sum, black_sum, mypy_sum))


def list_python_files() -> list[Path]:
    # Prefer Git if available (respects .gitignore)
    if shutil.which("git"):
        cp = subprocess.run(["git", "ls-files", "*.py"], text=True, capture_output=True)
        files = [REPO_ROOT / p for p in cp.stdout.splitlines() if p.strip()]
        if files:
            return files
    # Fallback: walk the tree but skip common dirs
    skip_dirs = {".venv", ".git", ".mypy_cache", ".ruff_cache", ".pytest_cache", "node_modules", "dist", "build"}
    out: list[Path] = []
    for root, dirs, fnames in os.walk(REPO_ROOT):
        # prune
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for n in fnames:
            if n.endswith(".py"):
                out.append(Path(root) / n)
    return out


def color_status(s: str) -> str:
    s_up = s.upper()
    if s_up in {"PASSED", "SUCCESS"}:
        return f"{GREEN}{s}{RESET}"
    if s_up in {"FAILED", "FAILURE"}:
        return f"{RED}{s}{RESET}"
    return f"{YELLOW}{s}{RESET}"  # SKIPPED/etc.


def summary_line(label: str, status: str, width: int = 69) -> str:
    plain_status = status  # visible text (color codes don't count for width)
    dots = "." * max(1, width - len(label) - len(plain_status))
    return f"{label}{dots}{color_status(plain_status)}"


# ------------------------------------------------------------------------------
# QUALITY CHECKS
# ------------------------------------------------------------------------------


def ruff_check(total_files: int) -> tuple[str, str]:
    """
    Use the pre-commit ruff hook (with --fix per your config).
    - If diagnostics remain (file:line:col: CODE msg), report FAILED and list details.
    - If only modifications happened (no remaining diagnostics), treat as PASSED with Auto-Fixes Applied.
    - If nothing to do, PASSED (0).
    """
    if not have_precommit():
        return "SKIPPED", "SKIPPED: pre-commit is not installed or .pre-commit-config.yaml missing."

    res = run_precommit_hook("ruff")
    text = (res.out or "") + "\n" + (res.err or "")

    # Collect remaining diagnostics (after --fix) if any.
    diag_re = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+):\s*(?P<code>[A-Z]+\d+)\s+(?P<msg>.+)$")

    per_file: dict[str, list[tuple[int, int, str, str]]] = {}
    for ln in text.splitlines():
        m = diag_re.match(ln.strip())
        if m:
            fn = m.group("file")
            line = int(m.group("line"))
            col = int(m.group("col"))
            code = m.group("code")
            msg = m.group("msg").strip()
            per_file.setdefault(fn, []).append((line, col, code, msg))

    remaining = sum(len(v) for v in per_file.values())

    # Heuristics to count/ack auto-fixes (pre-commit prints this line when files change).
    modified_hint = "Files were modified by this hook" in text
    fixed_count = 0
    for mm in re.finditer(r"Fixed\s+(\d+)\s+errors?", text, re.IGNORECASE):
        fixed_count += int(mm.group(1))

    if remaining > 0:
        # FAILED — show files + per-file diagnostics
        lines = [
            f"**FAILED** - {remaining} remaining issues (_checked {total_files} source files_)",
            "",
            "**The Failed Scripts:**",
        ]
        for fn, items in per_file.items():
            lines.append(f"- {relpath_str(fn)}: _{len(items)} Errors_")
        lines.append("")

        by_file = list(per_file.items())
        for i, (fn, issues) in enumerate(by_file):
            if i:
                lines.append("\n---\n")
            short = Path(fn).name
            lines.append(f"### {short}")
            for line, col, code, msg in issues:
                lines.append(f"**{relpath_str(fn)}: Ln {line}, Col {col}**  ")
                lines.append(f"{msg} ({code})\n")

        return "FAILED", "\n".join(lines)

    # No remaining diagnostics
    if res.rc == 0 and not modified_hint and fixed_count == 0:
        # Clean, nothing changed
        title = f"**PASSED** - {total_files} source files checked; Auto-Fixes Applied = 0"
        return "PASSED", title

    # Modified files but no remaining issues — treat as PASSED with fixes
    applied = fixed_count if fixed_count > 0 else "≥1"
    title = f"**PASSED** - {total_files} source files checked; Auto-Fixes Applied = {applied}"
    details = [title]
    if fixed_count > 0:
        details.append("")
        details.append(f"(Ruff reported: Fixed {fixed_count} errors)")
    return "PASSED", "\n".join(details)


def black_check(total_files: int) -> tuple[str, str]:
    """
    Use the pre-commit black hook for parity. We treat 'files were modified' as
    PASSED with Auto-Fixes Applied = <count>, listing files. Otherwise PASSED.
    Non-formatting failures -> FAILED with raw output snippet.
    """
    if not have_precommit():
        # Fallback: SKIPPED
        return "SKIPPED", "SKIPPED: pre-commit is not installed or .pre-commit-config.yaml missing."

    res = run_precommit_hook("black")
    out = (res.out or "") + "\n" + (res.err or "")

    # Collect reformatted files from lines: 'reformatted path/to/file.py'
    reformatted: list[str] = []
    for ln in out.splitlines():
        s = ln.strip()
        if s.startswith("reformatted "):
            fn = s[len("reformatted ") :].strip()
            reformatted.append(relpath_str(fn))

    changed = len(reformatted)
    modified_hint = "Files were modified by this hook" in out

    if changed > 0 or modified_hint:
        title = f"**PASSED** - {total_files} source files checked; Auto-Fixes Applied = {changed or '≥1'}"
        lines = [title]
        if reformatted:
            lines.append("")
            lines.append("Auto-fixed files:")
            for fn in reformatted:
                lines.append(f"- {fn}")
        return "PASSED", "\n".join(lines)

    if res.rc == 0:
        title = f"**PASSED** - {total_files} source files checked; Auto-Fixes Applied = 0"
        return "PASSED", title

    # Some non-formatting failure happened; surface the text
    return "FAILED", f"**FAILED**\n\n{out.strip()}"


def mypy_check(total_files: int) -> tuple[str, str]:
    """
    Run mypy through pre-commit for parity; keep mypy's summary line verbatim when present.
    """
    if not have_precommit():
        return "SKIPPED", "SKIPPED: pre-commit is not installed or .pre-commit-config.yaml missing."

    res = run_precommit_hook("mypy")
    combined = (res.out or "") + "\n" + (res.err or "")

    # mypy diagnostics (with optional column)
    diag_re = re.compile(
        r"""^(?P<file>[^:\n]+):(?P<line>\d+)(?::(?P<col>\d+))?:\s*
            (?P<level>error|warning|note):\s*(?P<msg>.+)$""",
        re.IGNORECASE | re.VERBOSE,
    )
    success_re = re.compile(r"^Success:\s+no issues found in\s+(\d+)\s+source\s+files\s*$", re.IGNORECASE)
    found_re = re.compile(
        r"^Found\s+(\d+)\s+errors?\s+in\s+(\d+)\s+files?\s+\(checked\s+(\d+)\s+source\s+files\)\s*$",
        re.IGNORECASE,
    )

    per_file: dict[str, list[tuple[int, int | None, str]]] = {}
    mypy_summary_line: str | None = None
    status = "FAILED"

    for ln in combined.splitlines():
        s = ln.strip()
        m = diag_re.match(s)
        if m:
            if m.group("level").lower() == "error":
                fn = m.group("file")
                line = int(m.group("line"))
                col = m.group("col")
                col_num = int(col) if col is not None else None
                msg = m.group("msg").strip()
                per_file.setdefault(fn, []).append((line, col_num, msg))
            continue
        if success_re.match(s):
            mypy_summary_line = s
            status = "PASSED"
        elif found_re.match(s):
            mypy_summary_line = s
            status = "FAILED"

    if status == "PASSED":
        md = f"**PASSED**\n\n{mypy_summary_line or 'Success: no issues found'}"
        return "PASSED", md

    # FAILED — build file list + verbose sections
    lines = ["**FAILED**", ""]
    if mypy_summary_line:
        lines.append(mypy_summary_line)
        lines.append("")
    lines.append("**The Failed Scripts:**")
    for fn, issues in per_file.items():
        lines.append(f"- {relpath_str(fn)}: _{len(issues)} Errors_")
    lines.append("")

    items = list(per_file.items())
    for i, (fn, issues) in enumerate(items):
        if i:
            lines.append("\n---\n")
        short = Path(fn).name
        lines.append(f"### {short}")
        for line, col, msg in issues:
            if col is not None:
                lines.append(f"**{relpath_str(fn)}: Ln {line}, Col {col}**  ")
            else:
                lines.append(f"**{relpath_str(fn)}: Ln {line}**  ")
            lines.append(f"{msg}\n")

    return "FAILED", "\n".join(lines)


def have_tool(cmd: str) -> bool:
    return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def gather_quality_results() -> tuple[int, tuple[str, str], tuple[str, str], tuple[str, str]]:
    """
    Returns:
      total_py_files,
      (ruff_sum, ruff_md),
      (black_sum, black_md),
      (mypy_sum, mypy_md)
    """
    total_py_files = len(list_python_files())

    if have_precommit():
        ruff_sum, ruff_md = ruff_check(total_files=total_py_files)
        black_sum, black_md = black_check(total_files=total_py_files)
        mypy_sum, mypy_md = mypy_check(total_files=total_py_files)
    else:
        msg = "SKIPPED: pre-commit is not installed or .pre-commit-config.yaml missing."
        ruff_sum, ruff_md = ("SKIPPED", msg)
        black_sum, black_md = ("SKIPPED", msg)
        mypy_sum, mypy_md = ("SKIPPED", msg)

    return total_py_files, (ruff_sum, ruff_md), (black_sum, black_md), (mypy_sum, mypy_md)


def run_quality_check() -> None:
    # One temporary spinner line for the whole quality phase
    with spinner_line("Running Quality Checks..."):
        total_files, (ruff_sum, ruff_md), (black_sum, black_md), (mypy_sum, mypy_md) = gather_quality_results()

    print(f"\n{BOLD}=== Quality Checks ==={RESET}\n")

    # Build report
    date_str, time_str, report_path = make_report_path("quality")
    write_report_header_generic(
        path=report_path,
        report_type="Quality Check",
        date_str=date_str,
        time_str=time_str,
        repo_root=REPO_ROOT,
        extra_fields={"FILES CHECKED": str(total_files)},
    )

    write_quality_summary_compact_md(report_path, ruff_sum, black_sum, mypy_sum)
    append_section_md(report_path, "RUFF CHECKS", ruff_md)
    append_section_md(report_path, "BLACK CHECKS", black_md)
    append_section_md(report_path, "MYPY CHECKS", mypy_md)

    # Terminal summary exactly as requested
    print(summary_line("ruff", ruff_sum))
    print(summary_line("black", black_sum))
    print(summary_line("mypy", mypy_sum))

    link = osc8_link("Click Here", report_path)
    print("\n" + f"Quality Check Complete: {link} to View Quality Report.")
    try:
        input(f"\nPress {BOLD}ENTER{RESET} to return to main menu…")
    except (EOFError, KeyboardInterrupt):
        pass
    print("\n---\n")


# ------------------------------------------------------------------------------
# PYTESTS
# ------------------------------------------------------------------------------


_PYTEST_SUMMARY_RE = re.compile(r"=+ short test summary info =+\n(?P<body>.*?)(?=\n=+|\Z)", re.DOTALL)
_PYTEST_FAILURES_RE = re.compile(r"=+ FAILURES =+\n(?P<body>.*?)(?=\n=+|\Z)", re.DOTALL)
_PYTEST_NODE_LINE_RE = re.compile(
    r"^(?P<nodeid>[\w\.\-\/\\:]+::[^\s]+)\s+(?P<status>PASSED|FAILED|SKIPPED|XFAILED|XPASS|ERROR)\b",
    re.IGNORECASE,
)


def parse_pytest_summary_block(text: str) -> str | None:
    m = _PYTEST_SUMMARY_RE.search(text)
    if not m:
        return None
    body = strip_ansi(m.group("body")).strip()
    return body if body else None


def extract_pytest_failures_block(text: str) -> str | None:
    m = _PYTEST_FAILURES_RE.search(text)
    if not m:
        return None
    return strip_ansi(m.group("body")).strip()


def parse_pytest_node_lines(text: str) -> tuple[list[str], list[str], list[str]]:
    """
    Returns (passed, failed, skipped) as nodeid strings from -vv output lines.
    """
    passed: list[str] = []
    failed: list[str] = []
    skipped: list[str] = []
    for raw in text.splitlines():
        s = strip_ansi(raw).strip()
        m = _PYTEST_NODE_LINE_RE.match(s)
        if not m:
            continue
        nodeid = m.group("nodeid")
        status = m.group("status").upper()
        if status == "PASSED":
            passed.append(nodeid)
        elif status == "FAILED":
            failed.append(nodeid)
        elif status == "SKIPPED":
            skipped.append(nodeid)
    return passed, failed, skipped


def run_pytests() -> None:
    # Run pytest verbosely but capture *all* output; set APP_ENV=test
    env = os.environ.copy()
    env["APP_ENV"] = "test"
    cmd = [sys.executable or "python3", "-m", "pytest", "-vv", "-r", "a", "--maxfail=0"]

    res = run_with_spinner("Running Pytests...", cmd, env=env)

    print(f"\n{BOLD}=== Pytests ==={RESET}\n")
    out = (res.out or "") + "\n" + (res.err or "")
    clean = strip_ansi(out)

    # Parse summary
    summary = parse_pytest_summary_block(clean)
    # Parse node lines
    passed, failed, skipped = parse_pytest_node_lines(clean)
    tests_ran = len(passed) + len(failed) + len(skipped)
    passed_n, failed_n, skipped_n = len(passed), len(failed), len(skipped)

    # If no summary block (all passed), craft a simple one
    if summary is None:
        summary = f"{tests_ran} passed"

    # Build report
    date_str, time_str, report_path = make_report_path("pytest")
    write_report_header_generic(
        path=report_path,
        report_type="Pytest",
        date_str=date_str,
        time_str=time_str,
        repo_root=REPO_ROOT,
        extra_fields={"TESTS RAN": str(tests_ran)},
    )

    # SUMMARY
    append_section_md(report_path, "SUMMARY", build_pytest_counts_md(passed_n, failed_n, skipped_n))

    # Lists
    if passed:
        md = "\n".join(f"- {n}" for n in passed)
        append_section_md(report_path, "TESTS THAT PASSED", md)
    if failed:
        # Include verbose failures as a single fenced block (robust across pytest versions)
        failures_block = extract_pytest_failures_block(clean)
        if failures_block:
            verbose_md = "```\n" + failures_block + "\n```"
        else:
            # Fallback to listing nodeids if failure block isn’t present
            verbose_md = "\n".join(f"- {n}" for n in failed)
        # Put a brief bullet list first, then the verbose block
        list_md = "\n".join(f"- {n}" for n in failed)
        append_section_md(report_path, "TESTS THAT FAILED", list_md + "\n\n" + verbose_md)
    if skipped:
        md = "\n".join(f"- {n}" for n in skipped)
        append_section_md(report_path, "TESTS THAT SKIPPED", md)

    # Terminal summary
    print(summary_count_line("Passed", passed_n))
    print(summary_count_line("Failed", failed_n))
    print(summary_count_line("Skipped", skipped_n))

    link = osc8_link("Click Here", report_path)
    print("\n" + f"Pytest Complete: {link} to View Pytest Report.")
    try:
        input(f"\nPress {BOLD}ENTER{RESET} to return to main menu…")
    except (EOFError, KeyboardInterrupt):
        pass
    print("\n---\n")


# ------------------------------------------------------------------------------
# PRE-COMMIT
# ------------------------------------------------------------------------------


def run_pre_commit_suite() -> None:
    # 1) QUALITY (spinner around all hooks)
    with spinner_line("Running Quality Checks..."):
        total_files, (ruff_sum, ruff_md), (black_sum, black_md), (mypy_sum, mypy_md) = gather_quality_results()

    # 2) PYTESTS (spinner for pytest)
    env = os.environ.copy()
    env["APP_ENV"] = "test"
    cmd = [sys.executable or "python3", "-m", "pytest", "-vv", "-r", "a", "--maxfail=0"]
    res = run_with_spinner("Running Pytests...", cmd, env=env)

    print(f"\n{BOLD}=== Pre-Commit Full Suite ==={RESET}\n")
    clean = strip_ansi((res.out or "") + "\n" + (res.err or ""))

    summary = parse_pytest_summary_block(clean)
    passed, failed, skipped = parse_pytest_node_lines(clean)
    tests_ran = len(passed) + len(failed) + len(skipped)
    if summary is None:
        summary = f"{tests_ran} passed"

    passed_n, failed_n, skipped_n = len(passed), len(failed), len(skipped)
    quality_ok = ruff_sum == "PASSED" and black_sum == "PASSED" and mypy_sum == "PASSED"
    pytest_ok = failed_n == 0 and res.rc == 0

    # Build report
    date_str, time_str, report_path = make_report_path("precommit")
    write_report_header_generic(
        path=report_path,
        report_type="Pre-Commit (Full Suite)",
        date_str=date_str,
        time_str=time_str,
        repo_root=REPO_ROOT,
        extra_fields={"FILES CHECKED": f"{total_files}  ", "TESTS RAN": str(tests_ran)},
    )

    # SUMMARY
    sum_lines = [
        f"**QUALITY CHECKS:** {'SUCCESS' if quality_ok else 'FAILURE'}  ",
        f"**PYTESTS:** {'SUCCESS' if pytest_ok else 'FAILURE'}",
    ]
    append_section_md(report_path, "SUMMARY", "\n".join(sum_lines))

    # QUALITY DETAILS
    append_h1_md(report_path, "QUALITY CHECKS", build_quality_summary_compact(ruff_sum, black_sum, mypy_sum))
    append_section_md(report_path, "RUFF CHECKS", ruff_md)
    append_section_md(report_path, "BLACK CHECKS", black_md)
    append_section_md(report_path, "MYPY CHECKS", mypy_md)

    # PYTEST DETAILS
    append_h1_md(report_path, "PYTESTS", build_pytest_counts_md(passed_n, failed_n, skipped_n))
    if passed:
        md = "\n".join(f"- {n}" for n in passed)
        append_section_md(report_path, "TESTS THAT PASSED", md)
    if failed:
        failures_block = extract_pytest_failures_block(clean)
        if failures_block:
            verbose_md = "```\n" + failures_block + "\n```"
        else:
            verbose_md = "\n".join(f"- {n}" for n in failed)
        list_md = "\n".join(f"- {n}" for n in failed)
        append_section_md(report_path, "TESTS THAT FAILED", list_md + "\n\n" + verbose_md)
    if skipped:
        md = "\n".join(f"- {n}" for n in skipped)
        append_section_md(report_path, "TESTS THAT SKIPPED", md)

    # Terminal summary
    print(summary_line("Quality Checks", "SUCCESS" if quality_ok else "FAILURE"))
    print(summary_line("Pytests", "SUCCESS" if pytest_ok else "FAILURE"))

    link = osc8_link("Click Here", report_path)
    print("\n" + f"Pre-Commit Complete: {link} to View Pre-Commit Report.")
    try:
        input(f"\nPress {BOLD}ENTER{RESET} to return to main menu…")
    except (EOFError, KeyboardInterrupt):
        pass
    print("\n---\n")


# ------------------------------------------------------------------------------
# Main Menu
# ------------------------------------------------------------------------------


def main() -> int:
    print(f"{BOLD}=== Quality / Tests / Pre-commit Wizard ==={RESET}")
    while True:
        print("\nWhat do you want to run?")
        print("\t1 = Just the Quality Checks")
        print("\t2 = Just the Pytests")
        print("\t3 = The Full Pre-Commit Suite")
        print("\tQ = Quit")
        ans = read_choice("Choice [1/2/3/Q]: ", valid={"1", "2", "3", "q"}, allow_blank=True)
        if ans is None:
            return 0
        if ans == "1":
            run_quality_check()
        elif ans == "2":
            run_pytests()
        elif ans == "3":
            run_pre_commit_suite()
        elif ans in {"q", ""}:
            return 0
        else:
            print("Please enter 1, 2, 3, or Q.")


if __name__ == "__main__":
    raise SystemExit(main())
