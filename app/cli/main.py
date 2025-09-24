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

Integration & dependencies
--------------------------
- Typer (Click under the hood)
- app.config.settings.get_settings
- app.config.logging_config.configure_logging
- app.utils.logging_tools.{new_trace_id, with_trace_id}
- app.errors.handlers.{wrap_cli_main}

Help text & examples
--------------------
The CLI --help and each command --help should include the example block from Step 15.8.

Testing hooks
-------------
- Keep top-level side effects minimal so tests can import without running commands.
- The Typer app object should be named `app` and importable as `from app.cli.main import app`.
===============================================================================
"""
