"""
===============================================================================
File: app/config/logging_config.py
Purpose
-------
Central logging configuration applied once at process start (run.py / CLI).
Supports human and JSON formats, injects trace/env/app/version details, and
redacts secrets.
===============================================================================
"""

from __future__ import annotations

import json
import logging
import logging.config
import re
from datetime import datetime, timezone
from types import ModuleType
from typing import TYPE_CHECKING, Any
from uuid import uuid4

logging_tools_module: ModuleType | None
try:  # pragma: no cover - optional dependency fallback
    from app.utils import logging_tools as logging_tools_module
except ImportError:  # pragma: no cover - optional dependency
    logging_tools_module = None

if TYPE_CHECKING:  # pragma: no cover
    from .settings import Settings

_SENSITIVE_FIELD_NAMES: set[str] = {
    "db_password",
    "db_pass",
    "password",
    "secret",
    "token",
    "DATABASE_URL",
    "database_url",
}
_CREDENTIAL_RE = re.compile(r"://([^:/?#]+):([^@]+)@")
_SECRET_RE = re.compile(r"(?i)(password|secret|token)=([^&\s]+)")

_CONFIGURED: bool = False


def _ensure_trace_id() -> str:
    """Ensure a trace id is available, delegating to logging tools when possible."""

    if logging_tools_module is not None:
        ensure = getattr(logging_tools_module, "ensure_trace_id", None)
        if callable(ensure):
            trace = ensure()
            if trace:
                return str(trace)
        getter = getattr(logging_tools_module, "get_trace_id", None)
        if callable(getter):
            trace = getter()
            if trace:
                return str(trace)
    return uuid4().hex[:16]


def _redact_text(value: str) -> str:
    """Redact credentials and obvious secrets from a string."""

    sanitized = _CREDENTIAL_RE.sub("://***:***@", value)
    sanitized = _SECRET_RE.sub(lambda match: f"{match.group(1)}=***", sanitized)
    return sanitized


class StaticFieldsFilter(logging.Filter):
    """Inject static fields derived from application settings."""

    def __init__(self, settings: "Settings") -> None:
        super().__init__()
        self._env = settings.APP_ENV
        self._app = settings.APP_NAME or "scheduling-engine"
        self._version = settings.APP_VERSION or "0.1.0"

    def filter(self, record: logging.LogRecord) -> bool:
        record.env = getattr(record, "env", self._env)
        record.app = getattr(record, "app", self._app)
        record.version = getattr(record, "version", self._version)
        return True


class TraceIdFilter(logging.Filter):
    """Ensure each record includes a trace identifier."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = getattr(record, "trace_id", None) or _ensure_trace_id()
        return True


class RedactionFilter(logging.Filter):
    """Redact sensitive material from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.redacted_message = _redact_text(message)

        for field_name in _SENSITIVE_FIELD_NAMES:
            if hasattr(record, field_name):
                value = getattr(record, field_name)
                if isinstance(value, str):
                    setattr(record, field_name, _redact_text(value))
                else:
                    setattr(record, field_name, "***")
        return True


class HumanFormatter(logging.Formatter):
    """Human-readable formatter suitable for development usage."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )

    def format(self, record: logging.LogRecord) -> str:
        record.message = getattr(record, "redacted_message", record.getMessage())
        if not getattr(record, "trace_id", None):
            record.trace_id = _ensure_trace_id()
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """JSON formatter emitting structured single-line payloads."""

    def format(self, record: logging.LogRecord) -> str:
        message = getattr(record, "redacted_message", record.getMessage())
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        if timestamp.endswith("+00:00"):
            timestamp = timestamp.replace("+00:00", "Z")

        payload: dict[str, Any] = {
            "ts": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "trace_id": getattr(record, "trace_id", _ensure_trace_id()),
            "msg": message,
            "env": getattr(record, "env", ""),
            "app": getattr(record, "app", ""),
            "version": getattr(record, "version", ""),
        }

        for key, value in record.__dict__.items():
            if key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "redacted_message",
            }:
                continue
            if key.startswith("_"):
                continue
            if key not in payload:
                payload[key] = value

        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(
    settings: "Settings",
    *,
    force_json: bool | None = None,
    force_level: str | None = None,
) -> logging.Logger:
    """Configure application logging and return the app logger."""

    use_json = settings.LOG_JSON if force_json is None else force_json
    level_name = (force_level or settings.LOG_LEVEL).upper()

    formatter_name = "json" if use_json else "human"

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "static_fields": {
                "()": f"{__name__}.StaticFieldsFilter",
                "settings": settings,
            },
            "trace_id": {"()": f"{__name__}.TraceIdFilter"},
            "redaction": {"()": f"{__name__}.RedactionFilter"},
        },
        "formatters": {
            "human": {"()": f"{__name__}.HumanFormatter"},
            "json": {"()": f"{__name__}.JsonFormatter"},
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": level_name,
                "stream": "ext://sys.stdout",
                "filters": ["static_fields", "trace_id", "redaction"],
                "formatter": formatter_name,
            }
        },
        "loggers": {
            "sqlalchemy.engine": {
                "handlers": ["stdout"],
                "level": "WARNING",
                "propagate": False,
            },
            "alembic": {
                "handlers": ["stdout"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "level": level_name,
            "handlers": ["stdout"],
        },
    }

    logging.config.dictConfig(config)

    app_logger = logging.getLogger("app")
    app_logger.setLevel(level_name)

    global _CONFIGURED
    _CONFIGURED = True

    return app_logger


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, ensuring configuration is applied once."""

    global _CONFIGURED
    if not _CONFIGURED:
        from . import get_settings

        configure_logging(get_settings())
    return logging.getLogger(name)


__all__ = [
    "configure_logging",
    "get_logger",
    "StaticFieldsFilter",
    "TraceIdFilter",
    "RedactionFilter",
]
