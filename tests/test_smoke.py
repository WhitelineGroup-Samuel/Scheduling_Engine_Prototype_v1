"""Smoke tests verifying configuration, logging, and database readiness."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.sql.schema import MetaData

from app.config.logging_config import configure_logging
from app.config.settings import Settings, get_settings
from app.db.alembic_env import target_metadata
from app.db.engine import create_engine_from_settings
from app.db.healthcheck import ping
from app.errors.codes import ErrorCode

pytestmark = pytest.mark.smoke


def test_settings_loads_and_validates() -> None:
    """Settings should load from the environment with expected defaults."""

    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.APP_ENV == "test"
    assert settings.TIMEZONE == "Australia/Melbourne"
    assert settings.LOG_LEVEL.upper() == "INFO"
    assert isinstance(settings.LOG_JSON, bool)

    database_url = settings.effective_database_url
    assert database_url, "effective_database_url should not be empty"
    if settings.DATABASE_URL:
        assert database_url == settings.DATABASE_URL
    else:
        assert settings.DB_NAME == "scheduling_test"


def test_timezone_available() -> None:
    """The configured timezone must resolve via :mod:`zoneinfo`."""

    settings = get_settings()
    tz = ZoneInfo(settings.TIMEZONE)
    aware_now = datetime.now(tz)
    assert aware_now.tzinfo is not None
    assert aware_now.tzinfo.utcoffset(aware_now) is not None


def test_logging_config_builds_and_emits(caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]) -> None:
    """Logging configuration should emit human and JSON formats with trace IDs."""

    base_settings = get_settings()
    human_settings = base_settings.model_copy(update={"LOG_JSON": False}, deep=True)
    configure_logging(human_settings, force_json=False, force_level="INFO")
    # Human-mode log should go to stdout/stderr; our config may reset handlers,
    # so validate via capsys rather than caplog (which relies on pytest’s handler).
    human_logger = logging.getLogger("app.smoke.logging")
    human_logger.propagate = True
    human_logger.error(
        "human-mode log",
        extra={
            "code": ErrorCode.UNKNOWN_ERROR.code,
            "exit_code": ErrorCode.UNKNOWN_ERROR.exit_code,
            "severity": ErrorCode.UNKNOWN_ERROR.severity,
        },
    )
    sys.stdout.flush()
    captured_human = capsys.readouterr()
    human_lines = [ln for ln in (captured_human.out + captured_human.err).splitlines() if ln.strip()]
    assert any("human-mode log" in ln for ln in human_lines), "Expected human log text"
    # our human formatter includes a trace marker like 'trace=<id>'; assert it’s present
    assert any("trace=" in ln for ln in human_lines), "Expected trace id in human log line"

    json_settings = base_settings.model_copy(update={"LOG_JSON": True}, deep=True)
    configure_logging(json_settings, force_json=True, force_level="INFO")
    json_logger = logging.getLogger("app.smoke.logging.json")
    json_logger.propagate = True
    json_logger.error(
        "json-mode log",
        extra={
            "code": ErrorCode.UNKNOWN_ERROR.code,
            "exit_code": ErrorCode.UNKNOWN_ERROR.exit_code,
            "severity": ErrorCode.UNKNOWN_ERROR.severity,
        },
    )
    sys.stdout.flush()
    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert lines, "Expected JSON log output"
    payload = json.loads(lines[-1])
    expected_keys = {
        "ts",
        "level",
        "logger",
        "trace_id",
        "msg",
        "env",
        "app",
        "version",
        "code",
        "exit_code",
    }
    assert expected_keys.issubset(payload)


def test_db_healthcheck_readonly() -> None:
    """The database healthcheck should succeed using read-only queries."""

    settings = get_settings()
    engine = create_engine_from_settings(settings, role="test")
    try:
        result = ping(engine)
    finally:
        engine.dispose()

    assert result["ok"] is True
    assert result["database"] == "scheduling_test"
    assert result["server_version"]
    assert result["duration_ms"] > 0


def test_alembic_wiring_discoverable() -> None:
    """Alembic metadata should be exposed for migration tooling."""

    assert isinstance(target_metadata, MetaData)


def test_cli_help_succeeds() -> None:
    """Invoking the CLI help should succeed and list core commands."""

    repo_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, "manage.py", "--help"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "check-env" in result.stdout
