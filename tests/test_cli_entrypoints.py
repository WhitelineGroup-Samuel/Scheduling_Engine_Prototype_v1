from __future__ import annotations

import json
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, NoReturn

import pytest
from typer.testing import CliRunner

from app.cli.main import app
from app.errors.codes import ErrorCode

runner = CliRunner()


# ----- Small helpers ---------------------------------------------------------


def _fake_settings() -> Any:
    # Minimal set of attributes accessed by CLI commands
    return SimpleNamespace(
        APP_NAME="Whiteline",
        APP_VERSION="0.1.0",
        APP_ENV="test",
        LOG_LEVEL="INFO",
        LOG_JSON=False,
        TIMEZONE="UTC",
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="whiteline_test",
        # commands read this property in multiple places
        effective_database_url="postgresql+psycopg://user:pass@localhost:5432/whiteline_test",
    )


class _DummyEngine:
    def dispose(self) -> None:
        pass


class _DummySession:
    """Minimal session used by seed-data dry-run planner."""

    def execute(self, stmt: Any) -> Any:  # noqa: ANN401
        class _Scalars:
            def first(self) -> Any | None:  # noqa: ANN401
                # No existing organisation → planner proposes 1 insert
                return None

        class _Result:
            def scalars(self) -> _Scalars:
                return _Scalars()

        return _Result()

    def close(self) -> None:
        pass


def _dummy_session_factory() -> Callable[[], _DummySession]:
    return lambda: _DummySession()


def _no_log(*args: object, **kwargs: object) -> None:
    """Typed no-op logger configurator."""
    return None


def _mk_engine(*args: object, **kwargs: object) -> _DummyEngine:
    """Typed factory for a dummy engine."""
    return _DummyEngine()


def _ping_check_env(*args: object, **kwargs: object) -> dict[str, Any]:
    return {
        "ok": True,
        "database": "whiteline_test",
        "server_version": "16.0",
        "duration_ms": 1.23,
    }


def _ping_init_db(*args: object, **kwargs: object) -> dict[str, Any]:
    return {"ok": True, "duration_ms": 1.0}


def _heads_current(*args: object, **kwargs: object) -> list[str]:
    return ["abcdef1"]


def _heads_script(*args: object, **kwargs: object) -> list[str]:
    return ["abcdef1"]


def _factory_session(*args: object, **kwargs: object) -> Callable[[], _DummySession]:
    return _dummy_session_factory()


def _ping_diag(*args: object, **kwargs: object) -> dict[str, Any]:
    return {
        "ok": True,
        "database": "whiteline_test",
        "server_version": "16.0",
        "duration_ms": 2.34,
    }


def _alembic_heads(*args: object, **kwargs: object) -> list[str]:
    return ["deadbee"]


def _boom(*args: object, **kwargs: object) -> NoReturn:
    """Typed function that always raises (to test wrap_cli_main error mapping)."""
    raise ValueError("bad input")


# ----- Tests -----------------------------------------------------------------


def test_cli_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Commands registered in app/cli/main.py
    for cmd in ("check-env", "init-db", "seed-data", "lint-sql", "diag"):
        assert cmd in result.stdout


def test_check_env_json_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch internals used by app/cli/check_env.py
    import app.cli.check_env as mod

    monkeypatch.setattr(mod, "get_settings", _fake_settings)
    monkeypatch.setattr(mod, "configure_logging", _no_log)
    monkeypatch.setattr(mod, "create_engine_from_settings", _mk_engine)
    monkeypatch.setattr(mod, "ping", _ping_check_env)

    result = runner.invoke(app, ["check-env", "--json"])
    assert result.exit_code == 0
    # Ensure valid JSON payload with minimal keys
    payload = json.loads(result.stdout.strip())
    assert payload["env"] == "test"
    assert payload["db"]["name"] == "whiteline_test"
    assert "ping" in payload and isinstance(payload["ping"], dict)


def test_init_db_dry_run_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch internals used by app/cli/init_db.py
    import app.cli.init_db as mod

    monkeypatch.setattr(mod, "get_settings", _fake_settings)
    monkeypatch.setattr(mod, "configure_logging", _no_log)
    monkeypatch.setattr(mod, "create_engine_from_settings", _mk_engine)
    monkeypatch.setattr(mod, "ping", _ping_init_db)
    monkeypatch.setattr(mod, "_current_heads", _heads_current)
    monkeypatch.setattr(mod, "_script_heads", _heads_script)

    result = runner.invoke(app, ["init-db", "--dry-run"])
    assert result.exit_code == 0
    assert "Current heads:" in result.stdout


def test_seed_data_dry_run_inserts_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Patch internals used by app/cli/seed_data.py
    import app.cli.seed_data as mod

    monkeypatch.setattr(mod, "get_settings", _fake_settings)
    monkeypatch.setattr(mod, "configure_logging", _no_log)
    monkeypatch.setattr(mod, "create_engine_from_settings", _mk_engine)
    monkeypatch.setattr(mod, "create_session_factory", _factory_session)

    result = runner.invoke(app, ["seed-data", "--org-name", "Demo Org"])
    assert result.exit_code == 0
    # Human summary should be printed in dry-run mode
    assert "Seed summary:" in result.stdout
    assert "inserted=1" in result.stdout


def test_lint_sql_exits_zero_even_without_sqlfluff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # If sqlfluff isn't installed, command prints info and exits 0.
    # We don't force an ImportError here; either way the contract is exit 0.
    import app.cli.lint_sql as mod

    monkeypatch.setattr(mod, "get_settings", _fake_settings)
    monkeypatch.setattr(mod, "configure_logging", _no_log)

    result = runner.invoke(app, ["lint-sql"])
    assert result.exit_code == 0


def test_diag_json_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch internals used by app/cli/diag.py
    import app.cli.diag as mod

    monkeypatch.setattr(mod, "get_settings", _fake_settings)
    monkeypatch.setattr(mod, "configure_logging", _no_log)
    monkeypatch.setattr(mod, "create_engine_from_settings", _mk_engine)
    monkeypatch.setattr(mod, "ping", _ping_diag)
    monkeypatch.setattr(mod, "_load_alembic_heads", _alembic_heads)

    result = runner.invoke(app, ["diag", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip())
    assert payload["db"]["ok"] is True
    assert payload["alembic"]["heads"] == ["deadbee"]


def test_wrap_cli_main_maps_value_error_to_validation_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Force the seed-data dry-run planner to raise ValueError.
    The decorator should map it to ValidationError (ErrorCode.VALIDATION_ERROR).
    """
    import app.cli.seed_data as mod

    monkeypatch.setattr(mod, "get_settings", _fake_settings)
    monkeypatch.setattr(mod, "configure_logging", _no_log)
    monkeypatch.setattr(mod, "create_engine_from_settings", _mk_engine)
    monkeypatch.setattr(mod, "create_session_factory", _factory_session)
    monkeypatch.setattr(mod, "_plan_seed", _boom)

    result = runner.invoke(app, ["seed-data", "--org-name", "X"])
    assert result.exit_code == ErrorCode.VALIDATION_ERROR.exit_code
