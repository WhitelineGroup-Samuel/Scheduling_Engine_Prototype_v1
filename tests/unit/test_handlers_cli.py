"""Unit tests for CLI error handling utilities and logging behaviour."""

from __future__ import annotations

import functools
import json
import logging
import sys

import pytest

from app.config.logging_config import configure_logging
from app.config.settings import Settings
from app.errors.codes import ErrorCode
from app.errors.exceptions import DBConnectionError, ValidationError
from app.errors.handlers import handle_cli_error, level_for, wrap_cli_main

setattr(Settings, "ENV_PREFIX", "")

pytestmark = pytest.mark.unit


def _make_settings(*, log_json: bool) -> Settings:
    """Return a settings instance populated with deterministic values for tests."""

    return Settings.model_construct(
        APP_NAME="scheduling-engine",
        APP_VERSION="0.1.0",
        APP_ENV="test",
        LOG_LEVEL="INFO",
        LOG_JSON=log_json,
        TIMEZONE="Australia/Melbourne",
        DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/scheduling_test",
    )


@pytest.fixture
def settings() -> Settings:
    """Return a copy of the application settings for test isolation."""

    return _make_settings(log_json=False)


@pytest.fixture
def configured_logger(settings: Settings) -> logging.Logger:
    """Configure logging for tests and return a dedicated logger instance."""

    configure_logging(settings, force_json=False, force_level="INFO")
    return logging.getLogger("app.tests.handlers")


def test_handle_cli_error_validation_returns_64_and_no_exc_info(
    configured_logger: logging.Logger, caplog: pytest.LogCaptureFixture
) -> None:
    """Validation errors should log once at ERROR level without tracebacks."""

    caplog.clear()
    caplog.set_level(logging.ERROR, logger=configured_logger.name)
    err = ValidationError("bad input", context={"field": "name"})

    handler = functools.partial(handle_cli_error, logger=configured_logger)
    exit_code = handler(err)

    assert exit_code == ErrorCode.VALIDATION_ERROR.exit_code
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == level_for(ErrorCode.VALIDATION_ERROR.severity)
    assert not record.exc_info
    assert record.code == ErrorCode.VALIDATION_ERROR.code
    assert record.exit_code == ErrorCode.VALIDATION_ERROR.exit_code
    assert getattr(record, "trace_id")


def test_handle_cli_error_db_connection_critical_has_exc_info(
    configured_logger: logging.Logger, caplog: pytest.LogCaptureFixture
) -> None:
    """Critical database errors should include traceback information."""

    caplog.clear()
    caplog.set_level(logging.CRITICAL, logger=configured_logger.name)
    err = DBConnectionError(
        "cannot connect",
        context={"host": "localhost", "port": 5432},
    )

    exit_code = handle_cli_error(err, configured_logger)

    assert exit_code == ErrorCode.DB_CONNECTION_ERROR.exit_code
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == level_for(ErrorCode.DB_CONNECTION_ERROR.severity)
    assert record.exc_info is not None
    assert record.code == ErrorCode.DB_CONNECTION_ERROR.code
    assert record.exit_code == ErrorCode.DB_CONNECTION_ERROR.exit_code


def test_wrap_cli_main_converts_exception_to_system_exit(
    settings: Settings, caplog: pytest.LogCaptureFixture
) -> None:
    """Unhandled exceptions are converted to :class:`SystemExit` with logging."""

    configure_logging(settings, force_json=False, force_level="INFO")
    caplog.clear()

    @wrap_cli_main
    def boom() -> None:
        """Raise a generic exception to trigger CLI error handling."""

        raise Exception("boom")

    assert boom.__name__ == "boom"

    capture_handler: list[logging.LogRecord] = []

    class _ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            capture_handler.append(record)

    handler = _ListHandler(level=logging.CRITICAL)
    logger = logging.getLogger(boom.__module__)
    logger.addHandler(handler)
    try:
        with pytest.raises(SystemExit) as excinfo:
            boom()
    finally:
        logger.removeHandler(handler)

    assert excinfo.value.code == ErrorCode.UNKNOWN_ERROR.exit_code
    assert len(capture_handler) == 1
    record = capture_handler[0]
    assert record.code == ErrorCode.UNKNOWN_ERROR.code
    assert record.levelno == level_for(ErrorCode.UNKNOWN_ERROR.severity)
    assert record.exc_info is not None


def test_json_mode_emits_parseable_json(capsys: pytest.CaptureFixture[str]) -> None:
    """JSON logging mode should emit structured payloads containing expected keys."""

    json_settings = _make_settings(log_json=True)
    configure_logging(json_settings, force_json=True, force_level="INFO")
    logger = logging.getLogger("app.tests.handlers.json")
    logger.error(
        "json emission test",
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
        "code",
        "exit_code",
        "env",
        "app",
        "version",
    }
    assert expected_keys.issubset(payload)
