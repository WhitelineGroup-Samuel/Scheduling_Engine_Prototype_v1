"""
===============================================================================
File: app/cli/main.py
Purpose
-------
Define the Typer application, register subcommands, and unify cross-cutting
concerns: settings loading, logging, trace id creation, and error handling.

Responsibilities
----------------
1) Create the Typer app with contextual help, version, and epilog examples.
2) Provide global options:
   - --verbose/-v : bump log level to DEBUG for the process lifetime.
   - (optional) --json : default JSON output mode for commands that support it.
   - The `--json` global flag sets a process-level default that subcommands can read,
     e.g., via a context object attached to Typer:
       app = Typer(context_settings={"obj": {"default_json": bool}})
   - Subcommands should read `ctx.obj.get("default_json")` if `--json` not passed per-command.
3) Register subcommands with kebab-case names:
   - check-env → app.cli.check_env
   - init-db   → app.cli.init_db
   - seed-data → app.cli.seed_data
   - lint-sql  → app.cli.lint_sql
   - diag      → app.cli.diag
4) Ensure each command function:
   - Loads settings (get_settings()) once.
   - Calls configure_logging(settings) exactly once.
   - Enters a new trace context (with_trace_id(new_trace_id())).
   - Is wrapped with @wrap_cli_main to map exceptions → one log line + exit code.
   - The `--json` global flag sets a process-level default that subcommands can read,
     e.g., via a context object attached to Typer:
       app = Typer(context_settings={"obj": {"default_json": bool}})
   - Subcommands should read `ctx.obj.get("default_json")` if `--json` not passed per-command.
   - Ensure `configure_logging(settings)` is called exactly once per command invocation.
     If logging is already configured, replace handlers to avoid duplicates (idempotent config).
   - Always annotate the command functions with `@wrap_cli_main` after logging and trace context
     are established inside the function body.

Integration & dependencies
--------------------------
- Typer (Click under the hood)
- app.config.settings.get_settings
- app.config.logging_config.configure_logging
- app.utils.logging_tools.{new_trace_id, with_trace_id}
- app.errors.handlers.{wrap_cli_main}
- Ensure `configure_logging(settings)` is called exactly once per command invocation.
  If logging is already configured, replace handlers to avoid duplicates (idempotent config).
- Always annotate the command functions with `@wrap_cli_main` after logging and trace context
  are established inside the function body.

Help text & examples
--------------------
- The CLI --help and each command --help should include the example block from Step 15.8.
- Include an epilog with examples showing each subcommand invocation exactly as listed
  in this prompt. Use kebab-case command names.

Testing hooks
-------------
- Keep top-level side effects minimal so tests can import without running commands.
- The Typer app object should be named `app` and importable as `from app.cli.main import app`.

Exports (explicit)
------------------
- The Typer application must be named `app`.
- Define `__all__ = ["app"]`.
===============================================================================
"""

from __future__ import annotations

from importlib import metadata

import typer

from app.cli.check_env import check_env_command
from app.cli.diag import diag_command
from app.cli.init_db import init_db_command
from app.cli.lint_sql import lint_sql_command
from app.cli.seed_data import seed_data_command


def _resolve_version() -> str:
    """Return the installed package version or fall back to the default."""

    try:
        return metadata.version("scheduling-engine")
    except metadata.PackageNotFoundError:
        return "0.1.0"
    except Exception:
        return "0.1.0"


_EXAMPLE_EPILOG = """Examples:\n  manage.py check-env\n  manage.py init-db\n  manage.py seed-data\n  manage.py lint-sql\n  manage.py diag"""

app = typer.Typer(
    name="Whiteline SportsHub CLI",
    help=(
        "Whiteline SportsHub scheduling engine management interface. "
        "Use the subcommands to validate environments, run migrations, seed "
        "data, lint SQL, and inspect diagnostics."
    ),
    no_args_is_help=True,
    add_completion=False,
    epilog=_EXAMPLE_EPILOG,
    context_settings={"obj": {}},
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable DEBUG logging for the invoked command.",
        is_flag=True,
    ),
    default_json: bool = typer.Option(
        False,
        "--json",
        help="Prefer JSON output when supported by subcommands.",
        is_flag=True,
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the CLI version and exit.",
        is_flag=True,
    ),
) -> None:
    """Store global flags for downstream commands and optionally print version."""

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["verbose"] = bool(verbose)
    ctx.obj["default_json"] = bool(default_json)

    if version:
        typer.echo(_resolve_version())
        raise typer.Exit()


app.command(
    "check-env",
    help="Validate configuration, logging, and database connectivity.",
)(check_env_command)

app.command(
    "init-db",
    help="Apply Alembic migrations to reach the requested revision.",
)(init_db_command)

app.command(
    "seed-data",
    help="Seed deterministic development data (dry-run by default).",
)(seed_data_command)

app.command(
    "lint-sql",
    help="Lint SQL files using sqlfluff when available.",
)(lint_sql_command)

app.command(
    "diag",
    help="Emit diagnostic metadata including environment and DB status.",
)(diag_command)


__all__ = ["app"]
